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

import socket
import numpy as np
import math

# Constants
CHUNK = 1024  # Size of each audio chunk to receive (in bytes, assuming each sample is 4 bytes as it's a 32-bit float)
FORMAT = 'f'  # Format of each sample (32-bit float)
CHANNELS = 1
RATE = 44100
REFERENCE_PEAK = 1.0  # Maximum peak value for 32-bit float audio


def start_audio_monitor(stop_event, socketio):
    # Setting up the UDP socket
    udp_ip = '127.0.0.1'
    udp_port = 10000
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind((udp_ip, udp_port))

    print("UDP socket bound to {}:{}".format(udp_ip, udp_port))

    try:
        while not stop_event.is_set():
            # Receive data from the socket
            data, addr = sock.recvfrom(CHUNK * 4)  # Receive CHUNK samples, each 4 bytes
            if not data:
                break

            # Convert bytes to 32-bit floats
            ndarray = np.frombuffer(data, dtype=np.float32)

            # Calculate the peak and dB level
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
    finally:
        print("Stopping audio monitor...")
        sock.close()
