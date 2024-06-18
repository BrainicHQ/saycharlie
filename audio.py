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
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(module)s - %(levelname)s: %(message)s',
    filename='/tmp/saycharlie.log',
    filemode='a'  # Use 'a' to append to the file
)

# Constants
CHUNK = 1024  # Size of each audio chunk to receive (in bytes, assuming each sample is 4 bytes as it's a 32-bit float)
FORMAT = 'f'  # Format of each sample (32-bit float)
CHANNELS = 1
RATE = 44100
REFERENCE_PEAK = 1.0  # Maximum peak value for 32-bit float audio


def start_audio_monitor(stop_event, socketio):
    # Setting up the first UDP socket on port 10000
    udp_ip = '127.0.0.1'
    udp_port = 10000
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind((udp_ip, udp_port))
    sock.setblocking(False)

    # Setting up the second UDP socket on port 10001
    udp_port2 = 10001
    sock2 = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock2.bind((udp_ip, udp_port2))
    sock2.setblocking(False)

    logging.info("UDP sockets bound to %s:%d and %s:%d", udp_ip, udp_port, udp_ip, udp_port2)

    try:
        while not stop_event.is_set():
            readable, _, _ = select.select([sock, sock2], [], [], 5)  # Modified to check both sockets
            for s in readable:
                try:
                    data, addr = s.recvfrom(CHUNK * 4)  # Attempt to receive CHUNK samples, each 4 bytes
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
                        logging.debug("Audio level emitted from %s: %f dB", addr, db)
                    else:
                        logging.warning("Received empty data packet from %s.", addr)
                except socket.error as e:
                    logging.error("Socket error occurred: %s", e)
            else:
                logging.info("Socket timed out without receiving data, continuing...")
    except Exception as e:
        logging.critical("Error processing audio data: %s", e)
    finally:
        sock.close()
        sock2.close()
        logging.info("Stopping audio monitor...")
