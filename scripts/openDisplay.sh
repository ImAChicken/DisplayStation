#parameters:
#$1 is the entire rtsp url
#$2 is the monitor width in pixels
#$3 is the monitor height in pixels
#$4 is the x divisor, the number of screens on the x axis
#$5 is the y divisor, the number of screens on the y axis
#$6 is the grid position, grid moves left to right, top to bottom, i.e. if both divisors are 3 and grid pos is 5, picture will be in the center of grid.
#$7 is the time the screen will be displayed



#!/bin/bash

echo "Starting openDisplay.sh..."
echo " "

	#find width of display	
	declare -i width=$2/$4
	echo "width = "$width
	
	#find height of display
	declare -i height=$3/$5
	echo "height = "$height
	
	#find X of display
	#X = ((grid position-1)%x divisor) * (display width / x divisor)
	declare -i temp=($6-1)%$4
	echo "temp = "$temp
	declare -i x=$2/$4*$temp
	echo "x = "$x
	
	#find Y of display
	#Y = ((the grid position-1)/ the x divisor, drop the decimal) * (display height / y divisor)
	declare -i temp=($6-1)/$4
	echo "temp = "$temp
	declare -i y=$3/$5*$temp
	echo "y = "$y
	
	#wait a random amount of time
	declare -i randomTimerInt=$RANDOM*10/32767 #generate a random number between 0 and 3276 ($RANDOM generates 0-32,767)
	randomTimer=$randomTimerInt"s" #add s to the end to indicate seconds
	sleep $randomTimer

	ffplay -noborder -x $width  -y $height -left $x -top $y $1 & sleep $7
		
		
	#killall ffplay

echo "ending openDisplay.sh"
echo " "
