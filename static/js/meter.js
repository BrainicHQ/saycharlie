let context;
let analyser;
let mediaStreamAudioSourceNode;
let animationFrameId;
const meter = document.getElementById("meter");
const dBLabel = document.getElementById("dBLabel");
const toggleButtonEl = document.getElementById("toggleButton");
let isMeasuring = false;

toggleButtonEl.onclick = async () => {
    if (!isMeasuring) {
        // Start measuring
        toggleButtonEl.textContent = "Stop Measuring";
        // change the button color via tailwindcss to red
        toggleButtonEl.classList.remove("bg-blue-500");
        toggleButtonEl.classList.add("bg-red-500");
        isMeasuring = true;

        const stream = await navigator.mediaDevices.getUserMedia({audio: true, video: false});
        context = new AudioContext();
        mediaStreamAudioSourceNode = context.createMediaStreamSource(stream);
        analyser = context.createAnalyser();

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
            meter.value = Math.max(0, Math.min(1, (dBLevel + 30) / 20 * 0.25));

            // Update dB label text
            dBLabel.textContent = `${dBLevel.toFixed(2)} dB`;

            if (isMeasuring) {
                animationFrameId = window.requestAnimationFrame(onFrame);
            }
        };

        animationFrameId = window.requestAnimationFrame(onFrame);
    } else {
        // Stop measuring
        toggleButtonEl.textContent = "Start Measuring";
        isMeasuring = false;

        // change the button color via tailwindcss to blue
        toggleButtonEl.classList.remove("bg-red-500");
        toggleButtonEl.classList.add("bg-blue-500");

        window.cancelAnimationFrame(animationFrameId);
        if (mediaStreamAudioSourceNode) {
            mediaStreamAudioSourceNode.disconnect();
        }
        if (analyser) {
            analyser.disconnect();
        }
        if (context) {
            await context.close();
        }
    }
};