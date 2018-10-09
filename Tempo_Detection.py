import numpy as np
import scipy
#%matplotlib inline
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

#This part is a bit change come from the Librosa source
# This is how to derive the Dynamic Tempogram
def tempo(y=None, sr=22050, onset_envelope=None, hop_length=512, start_bpm=120,
          std_bpm=1.0, ac_size=8.0, max_tempo=320.0, aggregate=np.mean):
    if start_bpm <= 0:
        raise ParameterError('start_bpm must be strictly positive')

    # Convert an array of size 1 to its scalar equivalent.
    win_length = np.asscalar(core.time_to_frames(ac_size, sr=sr, hop_length=hop_length))
    #print(win_length)
    # Compute a tempogram:
    tg = tempogram(y=y, sr=sr, onset_envelope=onset_envelope, hop_length=hop_length, win_length=win_length)

    # Eventually, we want this to work for time-varying tempo
    if aggregate is not None:
        tg = aggregate(tg, axis=1, keepdims=True)

    # Get the BPM values for each bin, skipping the 0-lag bin?
    bpms = core.tempo_frequencies(tg.shape[0], hop_length=hop_length, sr=sr)

    # Weight the autocorrelation by a log-normal distribution
    prior = np.exp(-0.5 * ((np.log2(bpms) - np.log2(start_bpm)) / std_bpm) ** 2)

    # Kill everything above the max tempo
    if max_tempo is not None:
        max_idx = np.argmax(bpms < max_tempo)
        prior[:max_idx] = 0

    # Really, instead of multiplying by the prior, we should set up a
    # probabilistic model for tempo and add log-probabilities.
    # This would give us a chance to recover from null signals and
    # rely on the prior.
    # it would also make time aggregation much more natural

    # Get the maximum, weighted by the prior
    best_period = np.argmax(tg * prior[:, np.newaxis], axis=0)

    tempi = bpms[best_period]
    # Wherever the best tempo is index 0, return start_bpm
    tempi[best_period == 0] = start_bpm
    return tempi

#This part is designed for get the main position of the Dynamic special time
def getdynamictempo():
    #load a music 
    y, sr = librosa.load('challenge/challenge_033_24768.wav')
    #choose the hop length 
    hop_length = 512
    # choose window length
    win_length=400

    #Get the Onset detection based on the spectral novelty function
    onset_envelope = librosa.onset.onset_strength(y=y, sr=sr, hop_length=hop_length, n_fft=2048)
    #Get the whole dynamic function 
    dtempo = tempo(y=y, onset_envelope=onset_envelope, sr=sr, aggregate=None)
    #Change the frame to the time
    times = librosa.frames_to_time(np.arange(len(dtempo)))
    # Define the tempo value and special time value
    actual_tempo=[dtempo[0]]
    special_time=[]
    # tempoindex is defined as the index of the tempo
    for tempoindex in range(len(dtempo)):
        tempoindex = tempoindex + 1
        if tempoindex < len(dtempo):
            if dtempo[tempoindex] != dtempo[tempoindex-1] :
                # this part is used for getting the special tempo position and change to the time
                actual_tempo.append(dtempo[tempoindex])
                special_time.append(librosa.frames_to_time(tempoindex-1))
    #this is try to print the special tempo and time
    print(actual_tempo)
    print(special_time)
    # return the critical point of tempo and time 
    return(y, sr, actual_tempo, special_time)
