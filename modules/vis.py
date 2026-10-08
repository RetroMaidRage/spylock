import sounddevice as sd
import numpy as np
import time
import configparser

config = configparser.ConfigParser()
config.read("spylock.conf")

vis_bars = config.getint("M_Visualizer",  "bars_length")

sample_rate = 44100
bars_length = vis_bars

audio_bars = [0.0] * bars_length
freq_data = [(0, 0)] * bars_length

#print(sd.query_devices())

def sort(magnt, freq, bars):
    global audio_bars, freq_data
    result = []
    freq_history = []
    freq_ranges = np.logspace(np.log10(20), np.log10(20000), bars + 1)

    for i in range(bars):
        low = freq_ranges[i]
        high = freq_ranges[i + 1]
        freq_history.append((low, high))

        mask = (freq >= low) & (freq < high)

        if np.any(mask):
            value = magnt[mask].mean()
        else:
            #value = max(value, 0.02)
            value = value

        result.append(value)

    return result, freq_history

def cli_visualize(output,freq_history, bars):
    print("\n"*100)
    all_bars = []
    for i in range(bars):
        curr_length = int(output[i] * 20)
        bar = "=" * curr_length
        #print(f"Bar: {i}: {bar} {output[i]:.2f}")
        print(f"Bar: {i}: {bar} {freq_history[i][0]:.0f}/{freq_history[i][1]:.0f}")



def callback(indata, frames, time, status):
    global audio_bars, freq_data

    audio = indata[:, 0]

    fft = np.fft.rfft(audio)
    magnitude = np.abs(fft)
    magnitude = np.log1p(magnitude)

    max_val = np.max(magnitude)
    if max_val > 0:
        magnitude = magnitude / max_val

    freqs = np.fft.rfftfreq(len(audio), 1 / sample_rate)

    output, freq_history = sort(magnitude, freqs, bars_length)


    alpha = 0.3
    audio_bars[:] = (
        np.array(audio_bars) * alpha +
        np.array(output) * (1 - alpha)
    )

    freq_data = freq_history
#    audio_bars = [(v * 0.8 + old * 0.2) for v, old in zip(output, audio_bars)]
    #cli_visualize(output, freq_history, bars_length)
# device=14
stream = sd.InputStream(callback=callback, channels=1, samplerate=sample_rate, blocksize=4096)
stream.start()
