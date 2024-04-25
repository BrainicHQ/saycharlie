const socket = io();
let timerInterval = null;

socket.on('connect', function () {
    console.log('Connected to server');
});

socket.on('update_last_talker', function (data) {
    // Update the content of the last talker <div>
    const lastTalkerElement = document.getElementById('lastTalker');
    if (data.last_talker !== "No one currently talking") {
        lastTalkerElement.innerText = "Last Talker: " + data.last_talker;
        startTimer();
    } else {
        lastTalkerElement.innerText = "Last Talker: " + data.last_talker;
        stopTimer();
        if (data.duration) {
            displayTalkDuration(data.duration);
        }
    }
});

function startTimer() {
    const timerElement = document.getElementById('talkerTimer');
    let startTime = Date.now();
    if (timerInterval) clearInterval(timerInterval);
    timerInterval = setInterval(() => {
        let elapsedTime = Math.floor((Date.now() - startTime) / 1000);
        let minutes = Math.floor(elapsedTime / 60);
        let seconds = elapsedTime % 60;
        timerElement.innerText = "Talk Duration: " + minutes + " min " + seconds + " sec";
    }, 1000);
}

function stopTimer() {
    clearInterval(timerInterval);
}

function displayTalkDuration(duration) {
    const timerElement = document.getElementById('talkerTimer');
    let minutes = Math.floor(duration / 60);
    let seconds = Math.floor(duration % 60);
    timerElement.innerText = "Last Talk Duration: " + minutes + " min " + seconds + " sec";
}