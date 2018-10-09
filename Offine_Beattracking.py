import numpy as np
import scipy
from tempodetect import getdynamictempo
from get_best import best_estimate
from get_best import best_estimate1
import numpy, scipy, matplotlib.pyplot as plt, IPython.display as ipd
import librosa, librosa.display
from librosa import cache
from librosa import core
from librosa import onset
from librosa import util
from librosa.feature import tempogram
from librosa.util.exceptions import ParameterError
import mir_eval
import heapq

frame_f = []
time_f = []

def find_location(spectral_novelty,temporeal, special_Single_left,special_Single_right,frame_f=frame_f,time_f = time_f):
    time_check = []
    # define a frame list
    # in one short time the around beat number
    number_period = round(float(temporeal / 60 * (special_Single_right-special_Single_left) ))
    # convert time to the frames
    frames0 = librosa.core.time_to_frames(special_Single_left)
     # convert time to the frames
    frames = librosa.core.time_to_frames(special_Single_right)
   
    # this is used for get the best 5 positions
    best_location = heapq.nlargest(number_period, spectral_novelty[frames0:frames])

    # get the beat time
    for frame in range(frames0, frames):
        if spectral_novelty[frame] in best_location:
            frame_f.append(frame)
            t0 = librosa.frames_to_time(frame, sr=sr)
            time_check.append(t0)
    # This part is one simple idea for add missing beat position
            #if len(time_f) > 1:
                #if t0-time_f[len(time_f)-2] > 0.1:
            #time_f.append(round(t0, 2))
    # add the beat time into the time list
    for i in range(len(time_check)):
        # add the first time
        if i==0:
            time_f.append(round(time_check[i],2))
        # add the after time
        if i > 0:           
            if time_check[i] - time_check[i - 1] > 0.1:
                time_f.append(round(time_check[i], 2))
    return(frame_f,time_f)


#main function for track the beats
for i in range(len(actual_tempo)):
    temporeal = actual_tempo[i]
    if i == 0:
        special_Single_left = float(0)
        special_Single_right = special_time[i]
    elif i > 0 and i < len(actual_tempo)-1:
        special_Single_left = special_time[i-1]
        special_Single_right = special_time[i]
    elif i == len(actual_tempo)-1:
        special_Single_left = special_time[i - 1]
        special_Single_right = float(len(y)/sr)
    (frame_f, time_f) = find_location(spectral_novelty, temporeal, special_Single_left,special_Single_right,frame_f=frame_f,time_f = time_f)
#print(frame_f)
print(time_f)



