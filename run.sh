#!/bin/bash

INPUT=$1
OUTPUT=$2

if [ -z "$OUTPUT" ]
then
    echo Usage:
    echo "    process.sh  INPUT OUTPUT"
    echo
    echo "INPUT: directory contain dcm files"
    echo "OUTPUT: output directory"
    exit
fi

if [ ! -d "$INPUT" ]
then
    echo Input directory $INPUT does not exist.
    exit
fi

INPUT=`readlink -e $INPUT`
if echo "$OUTPUT" | grep -v '^/'
then
    OUTPUT=$PWD/$OUTPUT
fi

MY_UID=`id -u`
MY_GID=`id -g`

mkdir -p $OUTPUT
mkdir -p $OUTPUT/intermediate/prep_result
mkdir $OUTPUT/intermediate/bbox_result
chmod -R a+rw $OUTPUT

# build docker
nvidia-docker build -t lung .

# run docker
nvidia-docker run --rm -it \
     -v $INPUT:/work/Data/ \
     -v $OUTPUT:/output \
     -v $OUTPUT/intermediate/prep_result:/work/grt123-DSB2017/prep_result \
     -v $OUTPUT/intermediate/bbox_result:/work/grt123-DSB2017/bbox_result \
     -e HUID=$MY_UID -e HGID=$MY_GID \
     lung /bin/bash process.sh

