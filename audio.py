#  Copyright (c) 2024 by Silviu Stroe (brainic.io)
#  #
#  This program is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#  #
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
#  GNU General Public License for more details.
#  #
#  You should have received a copy of the GNU General Public License
#  along with this program. If not, see <http://www.gnu.org/licenses/>.
#  #
#  Created on 6/6/24, 1:26 PM
#  #
#  Author: Silviu Stroe

import pyaudio
import numpy as np
import math

# Constants
CHUNK = 1024
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 44100
REFERENCE_PEAK = 32767  # Maximum peak value for 16-bit signed integer


def start_audio_monitor(stop_event, socketio):
    p = pyaudio.PyAudio()  # Define the PyAudio instance

    # Find input device index configured for dsnoop
    input_device_index = None
    for i in range(p.get_device_count()):
        dev_info = p.get_device_info_by_index(i)
        if 'USB Audio' in dev_info.get('name'):
            input_device_index = i
            break

    if input_device_index is None:
        print("Suitable dsnoop device not found. Please check your ALSA configuration.")
        return

    def callback(in_data, frame_count, time_info, status):
        try:
            # Calculate audio levels from input data
            ndarray = np.frombuffer(in_data, dtype=np.int16)
            peak = np.max(np.abs(ndarray))
            db = -30
            if peak > 0:
                # Normalize peak value and calculate dB level
                normalized_peak = peak / REFERENCE_PEAK
                db = 20 * math.log10(normalized_peak + 1e-40)
                db = max(-30, db)
                db = min(3, db)

            # Emit audio level data
            socketio.emit('audio_level', {'level': db}, namespace='/')
        except Exception as e:
            print(f"Error processing audio data: {e}")

        return None, pyaudio.paContinue

    # Open input stream with callback
    input_stream = p.open(format=FORMAT,
                          channels=CHANNELS,
                          rate=RATE,
                          input=True,
                          frames_per_buffer=CHUNK,
                          input_device_index=input_device_index,
                          stream_callback=callback)

    print("Starting to monitor audio with dsnoop...")
    input_stream.start_stream()

    try:
        while not stop_event.is_set():
            socketio.sleep(0.1)  # Keep the main thread active
    finally:
        print("Stopping audio monitor...")
        input_stream.stop_stream()
        input_stream.close()
        p.terminate()
