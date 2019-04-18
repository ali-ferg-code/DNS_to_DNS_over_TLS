#!/bin/sh

a=0

while [ $a -lt $1 ]
do
   echo $a
   a=`expr $a + 1`
   dig google.com
done
