// Audio and Voice Recording Manager
(function() {
  const toggleRecordBtn = document.getElementById('toggleRecordBtn');
  const recordBtnText = document.getElementById('recordBtnText');
  const recordBtnIcon = document.getElementById('recordBtnIcon');
  const recordIndicator = document.getElementById('recordIndicator');
  const recordingTimer = document.getElementById('recordingTimer');
  const audioBadge = document.getElementById('audioBadge');
  const clearAudioBtn = document.getElementById('clearAudioBtn');
  const audioFileInput = document.getElementById('audioFileInput');
  const recordedAudioPlayer = document.getElementById('recordedAudioPlayer');
  const recordedAudioPlayerContainer = document.getElementById('recordedAudioPlayerContainer');
  const speechLiveTranscript = document.getElementById('speechLiveTranscript');
  const canvas = document.getElementById('audioVisualizerCanvas');
  const ctx = canvas.getContext('2d');

  let mediaRecorder = null;
  let audioChunks = [];
  let recordedBlob = null;
  let recordedFile = null;
  let isRecording = false;

  let timerInterval = null;
  let startTime = 0;

  // Web Audio API for visualizer
  let audioCtx = null;
  let analyser = null;
  let animFrameId = null;

  // Speech Recognition (Optional instant live transcript)
  let recognition = null;
  let liveTranscript = '';

  function setupSpeechRecognition() {
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    if (SpeechRecognition) {
      try {
        recognition = new SpeechRecognition();
        recognition.continuous = true;
        recognition.interimResults = true;
        recognition.lang = 'vi-VN';

        recognition.onresult = (event) => {
          let interimTranscript = '';
          for (let i = event.resultIndex; i < event.results.length; ++i) {
            if (event.results[i].isFinal) {
              liveTranscript += event.results[i][0].transcript + ' ';
            } else {
              interimTranscript += event.results[i][0].transcript;
            }
          }
          speechLiveTranscript.textContent = (liveTranscript + interimTranscript).trim();
        };

        recognition.onerror = (e) => {
          console.warn('Speech recognition warning:', e.error);
        };
      } catch (e) {
        console.warn('Web Speech API initialization:', e);
      }
    }
  }

  setupSpeechRecognition();

  async function startRecording() {
    try {
      audioChunks = [];
      liveTranscript = '';
      speechLiveTranscript.textContent = '';
      
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });

      // Setup audio context & analyser
      audioCtx = new (window.AudioContext || window.webkitAudioContext)();
      analyser = audioCtx.createAnalyser();
      analyser.fftSize = 64;
      const source = audioCtx.createMediaStreamSource(stream);
      source.connect(analyser);

      // MediaRecorder
      let mimeType = 'audio/webm';
      if (!MediaRecorder.isTypeSupported('audio/webm')) {
        if (MediaRecorder.isTypeSupported('audio/mp4')) mimeType = 'audio/mp4';
        else if (MediaRecorder.isTypeSupported('audio/ogg')) mimeType = 'audio/ogg';
        else mimeType = '';
      }

      mediaRecorder = mimeType ? new MediaRecorder(stream, { mimeType }) : new MediaRecorder(stream);

      mediaRecorder.ondataavailable = (e) => {
        if (e.data && e.data.size > 0) {
          audioChunks.push(e.data);
        }
      };

      mediaRecorder.onstop = () => {
        stream.getTracks().forEach(track => track.stop());
        if (audioCtx) {
          audioCtx.close();
          audioCtx = null;
        }
        cancelAnimationFrame(animFrameId);
        drawIdleVisualizer();

        const type = mediaRecorder.mimeType || 'audio/webm';
        recordedBlob = new Blob(audioChunks, { type });
        const ext = type.includes('mp4') ? 'm4a' : (type.includes('ogg') ? 'ogg' : 'webm');
        recordedFile = new File([recordedBlob], `voice_${Date.now()}.${ext}`, { type });

        // Setup player preview
        const audioUrl = URL.createObjectURL(recordedBlob);
        recordedAudioPlayer.src = audioUrl;
        recordedAudioPlayerContainer.classList.remove('hidden');
        clearAudioBtn.classList.remove('hidden');

        audioBadge.textContent = 'Đã ghi âm ✓';
        audioBadge.className = 'text-xs bg-pink-500/20 text-pink-300 px-2 py-0.5 rounded-full font-bold';
      };

      mediaRecorder.start(250);
      isRecording = true;

      // Start timer
      startTime = Date.now();
      timerInterval = setInterval(updateTimer, 500);

      // Start speech recognition if supported
      if (recognition) {
        try { recognition.start(); } catch (_) {}
      }

      // Update UI
      toggleRecordBtn.className = 'flex-1 py-2 px-3 rounded-xl bg-red-600 hover:bg-red-500 text-white text-xs font-bold flex items-center justify-center space-x-2 transition shadow-md shadow-red-600/30';
      recordBtnText.textContent = 'Dừng Ghi Âm';
      recordBtnIcon.className = 'fa-solid fa-stop animate-pulse';
      recordIndicator.className = 'w-3 h-3 rounded-full bg-red-500 recording-pulse';
      audioBadge.textContent = 'Đang ghi âm...';
      audioBadge.className = 'text-xs bg-red-500/20 text-red-400 px-2 py-0.5 rounded-full';

      // Start visualizer animation
      drawVisualizer();

    } catch (err) {
      console.error('Audio recording error:', err);
      alert('Không thể truy cập Microphone: ' + (err.message || 'Thiết bị không cho phép truy cập. Bạn có thể dùng nút "Tải file Voice".'));
    }
  }

  function stopRecording() {
    if (mediaRecorder && mediaRecorder.state !== 'inactive') {
      mediaRecorder.stop();
    }
    isRecording = false;
    clearInterval(timerInterval);

    if (recognition) {
      try { recognition.stop(); } catch (_) {}
    }

    toggleRecordBtn.className = 'flex-1 py-2 px-3 rounded-xl bg-pink-600 hover:bg-pink-500 text-white text-xs font-bold flex items-center justify-center space-x-2 transition shadow-md shadow-pink-600/30';
    recordBtnText.textContent = 'Ghi Âm Lại';
    recordBtnIcon.className = 'fa-solid fa-microphone';
    recordIndicator.className = 'w-3 h-3 rounded-full bg-slate-600';
  }

  function updateTimer() {
    const elapsedSec = Math.floor((Date.now() - startTime) / 1000);
    const m = String(Math.floor(elapsedSec / 60)).padStart(2, '0');
    const s = String(elapsedSec % 60).padStart(2, '0');
    recordingTimer.textContent = `${m}:${s}`;
  }

  function drawVisualizer() {
    if (!isRecording || !analyser) return;

    const bufferLength = analyser.frequencyBinCount;
    const dataArray = new Uint8Array(bufferLength);
    analyser.getByteFrequencyData(dataArray);

    ctx.clearRect(0, 0, canvas.width, canvas.height);

    const barWidth = (canvas.width / bufferLength) * 2;
    let x = 0;

    for (let i = 0; i < bufferLength; i++) {
      const barHeight = (dataArray[i] / 255) * canvas.height;
      
      const gradient = ctx.createLinearGradient(0, canvas.height, 0, 0);
      gradient.addColorStop(0, '#db2777');
      gradient.addColorStop(1, '#a855f7');

      ctx.fillStyle = gradient;
      ctx.fillRect(x, canvas.height - barHeight, barWidth - 2, barHeight);

      x += barWidth;
    }

    animFrameId = requestAnimationFrame(drawVisualizer);
  }

  function drawIdleVisualizer() {
    ctx.clearRect(0, 0, canvas.width, canvas.height);
    ctx.strokeStyle = '#334155';
    ctx.lineWidth = 2;
    ctx.beginPath();
    ctx.moveTo(0, canvas.height / 2);
    ctx.lineTo(canvas.width, canvas.height / 2);
    ctx.stroke();
  }

  function handleFileUpload(e) {
    const file = e.target.files[0];
    if (!file) return;

    if (isRecording) stopRecording();

    recordedFile = file;
    recordedBlob = file;

    const audioUrl = URL.createObjectURL(file);
    recordedAudioPlayer.src = audioUrl;
    recordedAudioPlayerContainer.classList.remove('hidden');
    clearAudioBtn.classList.remove('hidden');

    audioBadge.textContent = 'Đã chọn file voice ✓';
    audioBadge.className = 'text-xs bg-pink-500/20 text-pink-300 px-2 py-0.5 rounded-full font-bold';
    recordingTimer.textContent = '00:00';
  }

  function clearAudio() {
    if (isRecording) stopRecording();

    recordedBlob = null;
    recordedFile = null;
    recordedAudioPlayer.src = '';
    recordedAudioPlayerContainer.classList.add('hidden');
    clearAudioBtn.classList.add('hidden');
    audioFileInput.value = '';
    speechLiveTranscript.textContent = '';
    recordingTimer.textContent = '00:00';

    audioBadge.textContent = 'Chưa có voice';
    audioBadge.className = 'text-xs bg-slate-800 text-slate-400 px-2 py-0.5 rounded-full';

    drawIdleVisualizer();
  }

  // Event Listeners
  toggleRecordBtn.addEventListener('click', () => {
    if (!isRecording) {
      startRecording();
    } else {
      stopRecording();
    }
  });

  clearAudioBtn.addEventListener('click', clearAudio);
  audioFileInput.addEventListener('change', handleFileUpload);

  // Resize canvas to match display size
  function resizeCanvas() {
    canvas.width = canvas.clientWidth || 300;
    canvas.height = canvas.clientHeight || 96;
    drawIdleVisualizer();
  }
  window.addEventListener('resize', resizeCanvas);
  setTimeout(resizeCanvas, 100);

  // Expose API
  window.audioManager = {
    getAudioFile: () => recordedFile,
    hasAudio: () => Boolean(recordedFile),
    getLiveTranscript: () => speechLiveTranscript.textContent.trim(),
    clear: clearAudio
  };
})();
