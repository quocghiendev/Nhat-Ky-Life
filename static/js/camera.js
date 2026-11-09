// Camera and Photo Manager
(function() {
  const liveVideo = document.getElementById('liveVideo');
  const captureCanvas = document.getElementById('captureCanvas');
  const capturedImagePreview = document.getElementById('capturedImagePreview');
  const cameraPlaceholder = document.getElementById('cameraPlaceholder');
  const liveCameraControls = document.getElementById('liveCameraControls');
  
  const startCameraBtn = document.getElementById('startCameraBtn');
  const stopCameraBtn = document.getElementById('stopCameraBtn');
  const snapPhotoBtn = document.getElementById('snapPhotoBtn');
  const switchCameraBtn = document.getElementById('switchCameraBtn');
  const clearPhotoBtn = document.getElementById('clearPhotoBtn');
  const imageFileInput = document.getElementById('imageFileInput');
  const photoBadge = document.getElementById('photoBadge');

  let currentStream = null;
  let currentFacingMode = 'environment'; // 'environment' (back) or 'user' (front)
  let capturedBlob = null;
  let capturedFile = null;

  async function startCamera() {
    try {
      if (currentStream) {
        stopCamera();
      }

      const constraints = {
        video: {
          facingMode: currentFacingMode,
          width: { ideal: 1920 },
          height: { ideal: 1080 }
        },
        audio: false
      };

      currentStream = await navigator.mediaDevices.getUserMedia(constraints);
      liveVideo.srcObject = currentStream;
      liveVideo.classList.remove('hidden');
      liveCameraControls.classList.remove('hidden');
      cameraPlaceholder.classList.add('hidden');
      capturedImagePreview.classList.add('hidden');
      photoBadge.textContent = 'Camera đang chạy';
      photoBadge.className = 'text-xs bg-emerald-500/20 text-emerald-400 px-2 py-0.5 rounded-full';
    } catch (err) {
      console.error('Camera access error:', err);
      alert('Không thể mở camera: ' + (err.message || 'Thiết bị không cho phép truy cập. Bạn có thể dùng nút "Tải ảnh lên".'));
    }
  }

  function stopCamera() {
    if (currentStream) {
      currentStream.getTracks().forEach(track => track.stop());
      currentStream = null;
    }
    liveVideo.classList.add('hidden');
    liveCameraControls.classList.add('hidden');
    if (!capturedBlob && !capturedFile) {
      cameraPlaceholder.classList.remove('hidden');
      photoBadge.textContent = 'Chưa có ảnh';
      photoBadge.className = 'text-xs bg-slate-800 text-slate-400 px-2 py-0.5 rounded-full';
    }
  }

  function snapPhoto() {
    if (!currentStream || !liveVideo.videoWidth) return;

    captureCanvas.width = liveVideo.videoWidth;
    captureCanvas.height = liveVideo.videoHeight;
    const ctx = captureCanvas.getContext('2d');
    ctx.drawImage(liveVideo, 0, 0, captureCanvas.width, captureCanvas.height);

    captureCanvas.toBlob(blob => {
      capturedBlob = blob;
      capturedFile = new File([blob], `snap_${Date.now()}.jpg`, { type: 'image/jpeg' });
      
      const imageUrl = URL.createObjectURL(blob);
      capturedImagePreview.src = imageUrl;
      capturedImagePreview.classList.remove('hidden');
      cameraPlaceholder.classList.add('hidden');
      clearPhotoBtn.classList.remove('hidden');

      stopCamera();

      photoBadge.textContent = 'Đã chụp ảnh ✓';
      photoBadge.className = 'text-xs bg-purple-500/20 text-purple-300 px-2 py-0.5 rounded-full font-bold';
    }, 'image/jpeg', 0.92);
  }

  function switchCamera() {
    currentFacingMode = (currentFacingMode === 'environment') ? 'user' : 'environment';
    startCamera();
  }

  function handleFileUpload(e) {
    const file = e.target.files[0];
    if (!file) return;

    stopCamera();
    capturedFile = file;
    capturedBlob = file;

    const reader = new FileReader();
    reader.onload = (event) => {
      capturedImagePreview.src = event.target.result;
      capturedImagePreview.classList.remove('hidden');
      cameraPlaceholder.classList.add('hidden');
      clearPhotoBtn.classList.remove('hidden');

      photoBadge.textContent = 'Đã chọn ảnh ✓';
      photoBadge.className = 'text-xs bg-purple-500/20 text-purple-300 px-2 py-0.5 rounded-full font-bold';
    };
    reader.readAsDataURL(file);
  }

  function clearPhoto() {
    stopCamera();
    capturedBlob = null;
    capturedFile = null;
    capturedImagePreview.src = '';
    capturedImagePreview.classList.add('hidden');
    cameraPlaceholder.classList.remove('hidden');
    clearPhotoBtn.classList.add('hidden');
    imageFileInput.value = '';

    photoBadge.textContent = 'Chưa có ảnh';
    photoBadge.className = 'text-xs bg-slate-800 text-slate-400 px-2 py-0.5 rounded-full';
  }

  // Event Listeners
  startCameraBtn.addEventListener('click', startCamera);
  stopCameraBtn.addEventListener('click', stopCamera);
  snapPhotoBtn.addEventListener('click', snapPhoto);
  switchCameraBtn.addEventListener('click', switchCamera);
  clearPhotoBtn.addEventListener('click', clearPhoto);
  imageFileInput.addEventListener('change', handleFileUpload);

  // Expose API
  window.cameraManager = {
    getImageFile: () => capturedFile,
    hasImage: () => Boolean(capturedFile),
    clear: clearPhoto
  };
})();
