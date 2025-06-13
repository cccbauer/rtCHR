#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
This experiment was created using PsychoPy2 Experiment Builder (v1.81.03), Wed 04 Feb 2015 11:22:15 AM EST
If you publish work using this script please cite the relevant PsychoPy publications
  Peirce, JW (2007) PsychoPy - Psychophysics software in Python. Journal of Neuroscience Methods, 162(1-2), 8-13.
  Peirce, JW (2009) Generating stimuli for neuroscience using PsychoPy. Frontiers in Neuroinformatics, 2:10. doi: 10.3389/neuro.11.010.2008
"""

from __future__ import division  # so that 1/3=0.333 instead of 1/3=0
from psychopy import visual, core, data, event, logging, sound, gui
from psychopy.constants import *  # things like STARTED, FINISHED
import numpy as np  # whole numpy lib is available, prepend 'np.'
from numpy import sin, cos, tan, log, log10, pi, average, sqrt, std, deg2rad, rad2deg, linspace, asarray
from numpy.random import random, randint, normal, shuffle
import os  # handy system and path functions
import time
import matplotlib.pyplot as plt
import matplotlib
import random
import csv
import math
import pandas as pd
import sys
import threading
import subprocess
import shlex
import locale
from bids_tsv_convert_balltask import *
import fnmatch # for matching csv file names for given run for sham subjects
import numpy as np


# button box yale
#left_button='3'
#right_button='4'
#enter_button='1'

# button box mgh
left_button='1'
right_button='2'
enter_button='0'

# Ensure that relative paths start from the same directory as this script
_thisDir = os.path.dirname(os.path.abspath(__file__))
os.chdir(_thisDir)

##################################################################################
## PARSE COMMAND LINE ARGUMENTS TO AUTOFILL DIALOGUE BOX AT STARTUP (for runs 2+) ##
num_cmd_line_arguments = len(sys.argv)
if num_cmd_line_arguments >= 2:
    input_participant = sys.argv[1]
else:
    input_participant = ''

# cmd line arg 3 will be run number
# if there is no command line argument 3 -- use empty string
# otherwise, use that as rum number
if num_cmd_line_arguments >= 3:
    input_run = sys.argv[2]
else:
    input_run = ''

# cmd line arg 4 will be feedback / no feedback 
if num_cmd_line_arguments >= 4:
    if sys.argv[3] == 'Feedback':
        input_feedback = ['Feedback', 'No Feedback']
    else:
        input_feedback = ['No Feedback', 'Feedback']
else:
    input_feedback = ['', 'Feedback', 'No Feedback']

# cmd line arg 5 will be 15min vs 30min
if num_cmd_line_arguments >= 4:
    if sys.argv[4] == '15min':
        input_feedback_condition = ['15min', '30min']
    else:
        input_feedback_condition = ['30min', '15min']
else:
    input_feedback_condition = ['', '15min', '30min']



# cmd line arg 6+ will be anchor
# if there is no command line argument -- use empty string
# otherwise, use that as rum number
if num_cmd_line_arguments >= 5:
    input_anchor = ' '.join(sys.argv[5:])
else:
    input_anchor = ''

#####################################################################################

# Store info about the experiment 
expName = 'DMN_BallTask'  # from the Builder filename that created thi s script
expInfo = {'participant':input_participant, 'run':input_run, 'anchor': input_anchor, 'feedback_on': input_feedback}


murfi_FAKE=False

# SHAM = True # added for Sham Feedback - this is now set through the dialogue box

# Show dialogue box until all participant info has been entered
while expInfo['feedback_on'] not in ['Feedback', 'No Feedback']:
    expInfo['feedback_on'] =  input_feedback
    dlg = gui.DlgFromDict(dictionary=expInfo, title=expName, 
        labels = {'participant': 'Participant ID (2XXX)',
                  'run': 'Run',
                  'feedback_on': 'Display Feedback?',
                  'anchor': 'Participant Anchor'},
        order = ['participant', 'run', 'feedback_on', 'anchor'])
    if dlg.OK == False: 
        core.quit()  # user pressed cancel
        

# Hard code other experiment info 
## Timestamp
expInfo['date'] = data.getDateStr()  
expInfo['expName'] = expName
expInfo['No_of_ROIs'] = 2
expInfo['Level_1_2_3'] = 1
expInfo['Run_Time'] = 150
expInfo['pda_outlier_threshold']=2
circles_move_with_hits=False
circle_radius_shrink_with_hits=True
num_pda_outliers=0
# Baseline time before feedback (seconds)
BaseLineTime=30 

# TR (seconds)
expInfo['tr']=1.2

# BPD changes
expInfo['feedback_condition'] = '15min'

#
roi_number_circles= str('%s') %(expInfo['No_of_ROIs'])
roi_number_circles=int(roi_number_circles)

'''
Minimum and maximum number of "hits" to targets for which scale factor won't be adjusted
Fewer hits than min_hits --> scale factor goes up and ball moves faster
More hits than max_hits (in either direction) --> scale factor goes down and ball moves more slowly
'''
min_hits=3 #3
max_hits=5 #5

# default scale factor (higher means ball moves up/down faster)
default_scale_factor = 10

# another interal scale factor to make sure scaling of feedback is appropriate (higher means ball moves up/down more SLOWLY)
internal_scaler=10


filename_prefix = "sub-rtchr"
foldername = os.path.join('data', filename_prefix + expInfo['participant'])
os.makedirs(foldername, exist_ok=True)  # Create 'data' and participant folder if needed

print("expInfo['feedback_on'] =", expInfo['feedback_on'])

# --- Define function to build filename
def build_filename(participant, run, feedback_flag):
    suffix = 'feedback' if feedback_flag == 'Feedback' else 'nofeedback'
    return os.path.join(foldername, f"{filename_prefix}{participant}_DMN_{suffix}_{run}")

# --- Initial filename
filename = build_filename(expInfo['participant'], expInfo['run'], expInfo['feedback_on'])

# --- Handle existing file via GUI dialog
while os.path.exists(filename + '_roi_outputs.csv'):
    warning_box = gui.Dlg(title='WARNING')
    warning_box.addText(
        f'Already have data for {expInfo["participant"]} run {expInfo["run"]}!\n'
        f'Click OK to write to Run {int(expInfo["run"]) + 1} instead\n'
        f'To overwrite run {expInfo["run"]}, select this option from the dropdown menu\n'
        f'Or, click Cancel to exit'
    )
    warning_box.addField(
        'Choose Run #',
        choices=[
            f"Run {int(expInfo['run']) + 1}",
            f"Overwrite Run {int(expInfo['run'])}"
        ]
    )
    warning_box_data = warning_box.show()

    if not warning_box.OK:
        core.quit()

    run_choice = warning_box_data[0].strip()
    
    if run_choice != f"Overwrite Run {expInfo['run']}":
        expInfo['run'] = int(expInfo['run']) + 1
        filename = build_filename(expInfo['participant'], expInfo['run'], expInfo['feedback_on'])
    else:
        print('OVERWRITE')
        print(filename)
        for suffix in ['_slider_questions.csv', '_roi_outputs.csv', '.csv', '.psydat','.tsv']:
            try:
                os.remove(filename + suffix)
            except FileNotFoundError:
                pass  # If already deleted, ignore
        break

# If first run, use default scale factor
# Otherwise, adjust scale factor up/down if needed
if int(expInfo['run']) == 1:
    print('Run 1: starting with default scale scale factor')
    expInfo['scale_factor'] = default_scale_factor
else:
    try:

        # loop through prior runs, starting at most recent, until the most recent prior run with at least 140 volumes is found
        # label this most recent run with 140+ volumes as the "last run" to pull parameters from
        last_run_complete=False
        last_run_counter=1
        while last_run_complete==False and last_run_counter < int(expInfo['run']):
            last_run_filename = filename.replace("feedback_" + str(expInfo['run']),
                                                 "feedback_" + str(int(expInfo['run'])-last_run_counter)) + '_roi_outputs.csv'
            print(last_run_filename)
            print("This run:",expInfo['run'])
            print("participant IDL",expInfo['participant'])
            last_run_info = pd.read_csv(last_run_filename)
            if last_run_info.shape[0] > 140:
                last_run_complete=True
            else:
                last_run_counter+=1

        # ONLY update scale factor if there is a prior COMPLETE run to use to do this
        if last_run_complete:
            # Dynamically determine which cumulative hits columns are available
            if "cen_cumulative_hits" in last_run_info.columns and "dmn_cumulative_hits" in last_run_info.columns:
                last_run_cen_hits = last_run_info["cen_cumulative_hits"].max()
                last_run_dmn_hits = last_run_info["dmn_cumulative_hits"].max()
            elif "smcl_cumulative_hits" in last_run_info.columns and "smcr_cumulative_hits" in last_run_info.columns:
                last_run_cen_hits = last_run_info["smcl_cumulative_hits"].max()
                last_run_dmn_hits = last_run_info["smcr_cumulative_hits"].max()
            else:
                print("⚠️ Could not find valid cumulative hits columns in last run file.")
                last_run_cen_hits = 0
                last_run_dmn_hits = 0


            print('Last run volumes: ', last_run_info.shape[0], ' Last run filename: ', last_run_filename)
            print('Last run SMCx or CEN hits: ', last_run_cen_hits, ' Last run SMCx DMN hits: ', last_run_dmn_hits)

            # last_run_scale_factor
            last_run_scale_factor = last_run_info.scale_factor[0]

            # if 5+ hits in either direction, decrease scale factor
            if last_run_dmn_hits > max_hits or last_run_cen_hits > max_hits:
                expInfo['scale_factor'] = last_run_scale_factor * 0.75
            
            # if not enough hits, increase scale factor
            elif last_run_cen_hits + last_run_dmn_hits < min_hits:
                expInfo['scale_factor'] = last_run_scale_factor * 1.25

            # otherwise, keep scale factor the same
            else:
                expInfo['scale_factor'] = last_run_scale_factor 

            print('Last run scale factor: ', last_run_scale_factor, ' This run scale factor: ', expInfo['scale_factor'])
        else:
            print('WARNING: no prior complete runs. Settting to default scale factor.')
            expInfo['scale_factor'] = default_scale_factor

    # If this breaks (no prior runs) use default scale factor    
    except Exception as error:
        print(error)
        print('ERROR: could not pull scale factor from previous run. Settting to default scale factor.')
        expInfo['scale_factor'] = default_scale_factor

'''
For Sham subjects read the frame data from the csv file for the matching run in the 'feedback' folder
There should exist a folder by the same subject number within the 'feedback' folder and it should 
contain csv files from matched experimental subject having 'Feedback_{run_number}' in their name
Each run should have a corresponding csv file
'''


RUN_TIME= str('%s') %(expInfo['Run_Time'])
RUN_TIME=int(RUN_TIME)
RUN_TIME=RUN_TIME

# Convert scale factor and position to pixel space
position_distance=expInfo['Level_1_2_3']
position_distance=int(position_distance)
scale_factor_z2pixels=expInfo['scale_factor']
scale_factor_z2pixels=int(scale_factor_z2pixels)
logFile = logging.LogFile(filename+'.log', level=logging.EXP)
logging.console.setLevel(logging.WARNING)  # this outputs to the screen, not a file



# Build subject ID from filename_prefix and participant input
subject_rct = f"{filename_prefix}{expInfo['participant']}"


# Read the randomization file
with open('rct/randomization.tsv', 'r') as f:
    lines = f.readlines()

# Extract header and clean lines
header = lines[0].strip().split()
entries = [line.strip().split() for line in lines[1:] if line.strip()]

# Create lookup dictionary
group_dict = {entry[0]: entry[1] for entry in entries}

# Get group assignment for the subject
group = group_dict.get(subject_rct)
frame = 0
# Calculate PDA and set dynamic labels
if group == '1':
    pda_label = 'cen_dmn_pda'
    cumulative_hit_labels = ['cen_cumulative_hits', 'dmn_cumulative_hits']
elif group == '0':
    pda_label = 'smcl_smcr_pda'
    cumulative_hit_labels = ['smcl_cumulative_hits', 'smcr_cumulative_hits']
else:
    pda_val = np.nan
    pda_label = 'unknown_pda'
    cumulative_hit_labels = ['roi1_cumulative_hits', 'roi2_cumulative_hits']

# Define dynamic header
csv_header = [
    'volume', 'scale_factor', 'time', 'time_plus_1.2',
    'smcl', 'smcr', 'cen', 'dmn',
    'stage', *cumulative_hit_labels,
    'num_pda_outliers', 'pda_value', 'pda_label',
    'ball_y_position', 'top_circle_y_position', 'bottom_circle_y_position']

# Write to file
csv_path = filename + '_roi_outputs.csv'
file_exists = os.path.isfile(csv_path)

with open(csv_path, 'a') as csvfile:
    stim_writer = csv.writer(csvfile, delimiter=',', quotechar='|', quoting=csv.QUOTE_MINIMAL)

    # Write header only if file is new
    if not file_exists or os.stat(csv_path).st_size == 0:
        stim_writer.writerow(csv_header)


# An ExperimentHandler isn't essential but helps with data saving
thisExp = data.ExperimentHandler(name=expName, version='',
    extraInfo=expInfo, runtimeInfo=None,
    originPath=None,
    savePickle=True, saveWideText=True,
    dataFileName=filename)
#save a log file for detail verbose info
logFile = logging.LogFile(filename+'.log', level=logging.EXP)
logging.console.setLevel(logging.WARNING)  # this outputs to the screen, not a file
endExpNow = False  # flag for 'escape' or other condition => quit the exp

# Start Code - component code to be run before the window creation
# Setup the Window
win = visual.Window(size=(1080,1080), fullscr=False, screen=1, allowGUI=False, allowStencil=False,#1024, 1024
    monitor='testMonitor', color=[-1,-1,-1], colorSpace='rgb',
    blendMode='avg', useFBO=True,
    )

# store frame rate of monitor if we can measure it successfully
expInfo['frameRate']=win.getActualFrameRate()
if expInfo['frameRate']!=None:
    frameDur = 1.0/expInfo['frameRate']
else:
    print('FRAME RATE GUESSING')
    frameDur = 1.0/60.0 # couldn't get a reliable measure so guess

# Approximately how many frames does the monitor refresh per volume?
tr_to_frame_ratio = expInfo['tr']/frameDur

# Create csv output file for post-run slider questions
run_questions_file = filename + '_slider_questions.csv'
with open(run_questions_file, 'a') as csvfile:
    stim_writer = csv.writer(csvfile, delimiter=',', quotechar='|', quoting=csv.QUOTE_MINIMAL)
    stim_writer.writerow(["id", "run", 'feedback_on', "question_text", "response", "rt"])  

slider_instruction = visual.TextStim(win=win, ori=0, name='text',
        text="You'll see a few slider questions next\nPress the left and right buttons to move the slider\nAnd the top button to enter your response\nPress any button to continue", 
        pos=[0, 0.2], height=0.06, wrapWidth=1.2,
        color=u'white', colorSpace='rgb', opacity=1,
        depth=0.0)


def run_slider(question_text='Default Text', left_label='left', right_label='right'):
    slider_question = visual.TextStim(win=win, ori=0, name='text',
        text=question_text, 
        pos=[0, 0.2], height=0.06, wrapWidth=1.2,
        color=u'white', colorSpace='rgb', opacity=1,
        depth=0.0)

    vas = visual.Slider(win,
                size=(0.85, 0.1),
                ticks=(1, 9),
                labels=(left_label, right_label),
                granularity=1,
                color='white',
                fillColor='white')

    event.clearEvents('keyboard')
    vas.markerPos = 5
    vas.draw()
    slider_question.draw()
    win.flip()
    continueRoutine = True
    while continueRoutine:
        keys = event.getKeys(keyList=[left_button, right_button, enter_button])
        if len(keys):
            if left_button in keys:
                vas.markerPos = vas.markerPos - 1
            elif right_button in keys:
                vas.markerPos = vas.markerPos  + 1 
            elif enter_button in keys:
                vas.rating=vas.markerPos
                continueRoutine=False
            vas.draw()
            slider_question.draw()
            win.flip()
            print(keys)

    print(f'Rating: {vas.rating}, RT: {vas.rt}')
    with open(run_questions_file, 'a') as csvfile:
            stim_writer = csv.writer(csvfile, delimiter=',', quotechar='|', quoting=csv.QUOTE_MINIMAL)
            stim_writer.writerow([expInfo['participant'], expInfo['run'], expInfo['feedback_on'],
                                  question_text, vas.rating, vas.rt])   

    
    return(vas.rating)

# Initialize components for Routine "instructions"
instructionsClock = core.Clock()
text = visual.TextStim(win=win, ori=0, name='text',
    text='',
    pos=[0, 0], height=0.06, wrapWidth=1.2,
    color=u'white', colorSpace='rgb', opacity=1,
    depth=0.0)

# Initialize components for Routine "trigger"
triggerClock = core.Clock()
waiting_for_trigger_text = visual.TextStim(win=win, ori=0, name='waiting_for_trigger_text',
    text=u'waiting for scanner',    
    pos=[0, 0], height=0.1, wrapWidth=2,
    color=u'white', colorSpace='rgb', opacity=1,
    depth=0.0)

# Initialize components for Routine "baseline"
baselineClock = core.Clock()
text_2 = visual.TextStim(win=win, ori=0, name='text_2',
    text=u'+',    
    pos=[0, 0], height=0.3, wrapWidth=None,
    color=u'white', colorSpace='rgb', opacity=1,
    depth=0.0)


text_relax = visual.TextStim(win=win, ori=0, name='text_relax',
    text=u'Relax',    
    pos=[0, -.2], height=0.07, wrapWidth=None,
    color=u'white', colorSpace='rgb', opacity=1,
    depth=0.0)

# Initialize components for Routine "feedback"
feedbackClock = core.Clock()

text_4 = visual.TextStim(win=win, ori=0, name='text_4',
    text='default text',    
    pos=[0, 0], height=0.1, wrapWidth=None,
    color=u'white', colorSpace='rgb', opacity=1,
    depth=-3.0)

#prepare the targets
colors=['yellow','lightblue','red','green','cyan','magenta','black','honeydew','indigo','maroon']

# Extract header and clean lines
header = lines[0].strip().split()
entries = [line.strip().split() for line in lines[1:] if line.strip()]

# Create lookup dictionary
group_dict = {entry[0]: entry[1] for entry in entries}

# Get group assignment for the subject
group = group_dict.get(subject_rct)

# Set ROI names based on group
if group == '1':
    roi_names_list = ['cen', 'dmn', 'smcl', 'smcr']
    cumulative_hits_fields = ['cen_cumulative_hits', 'dmn_cumulative_hits']
else:
    # Randomize the order of smcl and smcr, but keep cen/dmn fixed
    sm_rois = ['smcl', 'smcr']
    random.shuffle(sm_rois)  # shuffles in-place
    roi_names_list = sm_rois + ['cen', 'dmn']
    cumulative_hits_fields = [f'{roi}_cumulative_hits' for roi in sm_rois]

#print(f"Subject {subject_rct} is in group {group}. ROI names: {roi_names_list}")

#create the circles
tau = 2 * np.pi
theta = np.zeros((roi_number_circles))
for i in range(roi_number_circles):
    theta[i] = (i * tau)/float(roi_number_circles)

positions = np.exp((0-1j) * theta)
positions=positions*position_distance
positions = [1, -1]

# target_positions:
roi_pos = np.zeros((roi_number_circles, 2))
for i in range(roi_number_circles):
    roi_pos[i, :] = [(np.real(positions[i]))/3, (np.imag(positions[i]))/3]

# scale based on aspect ratio
scale=[win.size[1]/win.size[0], 1]

target_circles=[]
target_circles_id=[]
hit_counter=[]
home=[]
for i in range(roi_number_circles):
    roi_circle_i = visual.Circle(win, pos=(roi_pos[i, 1],roi_pos[i, 0]), 
                                 radius=0.15,fillColor=None, 
                                 lineColor=colors[i], lineWidth=3)
    roi_circle_i.size *= scale
    target_circles.append(roi_circle_i)
    hit_counter.append(0)
    print (hit_counter)

starting_point = visual.Circle(win, pos=(0,0), radius=0.005,fillColor='white', lineColor='white')
home.append(starting_point)

# function to check whether ball is in a given circle
def in_circle(center_x, center_y, radius, x, y):
    square_dist = (center_x - x) ** 2 + (center_y - y) ** 2
    return square_dist <= radius ** 2


# checks if ball has gone out of bounds above/below the middle of a circle
def further_than_circles(position, circle_center, ball_center):
    # if ball is above center of top circle
    if position == 0:
        further = ball_center > circle_center
    # if ball is below center of bottom circle
    elif position == 1:
        further = ball_center < circle_center
    return(further)


def wait_for_keypress(key_list:list):
    continueRoutine = True
    while continueRoutine:
        theseKeys = event.getKeys(keyList=key_list)
        if len(theseKeys) > 0:  # at least one key was pressed
                # a response ends the routine
                continueRoutine = False


def run_instructions(instruct_text):
    instruct_text.draw()
    win.flip()
    wait_for_keypress(['space', '1', '2'])


def quit_psychopy():
    """Close everything and exit nicely (ending the experiment)
    """
    # pygame.quit()  # safe even if pygame was never initialised
    logging.flush()

    # properly shutdown ioHub server
    from psychopy.iohub.client import ioHubConnection

    if ioHubConnection.ACTIVE_CONNECTION:
        ioHubConnection.ACTIVE_CONNECTION.quit()

    for thisThread in threading.enumerate():
        if hasattr(thisThread, 'stop') and hasattr(thisThread, 'running'):
            # this is one of our event threads - kill it and wait for success
            thisThread.stop()
            while thisThread.running == 0:
                pass  # wait until it has properly finished polling

ball = visual.Circle(win, 
                    pos=(0,0), 
                    radius=0.03,
                    fillColor='white',
                    lineColor='white',
                    lineWidth=3)

ball.size *= scale

def calculate_ball_position(circle_reference_position, activation, ball_x_position, ball_y_position, outlier):
    # New cursor position (of ball) will be dot product of position (negative if DMN, positive if CEN) and activity (always positive)
    cursor_position = np.dot(circle_reference_position, activation)

    # only update ball position if the PDA metric isn't an outlier
    if not outlier:
        # The position of the target circle cumulatively adds the scaled cursor position on each frame
        ball_y_position =ball_y_position+ (np.real(cursor_position) * (scale_factor_z2pixels/internal_scaler) / tr_to_frame_ratio) 
        ball_x_position=ball_x_position+ (np.imag(cursor_position) * scale_factor_z2pixels/internal_scaler / tr_to_frame_ratio )
    
    ball_position=(ball_x_position,ball_y_position)
    #print("Ball position:", ball_position)
    return(ball_position)    


instruct_text = visual.TextStim(win=win, ori=0, name='instruct_text',
    text=u'replace me', 
    pos=[0, 0], height=0.06, wrapWidth=1.2,
    color=u'white', colorSpace='rgb', opacity=1,
    depth=0.0)

# Initialize components for Routine "finish"
finishClock = core.Clock()
thank_you_end_run_text = visual.TextStim(win=win, ori=0, name='thank_you_end_run_text',
    text=u'thank you!',    
    pos=[0, 0], height=0.1, wrapWidth=None,
    color=u'white', colorSpace='rgb', opacity=1,
    depth=0.0)

# Create some handy timers
globalClock = core.Clock()  # to track the time since experiment started
routineTimer = core.CountdownTimer()  # to track time remaining of each (non-slip) routine 

no_feedback_run1_text = f"Next, you will get to continue the Mindful Describing practice you just learned.\
    \n\nBefore, you mentioned using your {expInfo['anchor']} as an anchor for your Describing Practice. \
Try to continue using this as your anchor, but it is also okay to switch anytime.\
\n\nYou will see 2 circles with a white ball in the middle, but they won’t move for now."

ready_text="You will see the plus sign (+) for 30 seconds at the start. \
Whenever you see the plus +,  please don’t practice Describing – just relax.\
\n\nOnce the circles appear, please start the Describing practice. \
This practice will last 2.5 min." 

feedback_run1_text1 = "Great job! Now, you’ll get to continue your Mindful Describing  with some feedback based on your actual brain activity to help your practice! \
\n\nYou will see the 2 circles and white ball again. \
When the white ball moves up towards the top yellow circle, this means you are in a mindful brain state with your Describing practice. \
\nIf the ball reaches either of the circles, it will move back to the center."

feedback_run1_text2 = "Try to focus mostly on the Mindful Describing Practice by being aware of your sensations from moment to moment and silently making a note in your mind. \
\n\nYou can check the screen every once in a while to see where the ball is going." 

feedback_later_runs_text = "Great job! Next, you’ll get to practice Mindful Describing for another 2.5min with more brain feedback from the ball. \
\n\nWhen the ball moves upwards, that corresponds to the Describing Practice."

no_feedback_later_runs_text = "Great job! Next, you’ll get to practice Describing for another 2.5min. \
\nThis time the ball and circles will not move, so you don’t need to check them."

# Depending on whether feedback is offered/which run it is -- show different instruction slides
if expInfo['feedback_on'] == "No Feedback":
    if int(expInfo['run']) == 1: 
        instruction_slide_list = [no_feedback_run1_text, ready_text]
    else:
        instruction_slide_list = [no_feedback_later_runs_text, ready_text]
elif expInfo['feedback_on'] == 'Feedback':
    if int(expInfo['run']) == 1: 
        instruction_slide_list = [feedback_run1_text1, feedback_run1_text2, ready_text]
    else:
        instruction_slide_list = [feedback_later_runs_text, ready_text]


for instructions_slide in instruction_slide_list:
    instruct_text.setText(instructions_slide)
    run_instructions(instruct_text)


 #murfi communicator
# if not (SHAM and expInfo['feedback_on'] == 'Feedback'):
from murfi_activation_communicator import MurfiActivationCommunicator

# Assign to roi_names_list see above for randomization

#roi_names_list = ['cen', 'dmn']#, 'mpfc','wm']
# REPLACE THIS IP WITH THE MURFI COMPUTER'S IP 192.168.2.5
# EXTERNAL STIMULUS COMPUTER IS 196.168.2.6
# FOR RUNNING ALL ON THE SYSTEM76 COMPUTER USE INTERNAL IP 127.0.0.1

communicator = MurfiActivationCommunicator('127.0.0.1',
                                               15001, 210,
                                               roi_names_list,expInfo['tr'],murfi_FAKE)
print ("murfi communicator ok")

thisExp.addData('temporal_resolution', expInfo['tr'])


#------Prepare to start Routine "trigger"-------
t = 0
triggerClock.reset()  # clock 
frameN = -1
# update component parameters for each repeat
key_resp_3 = event.BuilderKeyResponse()  # create an object of type KeyResponse
key_resp_3.status = NOT_STARTED
# keep track of which components have finished
triggerComponents = []
triggerComponents.append(waiting_for_trigger_text)
triggerComponents.append(key_resp_3)
for thisComponent in triggerComponents:
    if hasattr(thisComponent, 'status'):
        thisComponent.status = NOT_STARTED

#-------Start Routine "trigger"-------
continueRoutine = True
while continueRoutine:
    # get current time
    t = triggerClock.getTime()
    frameN = frameN + 1  # number of completed frames (so 0 is the first frame)
    # update/draw components on each frame
    
    # *waiting_for_trigger_text* updates
    if t >= 0.0 and waiting_for_trigger_text.status == NOT_STARTED:
        # keep track of start time/frame for later
        waiting_for_trigger_text.tStart = t  # underestimates by a little under one frame
        waiting_for_trigger_text.frameNStart = frameN  # exact frame index
        waiting_for_trigger_text.setAutoDraw(True)
    
    # *key_resp_3* updates
    if t >= 0.0 and key_resp_3.status == NOT_STARTED:
        # keep track of start time/frame for later
        key_resp_3.tStart = t  # underestimates by a little under one frame
        key_resp_3.frameNStart = frameN  # exact frame index
        key_resp_3.status = STARTED
        # keyboard checking is just starting
        key_resp_3.clock.reset()  # now t=0
        event.clearEvents(eventType='keyboard')
    if key_resp_3.status == STARTED:
        theseKeys = event.getKeys(keyList=['t','+','5', 5, 'equal', 'shift+=','num_equal','='])
        
        # check for quit:
        if "escape" in theseKeys:
            endExpNow = True
        if len(theseKeys) > 0:  # at least one key was pressed
            key_resp_3.keys = theseKeys[-1]  # just the last key pressed
            key_resp_3.rt = key_resp_3.clock.getTime()
            # a response ends the routine
            continueRoutine = False

            # reset trigger clock -- now it is keeping track of time relative to trigger!
            triggerClock.reset()
    
    # check if all components have finished
    if not continueRoutine:  # a component has requested a forced-end of Routine
        routineTimer.reset()  # if we abort early the non-slip timer needs reset
        break
    continueRoutine = False  # will revert to True if at least one component still running
    for thisComponent in triggerComponents:
        if hasattr(thisComponent, "status") and thisComponent.status != FINISHED:
            continueRoutine = True
            break  # at least one component has not yet finished
    
    # check for quit (the Esc key)
    if endExpNow or event.getKeys(keyList=["escape"]):
        core.quit()
    
    # refresh the screen
    if continueRoutine:  # don't flip if this routine is over or we'll get a blank screen
        win.flip()
    else:  # this Routine was not non-slip safe so reset non-slip timer
        routineTimer.reset()

#-------Ending Routine "trigger"-------
for thisComponent in triggerComponents:
    if hasattr(thisComponent, "setAutoDraw"):
        thisComponent.setAutoDraw(False)
# check responses
if key_resp_3.keys in ['', [], None]:  # No response was made
   key_resp_3.keys=None
# store data for thisExp (ExperimentHandler)
thisExp.addData('key_resp_3.keys',key_resp_3.keys)
if key_resp_3.keys != None:  # we had a response
    thisExp.addData('key_resp_3.rt', key_resp_3.rt)
thisExp.nextEntry()

# BASELINE: wait for 30s before delivering feedback
#------Prepare to start Routine "baseline"-------
t = 0
baselineClock.reset()  # clock 
frameN = -1
frame = 0
routineTimer = core.CountdownTimer(BaseLineTime)
# update component parameters for each repeat
# keep track of which components have finished
baselineComponents = []
baselineComponents.append(text_2)
for thisComponent in baselineComponents:
    if hasattr(thisComponent, 'status'):
        thisComponent.status = NOT_STARTED

#-------Start Routine "baseline"-------
continueRoutine = True
print("starting baseline")

# Ensure header is written once
csv_path = filename + '_roi_outputs.csv'
file_exists = os.path.isfile(csv_path)

# Define group-specific labels once
if group == '1':
    pda_label = 'cen_dmn_pda'
    cumulative_hit_labels = ['cen_cumulative_hits', 'dmn_cumulative_hits']
elif group == '0':
    pda_label = 'smcl_smcr_pda'
    cumulative_hit_labels = ['smcl_cumulative_hits', 'smcr_cumulative_hits']
else:
    pda_label = 'unknown_pda'
    cumulative_hit_labels = ['roi1_cumulative_hits', 'roi2_cumulative_hits']

csv_header = [
    'volume', 'scale_factor', 'time', 'time_plus_1.2',
    'smcl', 'smcr', 'cen', 'dmn',
    'stage', *cumulative_hit_labels,
    'num_pda_outliers', pda_label,
    'ball_y_position', 'top_circle_y_position', 'bottom_circle_y_position'
]

# Open file and write header if needed
if not file_exists or os.stat(csv_path).st_size == 0:
    with open(csv_path, 'a') as csvfile:
        stim_writer = csv.writer(csvfile, delimiter=',', quotechar='|', quoting=csv.QUOTE_MINIMAL)
        stim_writer.writerow(csv_header)

# Start baseline frame loop
while continueRoutine and routineTimer.getTime() > 0:
    communicator.update()
    roi_raw_activations = []

    # Try to collect ROI activations
    try:
        for i in range(len(roi_names_list)):
            roi_raw_i = communicator.get_roi_activation(roi_names_list[i], frame)
            roi_raw_activations.append(roi_raw_i)
    except:
        print(f"Did not get data for frame {frame}")
        roi_raw_activations = [np.nan for _ in roi_names_list]

    # Skip frame if any values are missing
    if any(np.isnan(val) for val in roi_raw_activations):
        continue

    # --- CSV ROIs: Collect all 4 ROI activations for output file ---
    roi_all_for_csv = []
    for roi_name in ['smcl', 'smcr', 'cen', 'dmn']:
        try:
            val = communicator.get_roi_activation(roi_name, frame)
        except Exception as e:
            print(f"Warning: Could not get activation for {roi_name} at frame {frame}. Error: {e}")
            val = np.nan
        roi_all_for_csv.append(val)

    # Determine which ROIs were used in feedback (even if randomized)
    # --- Calculate PDA using actual feedback ROI order ---
    roi1_name, roi2_name = roi_names_list[0], roi_names_list[1]  # active pair
    pda_label = f"{roi1_name}_{roi2_name}_pda"
    roi_full_order = ['smcl', 'smcr', 'cen', 'dmn']

    try:
        val1 = roi_raw_activations[roi_full_order.index(roi1_name)]
        val2 = roi_raw_activations[roi_full_order.index(roi2_name)]
        pda_val = val1 - val2
    except Exception as e:
        print(f"⚠️ PDA calc failed at frame {frame}: {e}")
        pda_val = np.nan

    # Write row to file
    with open(csv_path, 'a') as csvfile:
        stim_writer = csv.writer(csvfile, delimiter=',', quotechar='|', quoting=csv.QUOTE_MINIMAL)
        stim_writer.writerow([
    frame,
    expInfo['scale_factor'],
    triggerClock.getTime(),
    triggerClock.getTime() + 1.2,
    *roi_raw_activations,
    'baseline',
    0, 0,  # hits
    np.nan,  # outliers
    pda_val,
    pda_label,  # <- dynamic label
    ball.pos[1],
    target_circles[0].pos[1],
    target_circles[1].pos[1]
])


    frame += 1



    t = baselineClock.getTime()
    frameN = frameN + 1  # number of completed frames (so 0 is the first frame)
    # update/draw components on each frame
    
    # *text_2* updates
    if t >= 0.0 and text_2.status == NOT_STARTED:
        # keep track of start time/frame for later
        text_2.tStart = t  # underestimates by a little under one frame
        text_2.frameNStart = frameN  # exact frame index
        text_2.setAutoDraw(True)
        text_relax.setAutoDraw(True)
    if text_2.status == STARTED and t >= (0.0 + (BaseLineTime-win.monitorFramePeriod*0.75)): #most of one frame period left
        pass
        
    
    # check if all components have finished
    if not continueRoutine:  # a component has requested a forced-end of Routine
        routineTimer.reset()  # if we abort early the non-slip timer needs reset
        break
    continueRoutine = False  # will revert to True if at least one component still running
    for thisComponent in baselineComponents:
        if hasattr(thisComponent, "status") and thisComponent.status != FINISHED:
            continueRoutine = True
            break  # at least one component has not yet finished
    
    # check for quit (the Esc key)
    if endExpNow or event.getKeys(keyList=["escape"]):
        core.quit()
    
    # refresh the screen
    if continueRoutine:  # don't flip if this routine is over or we'll get a blank screen
        win.flip()

#-------Ending Routine "baseline"-------
text_2.setAutoDraw(False)
text_relax.setAutoDraw(False)
for thisComponent in baselineComponents:
    if hasattr(thisComponent, "setAutoDraw"):
        thisComponent.setAutoDraw(False)
        
        

#------Prepare to start Routine "feedback"-------
t = 0
feedbackClock.reset()  # clock 
frameN = -1
# update component parameters for each repeat
subject_key_target = event.BuilderKeyResponse()  # create an object of type KeyResponse
subject_key_target.status = NOT_STARTED
subject_key_reset = event.BuilderKeyResponse()  # create an object of type KeyResponse
subject_key_reset.status = NOT_STARTED
routineTimer = core.CountdownTimer(RUN_TIME)  # Create a new countdown timer with RUN_TIME seconds



# Initialize parameters before feedback
activity = 0
direction=0

# Draw initial stim positions
n_roi = roi_number_circles
for i in range(n_roi):
    target_circles[i].draw()
ball.draw()
win.flip()

pda_outlier=False
frame_data = []  # List to store all frame details




#-------Start Routine "feedback"-------
# initialize last_acquired_frame_time
last_acquired_frame_time = feedbackClock.getTime()
continueRoutine = True

# Loop keeps going until RUN_TIME is up
while continueRoutine and routineTimer.getTime() > 0:
    # get current time
    t = feedbackClock.getTime()
    run_stop_time=t
    frameN = frameN + 1  # number of completed frames (so 0 is the first frame)
    # update/draw components on each frame
    
    # *subject_key_target* updates
    if t >= 0.0 and subject_key_target.status == NOT_STARTED:
        # keep track of start time/frame for later
        subject_key_target.tStart = t  # underestimates by a little under one frame
        subject_key_target.frameNStart = frameN  # exact frame index
        subject_key_target.status = STARTED
        # keyboard checking is just starting
        subject_key_target.clock.reset()  # now t=0
        event.clearEvents(eventType='keyboard')
    if subject_key_target.status == STARTED:
        theseKeys = event.getKeys(keyList=['escape'])
        theseKeys_num=theseKeys

        # check for quit:
        if "escape" in theseKeys:
            endExpNow = True
        if len(theseKeys) > 0:  # at least one key was pressed
            subject_key_target.keys = theseKeys[-1]  # just the last key pressed
            subject_key_target.rt = subject_key_target.clock.getTime()
    
    # get updated data from MURFI    
    # get updated data from MURFI    
    communicator.update()

    # --- Feedback ROIs: Get just 2 for ball logic (e.g., ['smcl', 'smcr']) ---
    roi_raw_activations = []  # for feedback display (ball movement)
    for i in range(n_roi):  # n_roi = 2, controlled by setup
        roi_raw_i = communicator.get_roi_activation(roi_names_list[i], frame)
        roi_raw_activations.append(roi_raw_i)

    roi_activities = roi_raw_activations  # used in direction / activity calculation

    # --- CSV ROIs: Collect all 4 ROI activations for output file ---
    roi_all_for_csv = []
    for roi_name in ['smcl', 'smcr', 'cen', 'dmn']:
        try:
            val = communicator.get_roi_activation(roi_name, frame)
        except Exception as e:
            print(f"Warning: Could not get activation for {roi_name} at frame {frame}. Error: {e}")
            val = np.nan
        roi_all_for_csv.append(val)

       
    '''
    Check for any missing values (nan) from MURFI on the current frame. If there is a nan value, this most likely
    indicates that data hasn't been acquired yet for the current volume. In this case, continue, and keep trying to acquire
    roi_raw_activations from MURFI (without advancing the frame). This will happen several times for each volume before the data 
    for the next volume are available. 
    '''
    if np.isnan(roi_raw_activations[0]) or np.isnan(roi_raw_activations[1]):
        # get timestamp
        non_new_data_time=feedbackClock.getTime()

        # if time is more than 10s after last_acquired_frame_time, quit task (this means no more data is flowing in)
        if non_new_data_time - last_acquired_frame_time > 10:
            print('ERROR: NO DATA ARRIVING FROM MURFI! Is this a MoCo issue?')
            print(f'quit at {non_new_data_time} since there were no new frames since {last_acquired_frame_time}')
            continueRoutine=False
 

    # a list of [CEN, DMN] for the current frame
    else:
        roi_activities=roi_raw_activations

        # get a timestamp for last_acquired_frame_time
        last_acquired_frame_time = feedbackClock.getTime()
        print(last_acquired_frame_time)

        if np.nanmax(np.abs(roi_activities)) > expInfo['pda_outlier_threshold']:
            pda_outlier=True
            num_pda_outliers+=1
        else:
            pda_outlier=False

        print('time: ', routineTimer.getTime())
        print ("got feedback at frame : ",  frame, roi_raw_activations, roi_names_list)
        
        '''
        Loop through ROIs. Depending on which one has higher activity, change direction parameter 
        1 - upwards (when CEN higher)
        -1 = downwards (when DMN higher)
        '''
        for i in range(n_roi):
            target_circles[i].fillColor=None
            # for each ROI, look for the index -- see whether that ROI has the highest activity
            if roi_activities.index(np.nanmax(roi_activities))==i and np.nanmean(roi_activities)!=0:
                # Activity=absolute difference between ROI activations (always positive)
                activity=abs(np.nanmax(roi_activities)-(np.nanmin(roi_activities)))/10
                print ("activity",activity, " roi_activities",roi_activities)

                # activity will always be positive (PDA)
                # positions refers to either CEN position positions[0] or DMN position positions[1]
                print('Circle positions:', target_circles[0].pos[1], target_circles[1].pos[1])
                print ("direction -->", roi_names_list[i],'or', roi_names_list[i+2])
                print (roi_names_list[0],'or',roi_names_list[2],"hits: ",hit_counter[0], '   ', roi_names_list[1],'or',roi_names_list[3],"hits: ",hit_counter[1])
                direction = positions[i]

            # if the ball has passed the middle of either target circle, put position back to 0
            if further_than_circles(position=i, 
                circle_center=target_circles[i].pos[1], 
                ball_center=ball.pos[1]):

                # increment hig count
                hit_counter[i]=hit_counter[i]+1
                print('HIT', roi_names_list[i],"or",roi_names_list[i+2])
                ball.pos = (0,0)

                # for each hit, position of target circle moves away from the middle (up to a point)
                if circles_move_with_hits:
                    if np.abs(target_circles[i].pos[1]) + target_circles[i].radius + 0.1 < 1:
                        target_circles[i].pos=((target_circles[i].pos[0]*1.1), (target_circles[i].pos[1]*1.1))
                if circle_radius_shrink_with_hits:
                    target_circles[i].radius = np.maximum(target_circles[i].radius*.9, 0.03)

                target_circles[i].fillColor='white'

        # Compute PDA value and dynamic label
        roi1_name, roi2_name = roi_names_list[0], roi_names_list[1]
        pda_label = f"{roi1_name}_{roi2_name}_pda"
        roi_full_order = ['smcl', 'smcr', 'cen', 'dmn']

        try:
            val1 = roi_all_for_csv[roi_full_order.index(roi1_name)]
            val2 = roi_all_for_csv[roi_full_order.index(roi2_name)]
            pda_val = val1 - val2
        except Exception as e:
            print(f"⚠️ PDA calc failed at frame {frame}: {e}")
            pda_val = np.nan



        pda_label = f"{roi1_name}_{roi2_name}_pda"


        # Save info to outfile for each volume       
        with open(filename + '_roi_outputs.csv', 'a') as csvfile:
            stim_writer = csv.writer(csvfile, delimiter=',', quotechar='|', quoting=csv.QUOTE_MINIMAL)
            stim_writer.writerow([
	    frame,
	    expInfo['scale_factor'],
	    triggerClock.getTime(),
	    triggerClock.getTime() + 1.2,
	    *roi_all_for_csv,
	    'feedback',
	    hit_counter[0],
	    hit_counter[1],
	    num_pda_outliers,
	    pda_val,
	    pda_label,  # NEW
	    ball.pos[1],
	    target_circles[0].pos[1],
	    target_circles[1].pos[1]
	])


        # Increment the frame
        frame += 1
    
    # calculate next ball position
    pause_ball_movement=False
    for i in range(n_roi):
        if further_than_circles(position=i, 
                    circle_center=target_circles[i].pos[1], 
                    ball_center=ball.pos[1]):
            pause_ball_movement=True

    if not pause_ball_movement:
        ball.pos = calculate_ball_position(circle_reference_position=direction, activation=activity, ball_x_position=ball.pos[0], ball_y_position=ball.pos[1], outlier=pda_outlier)             

    # Draw stimuli (if on feedback mode)
    if expInfo['feedback_on'] == 'Feedback':
        for i in range(n_roi):
            target_circles[i].draw()
        ball.draw()

        # flip window
        win.flip()

        frame_info = {}
        # Store frame data including details for all circles and the ball
        # Save ball attributes as before
        frame_info["time"] = globalClock.getTime()
        frame_info["ball_x"] = ball.pos[0]
        frame_info["ball_y"] = ball.pos[1]
        frame_info["ball_radius"] = ball.radius

        # Here, if ball.fillColor is a string, save it as is:
        if ball.fillColor is None:
            ball_fill = [-1, -1, -1]  # black
        else:
            ball_fill = ball.fillColor
        frame_info["ball_color_r"] = ball_fill[0]
        frame_info["ball_color_g"] = ball_fill[1]
        frame_info["ball_color_b"] = ball_fill[2]

        # Save details for each of the three ROIs (target circles)
        for i, roi in enumerate(target_circles):
            frame_info[f"roi{i + 1}_x"] = roi.pos[0]
            frame_info[f"roi{i + 1}_y"] = roi.pos[1]
            frame_info[f"roi{i + 1}_radius"] = roi.radius
            # Fill Color
            if roi.fillColor is None:
                # Force black for 'no fill' to ensure no mid-gray
                fill_color = [-1, -1, -1]
            else:
                fill_color = roi.fillColor

            # If fill_color is [0,0,0] for some reason, also force it to black
            if (fill_color[0] == 0 and fill_color[1] == 0 and fill_color[2] == 0):
                fill_color = [-1, -1, -1]

            frame_info[f"roi{i + 1}_color_r"] = fill_color[0]
            frame_info[f"roi{i + 1}_color_g"] = fill_color[1]
            frame_info[f"roi{i + 1}_color_b"] = fill_color[2]

            # Line Color
            line_color = roi.lineColor
            frame_info[f"roi{i + 1}_lineColor_r"] = line_color[0]
            frame_info[f"roi{i + 1}_lineColor_g"] = line_color[1]
            frame_info[f"roi{i + 1}_lineColor_b"] = line_color[2]

        frame_data.append(frame_info)

    # quit if escape pressed
    if endExpNow or event.getKeys(keyList=["escape"]):
        core.quit()
    

#END OF FEEDBACK LOOP
# If feedback was displayed, save frame data
if expInfo['feedback_on'] == 'Feedback':
    df = pd.DataFrame(frame_data)  # Convert list to DataFrame
    csv_filename = filename+'_frames.csv'
    df.to_csv(csv_filename, index=False)  # Save CSV without index
    print(f"Feedback frames saved to {csv_filename}")

#------Prepare to start Routine "baseline"-------
t = 0
baselineClock.reset()  # clock 
frameN = -1
routineTimer = core.CountdownTimer(1.00000)  # Create a new countdown timer 
# update component parameters for each repeat
# keep track of which components have finished
baselineComponents = []
baselineComponents.append(text_2)
for thisComponent in baselineComponents:
    if hasattr(thisComponent, 'status'):
        thisComponent.status = NOT_STARTED

#-------Start Routine "baseline"-------
continueRoutine = True
while continueRoutine and routineTimer.getTime() > 0:
    # get current time
    t = baselineClock.getTime()
    frameN = frameN + 1  # number of completed frames (so 0 is the first frame)
    # update/draw components on each frame

    # *text_2* updates
    if t >= 0.0 and text_2.status == NOT_STARTED:
        # keep track of start time/frame for later
        text_2.tStart = t  # underestimates by a little under one frame
        text_2.frameNStart = frameN  # exact frame index
        text_2.setAutoDraw(True)
    if text_2.status == STARTED and t >= (0.0 + (1-win.monitorFramePeriod*0.75)): #most of one frame period left
        text_2.setAutoDraw(False)

# check if all components have finished
    if not continueRoutine:  # a component has requested a forced-end of Routine
        routineTimer.reset()  # if we abort early the non-slip timer needs reset
        break
    continueRoutine = False  # will revert to True if at least one component still running
    for thisComponent in baselineComponents:
        if hasattr(thisComponent, "status") and thisComponent.status != FINISHED:
            continueRoutine = True
            break  # at least one component has not yet finished

# check for quit (the Esc key)
    if endExpNow or event.getKeys(keyList=["escape"]):
        core.quit()

# refresh the screen
    if continueRoutine:  # don't flip if this routine is over or we'll get a blank screen
        win.flip()

#-------Ending Routine "baseline"-------
for thisComponent in baselineComponents:
    if hasattr(thisComponent, "setAutoDraw"):
        thisComponent.setAutoDraw(False)
    
  
 
#------Prepare to start Routine "finish"-------
t = 0
finishClock.reset()  # clock 
frameN = -1
# update component parameters for each repeat
# keep track of which components have finished
finishComponents = []
finishComponents.append(thank_you_end_run_text)
for thisComponent in finishComponents:
    if hasattr(thisComponent, 'status'):
        thisComponent.status = NOT_STARTED

# Ask slider questions only if halfway through the run or more (60s into feedback)
if run_stop_time >= 60:
    slider_instruction.draw()
    win.flip()
    wait_for_keypress(key_list=[right_button, left_button, enter_button])

    run_slider(question_text='How often were you using the Mindful Describing practice?',
                    left_label='Never', right_label='Always')
    run_slider(question_text='How often did you check the position of the ball?',
                    left_label='Never', right_label='All the time')
    run_slider(question_text='How difficult was it to apply Mindful Describing?',
                    left_label='Not at all', right_label='Very Difficult')
    run_slider(question_text='How calm do you feel right now?',
                    left_label='Not at all', right_label='Very calm')
    if expInfo['run'] == '5' and expInfo['feedback_on'] == 'Feedback':  # last feedback run
        run_slider(question_text='The ball seemed to move up while I was practicing Mindful Describing',
                   left_label='False', right_label='True')
        run_slider(question_text='The ball seemed to move down while my mind was wandering.',
                   left_label='False', right_label='True')
        run_slider(question_text='The ball seemed to move down while I was trying to control it.',
                   left_label='False', right_label='True')
else:
    with open(run_questions_file, 'a') as csvfile:
            stim_writer = csv.writer(csvfile, delimiter=',', quotechar='|', quoting=csv.QUOTE_MINIMAL)
            stim_writer.writerow([expInfo['participant'], expInfo['run'], expInfo['feedback_on'],
                                  'How often were you using the Mindful Describing practice?', np.nan, np.nan])

    with open(run_questions_file, 'a') as csvfile:
            stim_writer = csv.writer(csvfile, delimiter=',', quotechar='|', quoting=csv.QUOTE_MINIMAL)
            stim_writer.writerow([expInfo['participant'], expInfo['run'], expInfo['feedback_on'],
                                  'How often did you check the position of the ball?', np.nan, np.nan])  
    with open(run_questions_file, 'a') as csvfile:
            stim_writer = csv.writer(csvfile, delimiter=',', quotechar='|', quoting=csv.QUOTE_MINIMAL)
            stim_writer.writerow([expInfo['participant'], expInfo['run'], expInfo['feedback_on'],
                                  'How difficult was it to apply Mindful Describing', np.nan, np.nan])

    with open(run_questions_file, 'a') as csvfile:
            stim_writer = csv.writer(csvfile, delimiter=',', quotechar='|', quoting=csv.QUOTE_MINIMAL)
            stim_writer.writerow([expInfo['participant'], expInfo['run'], expInfo['feedback_on'],
                                  'How calm do you feel right now?', np.nan, np.nan])

    if expInfo['run'] == '5' and expInfo['feedback_on'] == 'Feedback':  # last feedback run
        with open(run_questions_file, 'a') as csvfile:
            stim_writer = csv.writer(csvfile, delimiter=',', quotechar='|', quoting=csv.QUOTE_MINIMAL)
            stim_writer.writerow([expInfo['participant'], expInfo['run'], expInfo['feedback_on'],
                                  'The ball seemed to move up while I was practicing Mindful Describing', np.nan,
                                  np.nan])

        with open(run_questions_file, 'a') as csvfile:
            stim_writer = csv.writer(csvfile, delimiter=',', quotechar='|', quoting=csv.QUOTE_MINIMAL)
            stim_writer.writerow([expInfo['participant'], expInfo['run'], expInfo['feedback_on'],
                                  'The ball seemed to move down while my mind was wandering.', np.nan, np.nan])

        with open(run_questions_file, 'a') as csvfile:
            stim_writer = csv.writer(csvfile, delimiter=',', quotechar='|', quoting=csv.QUOTE_MINIMAL)
            stim_writer.writerow([expInfo['participant'], expInfo['run'], expInfo['feedback_on'],
                                  'The ball seemed to move down while I was trying to control it.', np.nan, np.nan])


# Convert csv output to BIDS-format tsv
convert_balltask_csv_to_bids(
    infile=f"{filename}_roi_outputs.csv",
    filename_prefix=filename_prefix)

# display ending text and close window
thank_you_end_run_text.draw()
win.flip()
core.wait(3)
win.close()


# Set variables for the next run
if expInfo['run'] == '1' and expInfo['feedback_on'] == 'No Feedback':
    next_run =1
    next_feedback= 'Feedback'
elif expInfo['run'] == '2' and expInfo['feedback_on'] == 'No Feedback': 
    next_run =6
    next_feedback = 'Feedback'
elif expInfo['run'] == '5':
    next_run =2
    next_feedback='No'
elif expInfo['run'] == '10':
    next_run =3
    next_feedback='No'
else:
    next_run = int(expInfo['run']) + 1
    next_feedback='Feedback'

next_participant=expInfo['participant']
anchor = expInfo['anchor']
next_feedback_condition = expInfo['feedback_condition']

# Shut down psychopy before starting next run
quit_psychopy()


if expInfo['feedback_condition'] == '15min':
    if next_run < 6:
        subprocess.Popen(["bash", "reopen_balltask_mgh.sh", str(next_participant), str(next_run),
            str(next_feedback), str(next_feedback_condition), str(anchor)])
elif expInfo['feedback_condition'] == '30min':
    subprocess.Popen(["bash", "reopen_balltask_mgh.sh", str(next_participant), str(next_run),
        str(next_feedback), str(next_feedback_condition), str(anchor)])

# Quit python
sys.exit('Done with run')
