#!/bin/bash

##Input taken: subject_ID##
set -e

subject=${1}
step=${2}

subject_dir=../subjects/
cwd=$(pwd)

#!/bin/bash


# Check if subject directory exists
if [[ -d "${subject_dir}/${subject}" ]]; then
    # Ask user what to do
    if zenity --question \
        --title="Subject Exists" \
        --text="Directory exists: ${subject_dir}/${subject}\nOverwrite or Keep Existing?" \
        --ok-label="Overwrite" \
        --cancel-label="Keep Existing" \
        --width=350; then
        
        # User chose Overwrite - remove directory
        echo "Removing existing directory..."
        if ! rm -rf "${subject_dir}/${subject}"; then
            zenity --error --text="Failed to remove directory!" --width=300
            exit 1
        fi
        echo "Directory removed successfully"
    else
        # User chose Keep Existing - relaunch
        echo "Keeping existing directory - restarting..."
        exec bash launch_murfi.sh
    fi
fi
if [ ${step} = setup ]
then
clear
    usage="usage: source $(basename $0) subject_ID"
    mkdir ${subject_dir}$subject
    mkdir ${subject_dir}$subject/img
    mkdir ${subject_dir}$subject/log
    mkdir ${subject_dir}$subject/mask
    mkdir ${subject_dir}$subject/mask/mni
    mkdir ${subject_dir}$subject/xfm
    mkdir ${subject_dir}$subject/xml
    mkdir ${subject_dir}$subject/rest
    mkdir ${subject_dir}$subject/fsfs
    mkdir ${subject_dir}$subject/qc # DP ADD 4/12/23
    echo "++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++"
    echo "created all directories for "$subject
    echo "++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++"
    cp ${subject_dir}template/xml/xml_vsend/* ${subject_dir}$subject/xml/

    ##### This copies template cen.dmn.smc and stg masks to the test mask folder, please uncomment this line and copy the subjects own masks to this folder 
    #cp -r ${subject_dir}template/mask/* ${subject_dir}$subject/mask/
fi
