#!/bin/sh
#add or change create_dcm to create_vsend if needed
if [[ -z $MURFI_SUBJECT_NAME ]];
then
    input_string=$(zenity --forms --title="MURFI GUI" \
    --separator=" " \
    --add-entry="Participant ID (####)" \
    --add-combo="Step" --combo-values "create_dcm|setup" \
    --cancel-label "Exit" --ok-label "Run Selected Step")
    ret=$?
	# parse zenity output using space as delimiter
	read -a input_array <<< $input_string
	partcipant_id=sub-mindbpd${input_array[0]}
	step=${input_array[1]}
	
else
	input_string=$(zenity --forms --title="MURFI GUI" \
	--text="PARTICIPANT NAME: ${MURFI_SUBJECT_NAME}" \
	--separator=" " \
	--add-combo="Step" --combo-values "setup|------LOCALIZER-----|2vol|resting_state|extract_rs_networks|process_roi_masks|register|------NEUROFEEDBACK------|2vol|register|feedback|cleanup|backup_reg_mni_masks_to_2vol" \
	--cancel-label "Exit" --ok-label "Run Selected Step"\
	--width=300 --height=200)
	ret=$?
	# parse zenity output using space as delimiter
	read -a input_array <<< $input_string
	step=${input_array[0]}
	partcipant_id=$MURFI_SUBJECT_NAME
fi

# If user selects the Exit button, then quit MURFI
if [[ $ret == 1 ]];
then
	exit 0
fi


# Run selected step
#uncomment this if you need vsend creation
#if [ ${step} == 'create_vsend' ]
#then
#	echo "[$(date +%F_%T)] source createxml_vsend.sh ${partcipant_id} setup" >> "../#subjects/${partcipant_id}/murfi_command_log.txt"
#	source createxml_vsend.sh ${partcipant_id} setup 
	
if [ ${step} == 'create_dcm' ]
then
	echo "[$(date +%F_%T)] source createxml_dcm.sh ${partcipant_id} setup" >> "../subjects/${partcipant_id}/murfi_command_log.txt"
	source createxml_dcm.sh ${partcipant_id} setup 

else
	echo "[$(date +%F_%T)] source feedback.sh ${partcipant_id} ${step}" >> "../subjects/${partcipant_id}/murfi_command_log.txt"
	source feedback.sh ${partcipant_id} ${step}
fi

# Re-launch script to keep MURFI GUI open 
bash launch_murfi.sh
