import numpy as np
import scipy
%matplotlib inline
import numpy, scipy, matplotlib.pyplot as plt, IPython.display as ipd
import librosa, librosa.display
from ipywidgets import interact

from librosa import cache
from librosa import core
from librosa import onset
from librosa import util
from librosa.feature import tempogram
from librosa.util.exceptions import ParameterError
import mir_eval

__all__ = ['beat_track', 'tempo']

#Section 1:Basic Function
def evaluation(reference_beats,beat_times):    
    f_measure = mir_eval.beat.f_measure(reference_beats,beat_times)
    cemgil_score, cemgil_max = mir_eval.beat.cemgil(reference_beats, beat_times)
    goto_score = mir_eval.beat.goto(reference_beats, beat_times)
    information_gain = mir_eval.beat.information_gain(reference_beats, beat_times)
    
    print('f_measure', f_measure)
    print('cemgil_score', cemgil_score)
    print('goto_score', goto_score)
    print('information_gain', information_gain)
    #print('p_score', p_score)

#Section 2:Dynamic Programming evaluation
# evalutiopn for the Dynamic Programming
x, sr = librosa.load('challenge_pieces/challenge_033_24768.wav')
ipd.Audio(x, rate=sr)
tempo1, beat_times = beat_track(x, sr=sr,start_bpm=60, units='time')
reference_beats = mir_eval.io.load_events('challenge_txt/challenge_033_24768.txt')
#get the evaluation result
evaluation(reference_beats,beat_times)

##Section 3:Checking the Onset Detection
###oneset strength check
beat_times =[0.37, 2.07, 2.32, 2.86, 3.16, 4.76, 5.27, 5.83, 6.34, 7.38, 8.45, 9.52, 10.57, 10.84, 11.63, 12.68, 13.75, 14.79, 15.02, 16.9, 17.44, 17.69, 17.97, 19.04, 19.3, 20.06, 20.6, 21.11, 22.08, 22.52, 23.17, 24.22, 25.26, 26.03, 27.35, 27.59, 28.37, 28.58, 29.4]
beat_times = np.array(beat_times)
x, sr = librosa.load('challenge_pieces/challenge_033_24768.wav')
spectral_novelty = librosa.onset.onset_strength(x, sr=sr)
frames = numpy.arange(len(spectral_novelty))
t = librosa.frames_to_time(frames, sr=sr)
#print(spectral_novelty)
plt.figure(figsize=(15, 4))
plt.plot(t, spectral_novelty, 'r-')
plt.vlines(beat_times, 0, 16, color='k')
plt.vlines(reference_beats, 0, 16, color='c',linestyles = "dashed")
plt.xlim(0, t.max())
plt.xlabel('Time (sec)')
plt.legend(('Spectral Novelty',))

##Section 4:Dynamic Tempo Plot Check
hop_length = 512

plt.figure()
onset_env = librosa.onset.onset_strength(x, sr=sr, hop_length=hop_length, n_fft=2048)
tempogram = librosa.feature.tempogram(onset_envelope=onset_env, sr=sr, hop_length=hop_length, win_length=400)
librosa.display.specshow(tempogram, sr=sr, hop_length=hop_length, x_axis='time', y_axis='tempo')
dtempo = librosa.beat.tempo(onset_envelope=onset_env, sr=sr, aggregate=None)
print(max(librosa.frames_to_time(np.arange(len(dtempo)))))
#print(dtempo)
plt.plot(librosa.frames_to_time(np.arange(len(dtempo))), dtempo,color='w', linewidth=1.5, label='Tempo estimate')
plt.title('Dynamic tempo estimation')
plt.legend(frameon=True, framealpha=0.75)

