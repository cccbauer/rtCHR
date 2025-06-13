#!/bin/bash

##Input taken: subject_ID##
set -e

subject=${1}
step=${2}

subject_dir=../subjects/
rct_dir=./RCT/

if [ ${subject} = help ]
then
	echo "$(tput setaf 1)USAGE: $(basename $0)  subject_ID setup (just to create subject folders)"
	exit
fi


if [ ${step} = setup ]
then
	#clear
	usage="usage: source $(basename $0) subject_ID"
	mkdir ${subject_dir}$subject
	mkdir ${subject_dir}$subject/img
	mkdir ${subject_dir}$subject/log
	mkdir ${subject_dir}$subject/mask
	mkdir -p ${subject_dir}$subject/mask/mni
	mkdir ${subject_dir}$subject/xfm
	mkdir ${subject_dir}$subject/xml
	mkdir -p ${subject_dir}$subject/xml/rct
	mkdir ${subject_dir}$subject/rest
	mkdir ${subject_dir}$subject/fsfs
	mkdir ${subject_dir}$subject/qc # DP ADD 4/12/23
	echo "++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++"
	echo "created all directories for "$subject
	echo "++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++"
	cp ${subject_dir}template/xml/xml_orig/* ${subject_dir}$subject/xml/
	cp ${subject_dir}template/mask/mni/* ${subject_dir}$subject/mask/mni/
	awk -v subject="$subject" '$1 == subject {print $2 > "'${subject_dir}'"subject"/xml/rct/rct.txt"}' "${rct_dir}/randomization.tsv"


	##### This copies template cen.dmn.smc and stg masks to the test mask folder, please uncomment this line and copy the subjects own masks to this folder 
	#cp -r ${subject_dir}template/mask/* ${subject_dir}$subject/mask/

fi
