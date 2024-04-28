const socket = io();
let timerInterval = null;
let startTime = null;
const timerElement = document.getElementById('talkerTimer');  // Declare once, use throughout
const lastTalkerElement = document.getElementById('lastTalker');

socket.on('connect', () => {
    console.log('Connected to server');
});

socket.on('update_last_talker', (data) => {
    console.log('Received last talker data:', data)
    const last_talker = data['call_sign'];
    if (last_talker) {
        lastTalkerElement.innerText = "Current Talker: " + last_talker;
        startTime = Date.now();  // Reset the start time for accurate timing
        startTimer();
    } else {
        lastTalkerElement.innerText = "No one currently talking.";
        stopTimer();
        displayTalkDuration(data.duration || 0);  // Display duration or reset if undefined
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