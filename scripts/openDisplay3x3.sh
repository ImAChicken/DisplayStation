#parameters:
#$1 is the monitor width in pixels
#$2 is the monitor height in pixels
#$3 is the display time
#$4 is the entire 1st rtsp url
#$5 is the entire 2nd rtsp url
#$6 is the entire 3rd rtsp url
#$7 is the entire 4th rtsp url
#$8 is the entire 5th rtsp url
#$9 is the entire 6th rtsp url
#$10 is the entire 7th rtsp url
#$11 is the entire 8th rtsp url
#$12 is the entire 9th rtsp url


#!/bin/bash

echo "Starting openDisplay3x3.sh..."
echo " "
	
	bash scripts/openDisplay.sh $4 $1 $2 3 3 1 $3 &
	bash scripts/openDisplay.sh $5 $1 $2 3 3 2 $3 &
	bash scripts/openDisplay.sh $6 $1 $2 3 3 3 $3 &
	bash scripts/openDisplay.sh $7 $1 $2 3 3 4 $3 &
	bash scripts/openDisplay.sh $8 $1 $2 3 3 5 $3 &
	bash scripts/openDisplay.sh $9 $1 $2 3 3 6 $3 &
	bash scripts/openDisplay.sh ${10} $1 $2 3 3 7 $3 &
	bash scripts/openDisplay.sh ${11} $1 $2 3 3 8 $3 &
	bash scripts/openDisplay.sh ${12} $1 $2 3 3 9 $3

echo "ending openDisplay3x3.sh"
echo " "
