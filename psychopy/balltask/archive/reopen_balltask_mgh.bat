call %HOMEPATH%\anaconda3\Library\bin\conda.bat activate psychopy
set participant=%1
set run=%2
set feedback_on=%3
set condition=%4
set protocol=%5
set anchor=%6
python rt-network_feedback_mgh.py %participant% %run% %feedback_on% %condition% %protocol% %anchor% 
