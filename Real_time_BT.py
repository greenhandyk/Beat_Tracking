import pyaudio
import numpy as np
import wave
import librosa, librosa.display
from librosa import util
import time
from multiprocessing import Process, Queue
import os, time, random
from tempodetect import tempo





CHUNK = 2048
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 22500
sr = 22500
RECORD_SECONDS = 5
WAVE_OUTPUT_FILENAME = "output.wav"




# beat predict function
def beatevaluate(second_last_beat,last_beat):

    t = last_beat
    last_beat = 2*float(last_beat)-float(second_last_beat)
    second_last_beat = t

    return(last_beat,second_last_beat)


# data read function
def dataread(q,CHUNK):

    p = pyaudio.PyAudio()
    stream = p.open(format=pyaudio.paInt16, channels=1, rate=22500, input=True, frames_per_buffer=CHUNK)
    begin = time.time()
    print('begin', begin)
    for i in range(0, int(22500.0 / CHUNK * 30.0)):

        data = stream.read(CHUNK)

        q.put(data)

    stream.stop_stream()
    stream.close()
    p.terminate()
    stop = time.time()
    
# data out function
def dataout(q):

    frames = []
    beat_all=[0]
    #frames = np.array(frames)
    print(type(frames))
    account_clock =0
    flag = True
    k=1

    while True:

        value = q.get(True)

        # process the data out
        frames.append(value)
        
        


        account_clock = account_clock+1




        if account_clock ==5:

            if flag==True:
                frames0 = np.array(frames)
                frames_first = librosa.util.buf_to_float(frames0, dtype=np.float32)

                onset_envelope_first = librosa.onset.onset_strength(y=frames_first, sr=sr, hop_length=512, n_fft=2048)
                # Get the tempo and beat from dynamic program(optional)
                tempo, beats = librosa.beat.beat_track(frames_first, sr=sr, start_bpm=60, units='time')
                # get the tempo and beat use the new methods(optional)
                #(frame_f, time_f) = find_location(spectral_novelty, temporeal, special_Single_left,special_Single_right,frame_f=frame_f,time_f = time_f)
                
                flag = False
                if beats is not None:
                    for j in range(len(beats)):

                        print(round(beats[j],2))

                        beat_all.append(beats[j])
            else:
                frames0 = np.array(frames)
                frames1 = librosa.util.buf_to_float(frames0, dtype=np.float32)
                #tempo estimate
                #onset_envelope = librosa.onset.onset_strength(y=frames1, sr=sr, hop_length=512, n_fft=2048)

                tempo, beats = librosa.beat.beat_track(frames1, sr=sr, start_bpm=60, units='time')
                #print(k)
                

                if len(beats)>2:
                    last_beat = beats[len(beats) - 1]
                    #print(last_beat)
                    second_last_beat = beats[len(beats) - 2]

                    for i in range(round(float(tempo)/60.0)):

                        last_beat, second_last_beat = beatevaluate(second_last_beat,last_beat)


                        if last_beat not in beat_all and last_beat > beat_all[len(beat_all)-1]+0.05:

                            beat_all.append(last_beat)

                            print(round(last_beat,2))

            account_clock =0

            k= k+1
            








if __name__=='__main__':

    q = Queue()
    print("* recording")

    pw = Process(target=dataread, args=(q,CHUNK))

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
