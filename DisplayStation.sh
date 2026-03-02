#!/bin/bash

#all code begins here
echo "opening start.sh..."
echo " "

set -euo pipefail

#declare essential variables ############################################################################################################################################################################

	rtsp=() #declare the rtsp array
	rtspSub=() #declare the substream array
	rtspName=() #declare an array for rtsp reference names
	rtspIndex=() #declare an array for the config file to refer to indicies in the other arrays
	declare -i rtspIndexLength #store the length of the 
	
	declare -i displayWidth
	declare -i displayHeight
	declare -i layoutType
	declare -i minLayoutType=1 #if layoutType is less than this, fails initialization
	declare -i maxLayoutType=11 #if layoutType is greater than this, fails initialization
	declare runtimeBeforeLoop
	declare -i loopRuntimeForever #1 for true. 0 for false.
	
	declare passedInitialization=1 #this variable is set to 0 if a critical initialization error is found
	
	declare layoutFile #this is the name of the text file that defines the screen layout
	
#END declare essential variables ########################################################################################################################################################################


#update the RTSP files in case IP settings have changed. 
########################################################################################################################################
	bash scripts/discoverCameras.sh onvifScan.txt
	echo " "
	bash scripts/update_rtsp_from_onvif.sh RTSP1.txt onvifScan.txt
	echo " "
	echo " "
#END update the RTSP files in case IP settings have changed. 
########################################################################################################################################

#Popup error handler ###################################################################################################################
	ShowErrorAndExit () {
	    yad --error \
		--center \
		--title="DisplayStation Error" \
		--text="$1" \
		--button=OK:0

	    echo "ERROR: $1"
	    exit 1
	}
#END Popup error handler ###############################################################################################################

#read the RTSP.txt file and load it into the rtsp array variable ########################################################################################################################################
	echo "Loading RTSP streams from RTSP1.txt into rtsp[] arrays:"
	echo " "

	block=()

	while IFS= read -r line || [[ -n "$line" ]]; do
	    block+=("$line")

	    if (( ${#block[@]} == 8 )); then
		# Extract fields
		name="${block[1]}"
		ip="${block[2]}"
		user="${block[4]}"
		pass="${block[5]}"
		hdPath="${block[6]}"
		subPath="${block[7]}"

		# Construct RTSP URLs like old RTSP.txt
		hdURL="rtsp://${user}:${pass}@${ip}${hdPath}"
		subURL="rtsp://${user}:${pass}@${ip}${subPath}"

		# Add to arrays
		rtspName+=("$name")
		rtsp+=("$hdURL")
		rtspSub+=("$subURL")

		# Reset block
		block=()
	    fi
	done < RTSP1.txt

	rtspIndexLength=${#rtsp[@]}

	# Print for verification
	for ((i=0; i<$rtspIndexLength; i++)); do
	    echo "${rtspName[$i]}"
	    echo "${rtsp[$i]}"
	    echo "${rtspSub[$i]}"
	done
	echo " "
	
	# Fail if RTSP1.txt is empty
	if [ ! -s "RTSP1.txt" ] || [ "$rtspIndexLength" -eq 0 ]; then
	    ShowErrorAndExit "RTSP1.txt is empty.\n\nNo cameras are configured."
	fi
#END read the RTSP.txt file and load it into the rtsp array variable ####################################################################################################################################


############################################################################################################################
# Load settings from SETTINGS.txt
############################################################################################################################

	echo "Loading configuration from SETTINGS.txt..."
	echo " "

	SETTINGS_FILE="SETTINGS.txt"

	if [ -f "$SETTINGS_FILE" ]; then
		source "$SETTINGS_FILE"
	else
		echo "ERROR: SETTINGS.txt not found."
		exit 1
	fi

	# Assign program variables
	
	layoutFile="customLayouts/$LAYOUT_FILE"
	# Fail if no layout selected
	if [ "$LAYOUT_FILE" = "null" ] || [ -z "$LAYOUT_FILE" ]; then
	    ShowErrorAndExit "No layout file is selected.\n\nPlease select a layout before starting DisplayStation."
	fi
	# Fail if layout file does not exist
	if [ ! -f "$layoutFile" ]; then
	    ShowErrorAndExit "Selected layout file does not exist:\n\n$layoutFile\n\nPlease select a valid layout."
	fi

	displayWidth=$DISPLAY_WIDTH
	displayHeight=$DISPLAY_HEIGHT
	runtimeBeforeLoop="$REBOOT_TIMER"
	loopRuntimeForever="$RUN_INDEFINITE"
	restartTime="$RESTART_TIME"

	# Output loaded values
	echo "layoutFile = $layoutFile"
	echo "Display Width = $displayWidth"
	echo "Display Height = $displayHeight"
	echo "Runtime before screen reboot = $runtimeBeforeLoop"

	if [ "$loopRuntimeForever" -eq 1 ]; then
		echo "Program set to loop indefinitely"
	else
		echo "Program in test mode. Main runtime will loop 5 times then cease."
	fi

	echo "Daily restart time = $restartTime"
	echo " "

############################################################################################################################
# END Load settings from SETTINGS.txt
############################################################################################################################

#read the layout file and load preconfigured settings into the program ################################################################################################################################
	echo "loading the following values from "$layoutFile" into the rtsp[] array"
	echo " "
	
	declare -i lineNumber=1
	while IFS= read -r line 
		do
			#Set the layoutType
			if [ $lineNumber -eq 1 ]
			then
				layoutType=$line
				echo "Layout Type = "$layoutType
				
				#if layoutType is outside of accepted range, set intialization to failed
				if [ $layoutType -gt $maxLayoutType ] || [ $layoutType -lt $minLayoutType ]
				then
					passedInitialization=0
					echo "ERROR: layoutFile "$layoutFile
					echo "layoutType outside of acceptable range."
					echo " "
				fi
				
			fi
			
			if [ $lineNumber -gt 1 ]
			#if we are on line 2 or higher
			then
				#check if the ID set in the config is outside of the range of the rtsp array
				if [ $((line)) -ge $rtspIndexLength ]
				then
					echo "ERROR: RTSP1.txt on line "$lineNumber
					echo "Please check your RTSP index numbers in the RTSP1.txt file."
					passedInitialization=0
				else
					#then add each line to the array
					rtspIndex+=("$line")
					echo  ${rtspName[${rtspIndex[$lineNumber-2]}]}", ID Number:"${rtspIndex[$lineNumber-2]} #arrays start at 0 so in order to display the first instance in a loop, we must subtract 2
				fi
			fi
			((lineNumber++))
		done < "$layoutFile"
#ENDread the layout file and load preconfigured settings into the program ################################################################################################################################


# Initialize the display resolution
####################################################################################################################################
current_res=$(xdpyinfo 2>/dev/null | awk '/dimensions/ {print $2}')

# List of common 16:9 resolutions
valid_16_9=("1920x1080" "1366x768" "1600x900" "1280x720" "2560x1440" "3840x2160" "1024x576")

if [ -n "$current_res" ]; then

    echo "Detected resolution: $current_res"

    # Check if detected resolution is in the list of valid 16:9 resolutions
    is_valid=false
    for res in "${valid_16_9[@]}"; do
        if [ "$current_res" == "$res" ]; then
            is_valid=true
            break
        fi
    done

    if [ "$is_valid" = true ]; then
        echo "Valid 16:9 resolution detected. Updating system."

        displayWidth=$(echo "$current_res" | cut -d 'x' -f1)
        displayHeight=$(echo "$current_res" | cut -d 'x' -f2)

        # Update SETTINGS.txt
        sed -i "s/^DISPLAY_WIDTH=.*/DISPLAY_WIDTH=$displayWidth/" "$SETTINGS_FILE"
		sed -i "s/^DISPLAY_HEIGHT=.*/DISPLAY_HEIGHT=$displayHeight/" "$SETTINGS_FILE"

        echo "Display Width updated to $displayWidth"
        echo "Display Height updated to $displayHeight"
    else
        echo "Resolution $current_res is NOT in the supported 16:9 list. Keeping saved configuration values."
    fi

else
    echo "No monitor detected. Using saved configuration resolution."
fi

#END Initialize the display resolution
####################################################################################################################################


OpenScreen () {
	#$1 = rtsp url
	#$2 = x divisor, number of screens on x axis
	#$3 = y divisor, number of screens on y axis
	#$4 = grid position, grid moves left to right, top to bottom, i.e. if both divisors are 3 and grid pos is 5, picture will be in the center of grid.
	
	OpenLargeScreen $1 $2 $3 $4 1
}

OpenLargeScreen () {
	#$1 = rtsp url
	#$2 = x divisor, number of screens on x axis
	#$3 = y divisor, number of screens on y axis
	#$4 = grid position, grid moves left to right, top to bottom, i.e. if both divisors are 3 and grid pos is 5, picture will be in the center of grid.
	#$5 = screen size multiplier
	
	#wait a random amount of time
	declare -i randomTimerInt=$RANDOM*5/32767 #generate a random number between 0 and 3276 ($RANDOM generates 0-32,767)
	randomTimer=$randomTimerInt"s" #add s to the end to indicate seconds
	sleep $randomTimer
	
	echo "Starting OpenLargeScreen()"
	echo " "
	
	#find width of display	
	declare -i width=$displayWidth/$2*$5
	echo "width = "$width
	
	#find height of display
	declare -i height=$displayHeight/$3*$5
	echo "height = "$height
	
	#find X of display
	#X = ((grid position-1)%x divisor) * (display width / x divisor)
	declare -i temp=($4-1)%$2
	#echo "temp = "$temp
	declare -i x=$displayWidth/$2*$temp
	echo "x = "$x
	
	#find Y of display
	#Y = ((the grid position-1)/ the x divisor, drop the decimal) * (display height / y divisor)
	declare -i temp=($4-1)/$2
	#echo "temp = "$temp
	declare -i y=$displayHeight/$3*$temp
	echo "y = "$y

	#display the screen with FFPLAY
	ffplay -noborder -x $width  -y $height -left $x -top $y $1 & sleep 5s
	
	echo " "
}


OpenDisplay () {
	if [ $layoutType -eq 1 ]
	then
		echo "Layout Type "$layoutType": 1x1"
		OpenScreen ${rtsp[${rtspIndex[0]}]} 1 1 1 &
		sleep 1s
	elif [ $layoutType -eq 2 ]
	then
		echo "Layout Type "$layoutType": 2x2"
		for ((i=0; i<4; i++)); do
			OpenScreen ${rtsp[${rtspIndex[$i]}]} 2 2 $i+1 &
		done
		sleep 1s
	elif [ $layoutType -eq 3 ]
	then
		echo "Layout Type "$layoutType": 3x3"
		for ((i=0; i<9; i++)); do
			OpenScreen ${rtspSub[${rtspIndex[$i]}]} 3 3 $i+1 &
		done
		sleep 1s
	elif [ $layoutType -eq 4 ]
	then
		echo "Layout Type "$layoutType": 4x4"
		for ((i=0; i<16; i++)); do
			OpenScreen ${rtspSub[${rtspIndex[$i]}]} 4 4 $i+1 &
		done
		sleep 1s
	elif [ $layoutType -eq 5 ]
	then
		echo "Layout Type "$layoutType": 6 Screens"
		OpenLargeScreen ${rtsp[${rtspIndex[0]}]} 3 3 1 2 &
		OpenScreen ${rtspSub[${rtspIndex[1]}]} 3 3 3 &
		OpenScreen ${rtspSub[${rtspIndex[2]}]} 3 3 6 &
		OpenScreen ${rtspSub[${rtspIndex[3]}]} 3 3 7 &
		OpenScreen ${rtspSub[${rtspIndex[4]}]} 3 3 8 &
		OpenScreen ${rtspSub[${rtspIndex[5]}]} 3 3 9 &
		sleep 1s
	elif [ $layoutType -eq 6 ]
	then
		echo "Layout Type "$layoutType": 10 Screens"
		for ((i=0; i<2; i++)); do
			OpenScreen ${rtsp[${rtspIndex[$i]}]} 2 2 $i+1 &
		done
		for ((i=2; i<10; i++)); do
			OpenScreen ${rtspSub[${rtspIndex[$i]}]} 4 4 $i+7 &
		done
		sleep 1s
	elif [ $layoutType -eq 7 ]
	then
		echo "Layout Type "$layoutType": 8 Screens"
		OpenLargeScreen ${rtsp[${rtspIndex[0]}]} 4 4 1 3 &
		OpenScreen ${rtspSub[${rtspIndex[1]}]} 4 4 4 &
		OpenScreen ${rtspSub[${rtspIndex[2]}]} 4 4 8 &
		OpenScreen ${rtspSub[${rtspIndex[3]}]} 4 4 12 &
		OpenScreen ${rtspSub[${rtspIndex[4]}]} 4 4 13 &
		OpenScreen ${rtspSub[${rtspIndex[5]}]} 4 4 14 &
		OpenScreen ${rtspSub[${rtspIndex[6]}]} 4 4 15 &
		OpenScreen ${rtspSub[${rtspIndex[7]}]} 4 4 16 &
		sleep 1s
	elif [ $layoutType -eq 8 ]
	then
		echo "Layout Type "$layoutType": 13 Screens"
		OpenLargeScreen ${rtsp[${rtspIndex[0]}]} 4 4 6 2 &
		OpenScreen ${rtspSub[${rtspIndex[1]}]} 4 4 1 &
		OpenScreen ${rtspSub[${rtspIndex[2]}]} 4 4 2 &
		OpenScreen ${rtspSub[${rtspIndex[3]}]} 4 4 3 &
		OpenScreen ${rtspSub[${rtspIndex[4]}]} 4 4 4 &
		OpenScreen ${rtspSub[${rtspIndex[5]}]} 4 4 5 &
		OpenScreen ${rtspSub[${rtspIndex[6]}]} 4 4 8 &
		OpenScreen ${rtspSub[${rtspIndex[7]}]} 4 4 9 &
		OpenScreen ${rtspSub[${rtspIndex[8]}]} 4 4 12 &
		OpenScreen ${rtspSub[${rtspIndex[9]}]} 4 4 13 &
		OpenScreen ${rtspSub[${rtspIndex[10]}]} 4 4 14 &
		OpenScreen ${rtspSub[${rtspIndex[11]}]} 4 4 15 &
		OpenScreen ${rtspSub[${rtspIndex[12]}]} 4 4 16 &
		sleep 1s
	elif [ $layoutType -eq 9 ]
	then
		echo "Layout Type "$layoutType": 5x5"
		for ((i=0; i<25; i++)); do
			OpenScreen ${rtspSub[${rtspIndex[$i]}]} 5 5 $i+1 &
		done
		sleep 1s
	elif [ $layoutType -eq 10 ]
	then
		echo "Layout Type "$layoutType": 6x6"
		for ((i=0; i<36; i++)); do
			OpenScreen ${rtspSub[${rtspIndex[$i]}]} 6 6 $i+1 &
		done
		sleep 1s
	elif [ $layoutType -eq 11 ]
	then
		echo "Layout Type "$layoutType": 7x7"
		for ((i=0; i<49; i++)); do
			OpenScreen ${rtspSub[${rtspIndex[$i]}]} 7 7 $i+1 &
		done
		sleep 1s
	else
		echo "Invalid Layout Type. No display will be generated."
	fi
	
}

CloseProgram () {
    echo " "
    echo "Closing program..."
    echo "Killing all ffplay instances..."

    # Kill all ffplay processes safely
    pkill -f ffplay

    sleep 1s

    echo "All ffplay instances terminated."
    echo "Exiting start.sh..."
    exit 0
}

LaunchCloseButton () {

    buttonSize=70
    margin=20

    posX=$((displayWidth - buttonSize - margin))
    posY=$margin

    yad --undecorated \
        --skip-taskbar \
        --sticky \
        --fixed \
        --borders=0 \
        --no-focus \
        --geometry=${buttonSize}x${buttonSize}+${posX}+${posY} \
        --button="❌:0" \
        --text="" \
        --title="" \
        --on-top &

    closeButtonPID=$!

    wait $closeButtonPID

    if [ $? -eq 0 ]; then
        CloseProgram
    fi
}

if [ $passedInitialization -eq 1 ]; then

#pre runtime loop #######################################################################################################################################################################################

	python3 scripts/close_overlay.py &
	OpenDisplay

#END pre runtime loop ###################################################################################################################################################################################

#main runtime loop ######################################################################################################################################################################################	
	for ((i=0; i<5; i++)); do
		sleep $runtimeBeforeLoop #wait until the runtime timer expires
		
		#collect the pids of the active ffplay instaces
		numberOfPids="$(pgrep ffplay -c)"
		pidString="$(pgrep ffplay)" #get all the running ffplay pids in a string. The pids are separated by spaces.	
		pidArray=($pidString) #convert the string to an array
		
		echo " " #output the pids to the terminal
		echo "Displaying list of PIDs"
		for ((j=0; j<$numberOfPids; j++)); do
			echo "PID number "$j":"
			echo ${pidArray[$j]}
		done
		
		OpenDisplay #open a new instance of the displays
		
		sleep 5s #wait 5s before killing old screens
		
		for ((j=0; j<$numberOfPids; j++)); do
			kill ${pidArray[$j]} #kill all the old screens
		done
		
		#reset the value of i in order to make the runtime loop indefinitely
		if [ $loopRuntimeForever -eq 1 ]
			then
			i=0
		fi
	done
#END main runtime loop ##################################################################################################################################################################################

	killall ffplay #terminate any ffplay instances that are still active
	
else
	echo "Critical initialization error caused program to fail. Please check your config files."
fi
	
#all code must be above this line
echo " "
echo "closing start.sh..."
echo "this program will end now"
#this is the last line in the program
