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
import select

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
    sock.setblocking(0)  # Set the socket to non-blocking mode

    print("UDP socket bound to {}:{}".format(udp_ip, udp_port))

    try:
        while not stop_event.is_set():
            readable, _, _ = select.select([sock], [], [], 5)  # Check if the socket is ready to read with a 5 second timeout
            if readable:
                data, addr = sock.recvfrom(CHUNK * 4)  # Attempt to receive CHUNK samples, each 4 bytes
                if data:
                    ndarray = np.frombuffer(data, dtype=np.float32)
                    peak = np.max(np.abs(ndarray))
                    db = -30
                    if peak > 0:
                        normalized_peak = peak / REFERENCE_PEAK
                        db = 20 * math.log10(normalized_peak + 1e-40)
                        db = max(-30, db)
                        db = min(3, db)
                    socketio.emit('audio_level', {'level': db}, namespace='/')
                else:
                    print("No data received, continuing...")
            else:
                print("Socket timed out without receiving data, continuing...")
    except Exception as e:
        print(f"Error processing audio data: {e}")
    finally:
        sock.close()
        print("Stopping audio monitor...")
