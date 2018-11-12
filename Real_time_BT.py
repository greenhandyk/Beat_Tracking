import pyaudio
import numpy as np
import wave
import librosa, librosa.display
from librosa import util
import time
from multiprocessing import Process, Queue
import os, time, random
from tempodetect import tempo
from offline import find_location



# set up for basic data information
CHUNK = 2048
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 22500
sr = 22500
RECORD_SECONDS = 5
WAVE_OUTPUT_FILENAME = "output.wav"




# beat predict function
def beatevaluate(second_last_beat,last_beat):
    # use the basic beat presiction 
    t = last_beat
    last_beat = 2*float(last_beat)-float(second_last_beat)
    #return the second beat 
    second_last_beat = t
    # return the last and second last beat
    return(last_beat,second_last_beat)


# data read function
def dataread(q,CHUNK):
    # open a pyaudio channel
    p = pyaudio.PyAudio()
    stream = p.open(format=pyaudio.paInt16, channels=1, rate=22500, input=True, frames_per_buffer=CHUNK)
    # calculate the process time
    begin = time.time()
    print('begin', begin)
    # Choose 30 seconds as an example
    for i in range(0, int(22500.0 / CHUNK * 30.0)):
        # read data stream by stream
        data = stream.read(CHUNK)
        # use the queue to process the data
        q.put(data)
    # stop the stream
    stream.stop_stream()
    # close the stream
    stream.close()
    # close the terminal
    p.terminate()
    # calculate the time
    stop = time.time()
    
# data out function
def dataout(q):
    # create the frame and beat list to store the data
    frames = []
    beat_all=[0]
    #frames = np.array(frames)
    print(type(frames))
    # use for calculate the process clock
    account_clock =0
    # flag for design for Ture or False
    flag = True
    k=1

    while True:
        # keep process the data from the input
        value = q.get(True)
        # process the data out
        frames.append(value)
        # account the frame number
        account_clock = account_clock+1
        # when the time get around 0.1 second
        if account_clock ==5:
            # design for the first frame in case no beat detetct
            if flag==True:
                # make the list to the frame
                frames0 = np.array(frames)
                # change the data types 
                frames_first = librosa.util.buf_to_float(frames0, dtype=np.float32)
                (y, sr, actual_tempo, special_time) = getdynamictempo()
                # get the onset envelop
                onset_envelope_first = librosa.onset.onset_strength(y=frames_first, sr=sr, hop_length=512, n_fft=2048)
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
                beats = time_f
                # Get the tempo and beat from dynamic program(optional)
                #tempo, beats = librosa.beat.beat_track(frames_first, sr=sr, start_bpm=60, units='time')
                # get the tempo and beat use the new methods(optional)
                #(frame_f, time_f) = find_location(spectral_novelty, temporeal, special_Single_left,special_Single_right,frame_f=frame_f,time_f = time_f)
                # change back to false flag
                flag = False
                if beats is not None:
                    # put the data into the list
                    for j in range(len(beats)):
                        # get the result near to last two decimal point
                        print(round(beats[j],2))
                        # get the data to the all data list
                        beat_all.append(beats[j])
            else:
                # repeat the last part at this time is not first frame anymore
                frames0 = np.array(frames)
                frames1 = librosa.util.buf_to_float(frames0, dtype=np.float32)
                #tempo estimate
                #onset_envelope = librosa.onset.onset_strength(y=frames1, sr=sr, hop_length=512, n_fft=2048)
                tempo, beats = librosa.beat.beat_track(frames1, sr=sr, start_bpm=60, units='time')
                #print(k)
                # begin to predict the future beat basic on the orginal methods
                if len(beats)>2:
                    last_beat = beats[len(beats) - 1]
                    #print(last_beat)
                    second_last_beat = beats[len(beats) - 2]
                    # calculate the number of beat need to process
                    for i in range(round(float(tempo)/60.0)):
                    # evaluate the future time
                        last_beat, second_last_beat = beatevaluate(second_last_beat,last_beat)
                        # filter the noise beat
                        if last_beat not in beat_all and last_beat > beat_all[len(beat_all)-1]+0.05:
                        # add to future data
                            beat_all.append(last_beat)
                        # print out the predict data
                            print(round(last_beat,2))
            # clear the clock number
            account_clock =0
            # number account
            k= k+1
            



if __name__=='__main__':
    # define the queue
    q = Queue()
    print("* recording")
    # create the first processor for geting the data
    pw = Process(target=dataread, args=(q,CHUNK))
    # create the second processor for output the data
    pr = Process(target=dataout, args=(q,))

    # open process of pw
    pw.start()
    # open process of pr
    pr.start()
    # waiting fir the pw joining

    pw.join()

    # terminal pr
    pr.terminate()

    print("* done recording")
