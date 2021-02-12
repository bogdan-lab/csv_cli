#!/bin/bash
CFG=$1

echo "---> HYBRID SEGMENT <---"
grep hybrid -A 7 ${CFG}
echo " "
echo "-------------------------"
echo " "
echo "---> MATERIAL SEGMENT <---"
grep material ${CFG}
echo " "
echo "-------------------------"
echo " "
echo "---> TIME SEGMENT <---"
grep full_time ${CFG}
grep t_write ${CFG}
grep dt ${CFG}
echo " "
echo "-------------------------"


