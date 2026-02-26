#parameters:
#$1 is the display layout type as definined in CONF.txt
#$2 is the monitor width in pixels
#$3 is the monitor height in pixels
#$4 is the display time
#$5 is the entire 1st rtsp url
#$6 is the entire 2nd rtsp url
#$7 etc...


#!/bin/bash

echo "Starting openDisplaySwitch.sh..."
echo " "

	if [ $1 -eq 1 ]
	then
		echo bash scripts/openDisplay.sh $5 $2 $3 1 1 1 $4
	elif [ $1 -eq 2 ]
	then
		bash scripts/openDisplay2x2.sh $2 $3 $4 $5 $6 $7 $8
	elif [ $1 -eq 3 ]
	then
		bash scripts/openDisplay3x3.sh $2 $3 $4 $5 $6 $7 $8 $9 ${10} ${11} ${12} ${13}
	elif [ $1 -eq 4 ]
	then
		echo "4x4 screens are not yet implemented."
		bash scripts/openDisplay4x4.sh $2 $3 $4 $5 $6 $7 $8 $9 ${10} ${11} ${12} ${13} ${14} ${15} ${16} ${17} ${18} ${19} ${20}
	elif [ $1 -eq 5 ]
	then
		bash scripts/openDisplay5x5.sh $2 $3 $4 $5 $6 $7 $8 $9 ${10} ${11} ${12} ${13} ${14} ${15} ${16} ${17} ${18} ${19} ${20} ${21} ${22} ${23} ${24} ${26} ${27} ${28} ${29}
	elif [ $1 -eq 6 ]
	then
		echo "6 screens not yet implemeneted."
	elif [ $1 -eq 7 ]
	then
		echo "8 screens not yet implemeneted."
	elif [ $1 -eq 8 ]
	then
		echo "10 screens not yet implemeneted."
	else
		echo "Invalid Display Layout Type. Check CONF.txt"
		echo "Check CONF.txt"
		echo "Check CONF.txt"
		echo "Check CONF.txt" 
	fi

echo "ending openDisplaySwitch.sh"
echo " "
