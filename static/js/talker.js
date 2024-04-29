const socket = io();
let timerInterval = null;
let startTime = null;
const timerElement = document.getElementById('talkerTimer');  // Declare once, use throughout
const lastTalkerElement = document.getElementById('lastTalker');

socket.on('connect', () => {
    console.log('Connected to server');
});

socket.on('update_last_talker', (talker) => {
    console.log('Received last talker data:', talker)
    const talker_callsign = talker['call_sign'];
    if (!talker['stopped']) {
        lastTalkerElement.innerText = "Current Talker: " + talker_callsign;
        startTime = parseDateTime(talker['start_date_time']).getTime();
        startTimer();
    } else {
        lastTalkerElement.innerText = "Previous Talker: " + talker_callsign;
        stopTimer();
        displayTalkDuration(talker.duration || 0);  // Display duration or reset if undefined
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
    const [date, time] = dateTimeStr.split(' ');
    const [day, month, year] = date.split('.');
    const [hours, minutes, seconds] = time.split(':');

    // Create a new Date object with year, month (0-indexed), day, hours, minutes, seconds
    return new Date(+year, month - 1, // Month is 0-indexed in JavaScript
        +day, +hours, +minutes, +seconds);
}