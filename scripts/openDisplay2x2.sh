#parameters:
#$1 is the monitor width in pixels
#$2 is the monitor height in pixels
#$3 is the display time
#$4 is the entire 1st rtsp url
#$5 is the entire 2nd rtsp url
#$6 is the entire 3rd rtsp url
#$7 is the entire 4th rtsp url


#!/bin/bash

echo "Starting openDisplay2x2.sh..."
echo " "
	
	bash scripts/openDisplay.sh $4 $1 $2 2 2 1 $3 &
	bash scripts/openDisplay.sh $5 $1 $2 2 2 2 $3 &
	bash scripts/openDisplay.sh $6 $1 $2 2 2 3 $3 &
	bash scripts/openDisplay.sh $7 $1 $2 2 2 4 $3

echo "ending openDisplay2x2.sh"
echo " "
