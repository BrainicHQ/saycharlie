/*
 * # Copyright (c) 2024 by Silviu Stroe (brainic.io)
 * #
 * # This program is free software: you can redistribute it and/or modify
 * # it under the terms of the GNU General Public License as published by
 * # the Free Software Foundation, either version 3 of the License, or
 * # (at your option) any later version.
 * #
 * # This program is distributed in the hope that it will be useful,
 * # but WITHOUT ANY WARRANTY; without even the implied warranty of
 * # MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
 * # GNU General Public License for more details.
 * #
 * # You should have received a copy of the GNU General Public License
 * # along with this program. If not, see <http://www.gnu.org/licenses/>.
 * #
 * # Created on 5/16/24, 8:44 PM
 * #
 * # Author: Silviu Stroe
 */

const socket = io();
let timerInterval = null;
let startTime = null;
const timerElement = document.getElementById('talkerTimer');  // Declare once, use throughout
const lastTalkerElement = document.getElementById('lastTalker');

socket.on('connect', () => {
    console.log('Connected to server');
});

socket.on('update_last_talker', async (talker) => {
    const talker_callsign = talker['callsign'];
    try {
        // Fetch the name using the async function
        const name = await fetchName(talker_callsign);
        const displayName = name ? ` (${name})` : ' (Name unavailable)';

        if (!talker['stopped']) {
            lastTalkerElement.innerText = "Current Talker: " + talker_callsign + displayName;
            startTime = parseDateTime(talker['start_date_time']).getTime();
            startTimer();
        } else {
            lastTalkerElement.innerText = "Previous Talker: " + talker_callsign + displayName;
            stopTimer();
            displayTalkDuration(talker.duration || 0);  // Display duration or reset if undefined
        }
    } catch (error) {
        console.error('Failed to fetch name:', error);
        // Handle the error by updating the UI appropriately
        lastTalkerElement.innerText = talker['stopped'] ? "Previous Talker: " + talker_callsign + " (Failed to fetch name)" : "Current Talker: " + talker_callsign + " (Failed to fetch name)";
        if (!talker['stopped']) {
            startTimer();
        } else {
            stopTimer();
            displayTalkDuration(talker.duration || 0);
        }
    }
});

function startTimer() {
    if (timerInterval) clearInterval(timerInterval);
    timerInterval = setInterval(() => {
        updateTimerDisplay(Date.now() - startTime);
    }, 1000);
}

function stopTimer() {
    clearInterval(timerInterval);
}

function updateTimerDisplay(elapsedTime) {
    let minutes = Math.floor(elapsedTime / 60000);
    let seconds = Math.floor((elapsedTime % 60000) / 1000);
    timerElement.innerText = "Talk Duration: " + minutes + " min " + seconds + " sec";
}

function displayTalkDuration(duration) {
    if (!duration) {
        timerElement.innerText = "No talk currently or data missing.";
    } else {
        let minutes = Math.floor(duration / 60);
        let seconds = Math.floor(duration % 60);
        timerElement.innerText = "Last Talk Duration: " + minutes + " min " + seconds + " sec";
    }
}

function parseDateTime(dateTimeStr) {
    return new Date(dateTimeStr);
}