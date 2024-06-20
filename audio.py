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
CHUNK = 2048  # Adjust the chunk size to handle more samples per batch
SAMPLE_SIZE = 4  # Each sample is a 32-bit float, hence 4 bytes
GROUP_SIZE = 50  # Number of samples per group for LMS calculation

# dB range for front-end display
MIN_DB = -30
MAX_DB = 3


def calculate_lms(data):
    """Calculate the Log-Mean-Square (LMS) of the given data."""
    squares = np.square(data)
    mean_squares = np.mean(squares)
    lms = np.sqrt(mean_squares)
    return lms


def db_scale(lms):
    """Convert LMS value to a dB scale clamped within a specified range."""
    # dB value before clamping
    if lms > 0:
        db = 20 * math.log10(lms + 1e-40)  # Prevent log(0) error
    else:
        db = MIN_DB
    # Clamping to -30 to 3 dB range
    return max(MIN_DB, min(MAX_DB, db))


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
            readable, _, _ = select.select([sock, sock2], [], [], 5)
            for s in readable:
                data, addr = s.recvfrom(CHUNK * SAMPLE_SIZE)
                if data:
                    samples = np.frombuffer(data, dtype=np.float32)
                    max_lms = float('-inf')
                    for start in range(0, len(samples), GROUP_SIZE):
                        group = samples[start:start + GROUP_SIZE]
                        if len(group) == GROUP_SIZE:
                            lms = calculate_lms(group)
                            db = db_scale(lms)
                            max_lms = max(max_lms, db)  # Track the max dB value as adjusted
                    logging.info("Max dB from %s: %f dB", addr, max_lms)
                    socketio.emit('audio_level', {'level': max_lms}, namespace='/')  # Emit the max dB value
                else:
                    logging.warning("Received empty data packet from %s.", addr)
    except socket.error as e:
        logging.error("Socket error occurred: %s", e)
    except Exception as e:
        logging.critical("Error processing audio data: %s", e)
    finally:
        sock.close()
        sock2.close()
        logging.info("Stopping audio monitor...")
