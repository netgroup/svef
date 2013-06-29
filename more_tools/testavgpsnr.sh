#!/bin/bash

TEST=$1; 
INITFRAME=${2:-1000}
ENDFRAME=${3:-1400}

averagepsnr.py autotest${TEST}/x${TEST}_var_matlab.txt $INITFRAME $ENDFRAME 
averagepsnr.py autotest${TEST}/x${TEST}_11_matlab.txt $INITFRAME $ENDFRAME

