const meter = document.getElementById("meter");
const dBLabel = document.getElementById("dBLabel");
const startButtonEl = document.getElementById("startButton");

startButtonEl.onclick = async () => {
    startButtonEl.disabled = true;

    const stream = await navigator.mediaDevices.getUserMedia({audio: true, video: false});
    const context = new AudioContext();
    const mediaStreamAudioSourceNode = context.createMediaStreamSource(stream);
    const analyser = context.createAnalyser();

    mediaStreamAudioSourceNode.connect(analyser);

    const pcmData = new Float32Array(analyser.fftSize);

    const onFrame = () => {
        analyser.getFloatTimeDomainData(pcmData);

        let sum = 0.0;
        for (const amplitude of pcmData) {
            sum += amplitude * amplitude;
        }

        // Calculate RMS (Root Mean Square) level in dB
        const rms = Math.sqrt(sum / pcmData.length);
        const dBLevel = 20 * Math.log10(rms);

        // Scale the dB level to fit within a narrower range of the meter's scale
        // Update meter value
        meter.value = Math.max(0, Math.min(1, (dBLevel + 30) / 20 * 0.25));

        // Update dB label text
        dBLabel.textContent = `${dBLevel.toFixed(2)} dB`;

        window.requestAnimationFrame(onFrame);
    };

    window.requestAnimationFrame(onFrame);
};