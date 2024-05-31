#!/bin/bash
# Script to create a loopback device that routes microphone input to playback in real-time
#
#  Copyright (c) 2024 by Silviu Stroe (brainic.io)
#
#  This program is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program. If not, see <http://www.gnu.org/licenses/>.
#
#  Created on 5/30/24, 1:16 PM
#
#  Author: Silviu Stroe
#

# Kill any running arecord or aplay processes
pkill arecord
pkill aplay

# Function to find the microphone device
find_microphone() {
    # Get list of audio input devices
    devices=$(arecord -l | grep "card [0-9]:")

    # Extract the first device that contains "USB Audio" in its name (assuming that's the microphone) and return its ID
    # If no such device is found, return the first device in the list that is not the loopback device
    best_device=""
    while IFS= read -r device; do
        if echo "$device" | grep -q "USB Audio"; then
            best_device=$(echo "$device" | cut -d ' ' -f 2 | tr -d ':')
            break
        elif [ -z "$best_device" ] && ! echo "$device" | grep -q "Loopback"; then
            best_device=$(echo "$device" | cut -d ' ' -f 2 | tr -d ':')
        fi
    done <<< "$devices"

    echo "$best_device"
}

# Find the microphone device
mic=$(find_microphone)

if [ -z "$mic" ]; then
    echo "Microphone not found."
    exit 1
fi

# Load the loopback module if it's not already loaded
if ! lsmod | grep -q "snd_aloop"; then
    sudo modprobe snd_aloop
fi

# Create /etc/asound.conf with dynamic microphone device
cat > /etc/asound.conf <<EOL
# Define a loopback PCM device
pcm.loopback {
    type plug
    slave.pcm "hw:Loopback,1,0"
}

# Define a microphone input that routes through the loopback device
pcm.mic_route {
    type plug
    slave.pcm "hw:${mic},0"  # This is your microphone device
}

# Define a default PCM device that routes microphone input to loopback for playback
pcm.!default {
    type asym
    playback.pcm "loopback"
    capture.pcm "mic_route"
}
EOL

# Route the microphone input to the loopback device
arecord -f cd -D "hw:${mic},0" | aplay -D hw:1,0 &

# Disown the process so it doesn't get killed when the terminal is closed
disown