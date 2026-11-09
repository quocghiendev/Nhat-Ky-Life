// Multimodal AI Coordinator
(function() {
  const aiProcessBtn = document.getElementById('aiProcessBtn');
  const aiProcessBtnText = document.getElementById('aiProcessBtnText');
  const aiLoadingStatus = document.getElementById('aiLoadingStatus');
  const aiLoadingText = document.getElementById('aiLoadingText');
  const eventNotesInput = document.getElementById('eventNotesInput');
  const eventToneSelect = document.getElementById('eventToneSelect');
  const autoSaveToggle = document.getElementById('autoSaveToggle');
  const aiEventDate = document.getElementById('aiEventDate');
  const aiEventTime = document.getElementById('aiEventTime');

  async function handleAIProcess() {
    const imageFile = window.cameraManager ? window.cameraManager.getImageFile() : null;
    const audioFile = window.audioManager ? window.audioManager.getAudioFile() : null;
    const notes = eventNotesInput.value.trim();
    const tone = eventToneSelect.value;
    const autoSave = autoSaveToggle.checked;
    const targetDate = aiEventDate ? aiEventDate.value : '';
    const targetTime = aiEventTime ? aiEventTime.value : '';

    if (!imageFile && !audioFile && !notes) {
      alert('Vui lòng cung cấp ít nhất 1 dữ liệu: Chụp/Tải ảnh, Ghi âm giọng nói, hoặc Ghi chú nhanh.');
      return;
    }

    // Set UI loading state
    aiProcessBtn.disabled = true;
    aiProcessBtnText.textContent = 'Đang xử lý đa phương thức...';
    aiLoadingStatus.classList.remove('hidden');
    aiLoadingText.textContent = 'Đang tải tệp hình ảnh & âm thanh lên...';

    const stages = [
      'AI đang quan sát ảnh & lắng nghe từng câu chữ trong giọng nói...',
      'Đang đúc kết cảm xúc & xây dựng mạch truyện nhật ký...',
      'Đang hoàn tất bài viết nhật ký...'
    ];
    let stageIdx = 0;
    const stageTimer = setInterval(() => {
      if (stageIdx < stages.length) {
        aiLoadingText.textContent = stages[stageIdx++];
      }
    }, 2500);

    try {
      const formData = new FormData();
      if (imageFile) {
        formData.append('image', imageFile);
      }
      if (audioFile) {
        formData.append('audio', audioFile);
      }
      if (notes) {
        formData.append('notes', notes);
      }
      if (targetDate) {
        formData.append('entry_date', targetDate);
      }
      if (targetTime) {
        formData.append('entry_time', targetTime);
      }
      formData.append('tone', tone);
      formData.append('auto_save', autoSave ? 'true' : 'false');

      const response = await fetch('/api/ai/process-event', {
        method: 'POST',
        body: formData
      });

      clearInterval(stageTimer);

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(errorData.detail || `Lỗi máy chủ (${response.status})`);
      }

      const result = await response.json();

      // Reset loading UI
      aiLoadingStatus.classList.add('hidden');
      aiProcessBtn.disabled = false;
      aiProcessBtnText.textContent = 'AI Tự Động Tóm Tắt & Viết Nhật Ký Ngày';

      if (result.auto_saved && result.entry) {
        // Clear inputs
        if (window.cameraManager) window.cameraManager.clear();
        if (window.audioManager) window.audioManager.clear();
        eventNotesInput.value = '';

        // Notify user
        const isPast = targetDate && targetDate < new Date().toISOString().split('T')[0];
        const msg = isPast ? `✨ Đã lưu nhật ký cho ngày quá khứ (${targetDate})!` : '✨ Đã tạo và lưu nhật ký thành công!';
        showToast(msg, 'success');

        // Refresh timeline and switch date filter if writing for past date
        if (window.appController) {
          if (targetDate) {
            window.appController.setSelectedDate(targetDate);
          }
          await window.appController.loadStats();
          await window.appController.loadDates();
          await window.appController.loadEntries();
        }
      } else {
        // Switch to manual tab and prefill
        if (window.appController) {
          window.appController.switchToManualTab(result.ai_result, result.image_path, result.audio_path);
        }
        showToast('Đã tạo bản nháp AI, bạn có thể xem lại trước khi lưu!', 'info');
      }

    } catch (err) {
      clearInterval(stageTimer);
      aiLoadingStatus.classList.add('hidden');
      aiProcessBtn.disabled = false;
      aiProcessBtnText.textContent = 'AI Tự Động Tóm Tắt & Viết Nhật Ký Ngày';
      console.error('AI Processing error:', err);
      alert('Không thể hoàn thành xử lý AI: ' + (err.message || 'Lỗi không xác định'));
    }
  }

  function showToast(message, type = 'info') {
    const toast = document.createElement('div');
    const bgClass = type === 'success' ? 'bg-emerald-600' : 'bg-purple-600';
    toast.className = `fixed bottom-6 right-6 z-50 px-5 py-3 rounded-2xl text-white font-medium text-sm shadow-2xl flex items-center space-x-2 transition-all transform duration-300 translate-y-10 opacity-0 ${bgClass}`;
    toast.innerHTML = `<i class="fa-solid fa-circle-check text-base"></i><span>${message}</span>`;
    document.body.appendChild(toast);

    setTimeout(() => {
      toast.classList.remove('translate-y-10', 'opacity-0');
    }, 10);

    setTimeout(() => {
      toast.classList.add('translate-y-10', 'opacity-0');
      setTimeout(() => toast.remove(), 300);
    }, 3500);
  }

  aiProcessBtn.addEventListener('click', handleAIProcess);

  window.aiCoordinator = {
    showToast
  };
})();
