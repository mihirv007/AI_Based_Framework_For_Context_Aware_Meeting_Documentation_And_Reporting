import sounddevice as sd
from scipy.io.wavfile import write
import datetime
import requests
import os

fs = 16000
duration = 600  # 10 minutes (full meeting chunk)

SERVER_URL = "http://192.168.1.5:5000/upload-audio"  # your laptop IP

def record_and_send():
    print("Recording started...")

    audio = sd.rec(int(duration * fs), samplerate=fs, channels=1)
    sd.wait()

    filename = f"meeting_{datetime.datetime.now().strftime('%H-%M-%S')}.wav"
    write(filename, fs, audio)

    print(f"Saved: {filename}")

    try:
        with open(filename, 'rb') as f:
            response = requests.post(SERVER_URL, files={'file': f})

        print("Uploaded:", response.status_code)

        # Optional: delete file after sending
        os.remove(filename)

    except Exception as e:
        print("Upload failed:", e)

# LOOP
while True:
    record_and_send()