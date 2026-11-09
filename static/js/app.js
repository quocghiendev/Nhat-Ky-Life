// Main App Controller
(function() {
  // DOM Elements
  const clockText = document.getElementById('clockText');
  const themeToggleBtn = document.getElementById('themeToggleBtn');
  const themeIcon = document.getElementById('themeIcon');
  
  const statDays = document.getElementById('statDays');
  const statEntries = document.getElementById('statEntries');
  const statImages = document.getElementById('statImages');
  const statAudios = document.getElementById('statAudios');
  
  const tabAiModeBtn = document.getElementById('tabAiModeBtn');
  const tabManualModeBtn = document.getElementById('tabManualModeBtn');
  const aiModeSection = document.getElementById('aiModeSection');
  const manualModeSection = document.getElementById('manualModeSection');

  // AI Event Time Elements (Supporting Past & Real-time entries)
  const aiEventDate = document.getElementById('aiEventDate');
  const aiEventTime = document.getElementById('aiEventTime');
  const aiSetNowBtn = document.getElementById('aiSetNowBtn');
  const aiSetYesterdayBtn = document.getElementById('aiSetYesterdayBtn');
  const aiPastDateBanner = document.getElementById('aiPastDateBanner');
  const aiPastDateText = document.getElementById('aiPastDateText');
  
  const manualEntryForm = document.getElementById('manualEntryForm');
  const manualTitle = document.getElementById('manualTitle');
  const manualDate = document.getElementById('manualDate');
  const manualTime = document.getElementById('manualTime');
  const manualContent = document.getElementById('manualContent');
  const manualMood = document.getElementById('manualMood');
  const manualTags = document.getElementById('manualTags');
  const manualTimeOfDay = document.getElementById('manualTimeOfDay');

  const dateFilterSelect = document.getElementById('dateFilterSelect');
  const todayQuickBtn = document.getElementById('todayQuickBtn');
  const searchInput = document.getElementById('searchInput');
  const filterFavoritesBtn = document.getElementById('filterFavoritesBtn');

  const dailySummaryCard = document.getElementById('dailySummaryCard');
  const dailySummaryMood = document.getElementById('dailySummaryMood');
  const dailySummaryText = document.getElementById('dailySummaryText');
  const dailySummaryHighlights = document.getElementById('dailySummaryHighlights');
  const refreshDailySummaryBtn = document.getElementById('refreshDailySummaryBtn');

  const timelineContainer = document.getElementById('timelineContainer');
  const emptyState = document.getElementById('emptyState');

  // Settings Modal elements
  const openSettingsBtn = document.getElementById('openSettingsBtn');
  const closeSettingsBtn = document.getElementById('closeSettingsBtn');
  const settingsModal = document.getElementById('settingsModal');
  const selectGeminiProviderBtn = document.getElementById('selectGeminiProviderBtn');
  const selectOpenaiProviderBtn = document.getElementById('selectOpenaiProviderBtn');
  const geminiSettingsFields = document.getElementById('geminiSettingsFields');
  const openaiSettingsFields = document.getElementById('openaiSettingsFields');
  const geminiApiKeyInput = document.getElementById('geminiApiKeyInput');
  const openaiApiKeyInput = document.getElementById('openaiApiKeyInput');
  const geminiModelSelect = document.getElementById('geminiModelSelect');
  const openaiModelSelect = document.getElementById('openaiModelSelect');
  const toggleGeminiKeyVisibility = document.getElementById('toggleGeminiKeyVisibility');
  const testApiKeyBtn = document.getElementById('testApiKeyBtn');
  const testResultMsg = document.getElementById('testResultMsg');
  const saveSettingsBtn = document.getElementById('saveSettingsBtn');
  const apiKeyStatusDot = document.getElementById('apiKeyStatusDot');
  const geminiKeyStatusText = document.getElementById('geminiKeyStatusText');

  // Edit Modal elements
  const editModal = document.getElementById('editModal');
  const closeEditModalBtn = document.getElementById('closeEditModalBtn');
  const cancelEditBtn = document.getElementById('cancelEditBtn');
  const editEntryForm = document.getElementById('editEntryForm');
  const editEntryId = document.getElementById('editEntryId');
  const editTitle = document.getElementById('editTitle');
  const editContent = document.getElementById('editContent');
  const editMood = document.getElementById('editMood');
  const editTags = document.getElementById('editTags');

  // Lightbox elements
  const lightboxModal = document.getElementById('lightboxModal');
  const lightboxImg = document.getElementById('lightboxImg');

  // State
  let currentSettings = {};
  let selectedDate = '';
  let onlyFavorites = false;
  let manualUploadedImagePath = '';
  let manualUploadedAudioPath = '';

  // 1. Live Clock
  function updateLiveClock() {
    const now = new Date();
    clockText.textContent = now.toLocaleTimeString('vi-VN', { hour12: false });
  }
  setInterval(updateLiveClock, 1000);
  updateLiveClock();

  // 2. Theme Toggle
  const isDark = localStorage.getItem('theme') !== 'light';
  applyTheme(isDark);

  function applyTheme(dark) {
    if (dark) {
      document.documentElement.classList.add('dark');
      themeIcon.className = 'fa-solid fa-moon';
      localStorage.setItem('theme', 'dark');
    } else {
      document.documentElement.classList.remove('dark');
      themeIcon.className = 'fa-solid fa-sun';
      localStorage.setItem('theme', 'light');
    }
  }

  themeToggleBtn.addEventListener('click', () => {
    const currentlyDark = document.documentElement.classList.contains('dark');
    applyTheme(!currentlyDark);
  });

  // 3. Tab switching (AI Mode vs Manual Mode)
  tabAiModeBtn.addEventListener('click', () => {
    tabAiModeBtn.className = 'px-3.5 py-1.5 rounded-lg bg-gradient-to-r from-purple-600 to-indigo-600 text-white shadow-sm flex items-center space-x-1.5 transition';
    tabManualModeBtn.className = 'px-3.5 py-1.5 rounded-lg text-slate-400 hover:text-slate-200 flex items-center space-x-1.5 transition';
    aiModeSection.classList.remove('hidden');
    manualModeSection.classList.add('hidden');
  });

  tabManualModeBtn.addEventListener('click', () => {
    tabManualModeBtn.className = 'px-3.5 py-1.5 rounded-lg bg-gradient-to-r from-purple-600 to-indigo-600 text-white shadow-sm flex items-center space-x-1.5 transition';
    tabAiModeBtn.className = 'px-3.5 py-1.5 rounded-lg text-slate-400 hover:text-slate-200 flex items-center space-x-1.5 transition';
    manualModeSection.classList.remove('hidden');
    aiModeSection.classList.add('hidden');

    const now = new Date();
    manualDate.value = now.toISOString().split('T')[0];
    manualTime.value = now.toTimeString().slice(0, 5);
  });

  // AI Event Time management (Real-time & Past dates)
  function initAiDateTime() {
    const now = new Date();
    if (aiEventDate && !aiEventDate.value) {
      aiEventDate.value = now.toISOString().split('T')[0];
    }
    if (aiEventTime && !aiEventTime.value) {
      aiEventTime.value = now.toTimeString().slice(0, 5);
    }
    checkPastDateStatus();
  }

  function checkPastDateStatus() {
    if (!aiEventDate || !aiPastDateBanner) return;
    const todayStr = new Date().toISOString().split('T')[0];
    const chosen = aiEventDate.value;
    if (chosen && chosen < todayStr) {
      aiPastDateBanner.classList.remove('hidden');
      if (aiPastDateText) {
        aiPastDateText.innerHTML = `Bạn đang viết nhật ký cho ngày <b>${chosen} (QUÁ KHỨ)</b>. AI sẽ tự động điều chỉnh văn phong hoài niệm và hồi tưởng.`;
      }
    } else {
      aiPastDateBanner.classList.add('hidden');
    }
  }

  if (aiSetNowBtn) {
    aiSetNowBtn.addEventListener('click', () => {
      const now = new Date();
      if (aiEventDate) aiEventDate.value = now.toISOString().split('T')[0];
      if (aiEventTime) aiEventTime.value = now.toTimeString().slice(0, 5);
      checkPastDateStatus();
      if (window.aiCoordinator) window.aiCoordinator.showToast('Đã đặt thời điểm: Bây giờ (Thời gian thực)', 'info');
    });
  }

  if (aiSetYesterdayBtn) {
    aiSetYesterdayBtn.addEventListener('click', () => {
      const y = new Date();
      y.setDate(y.getDate() - 1);
      if (aiEventDate) aiEventDate.value = y.toISOString().split('T')[0];
      checkPastDateStatus();
      if (window.aiCoordinator) window.aiCoordinator.showToast('Đã chọn thời điểm: Hôm qua', 'info');
    });
  }

  if (aiEventDate) {
    aiEventDate.addEventListener('change', checkPastDateStatus);
  }

  initAiDateTime();

  // 4. Load Stats
  async function loadStats() {
    try {
      const resp = await fetch('/api/entries/stats');
      const data = await resp.json();
      statDays.textContent = data.total_days;
      statEntries.textContent = data.total_entries;
      statImages.textContent = data.total_images;
      statAudios.textContent = data.total_audios;
    } catch (e) {
      console.error('Failed to load stats:', e);
    }
  }

  // 5. Load Dates
  async function loadDates() {
    try {
      const resp = await fetch('/api/entries/dates');
      const data = await resp.json();
      const dates = data.dates || [];

      const currentVal = dateFilterSelect.value;
      dateFilterSelect.innerHTML = '<option value="">Tất cả các ngày</option>';

      const todayStr = new Date().toISOString().split('T')[0];
      let hasToday = false;

      dates.forEach(d => {
        if (d.date === todayStr) hasToday = true;
        const opt = document.createElement('option');
        opt.value = d.date;
        const display = (d.date === todayStr) ? `Hôm nay (${d.date})` : d.date;
        opt.textContent = `${display} (${d.count} mục)`;
        dateFilterSelect.appendChild(opt);
      });

      if (!hasToday) {
        const todayOpt = document.createElement('option');
        todayOpt.value = todayStr;
        todayOpt.textContent = `Hôm nay (${todayStr}) (0 mục)`;
        dateFilterSelect.insertBefore(todayOpt, dateFilterSelect.children[1] || null);
      }

      if (currentVal) {
        dateFilterSelect.value = currentVal;
      }
    } catch (e) {
      console.error('Failed to load dates:', e);
    }
  }

  // 6. Load Entries & Render Timeline
  async function loadEntries() {
    const keyword = searchInput.value.trim();
    let url = `/api/entries?limit=100`;
    if (selectedDate) url += `&date=${encodeURIComponent(selectedDate)}`;
    if (keyword) url += `&keyword=${encodeURIComponent(keyword)}`;

    try {
      const resp = await fetch(url);
      const data = await resp.json();
      let entries = data.entries || [];

      if (onlyFavorites) {
        entries = entries.filter(e => e.is_favorite);
      }

      renderTimeline(entries);
      checkAndLoadDailySummary(selectedDate);
    } catch (e) {
      console.error('Failed to load entries:', e);
    }
  }

  function renderTimeline(entries) {
    timelineContainer.innerHTML = '';

    if (entries.length === 0) {
      emptyState.classList.remove('hidden');
      return;
    }
    emptyState.classList.add('hidden');

    entries.forEach(entry => {
      const item = document.createElement('div');
      item.className = 'timeline-item bg-slate-900/70 backdrop-blur border border-slate-800 rounded-3xl p-5 md:p-6 transition hover:border-purple-500/40 glow-card';
      item.id = `entry-${entry.id}`;

      // Mood badge & Dot color
      const moodEmoji = entry.mood_emoji || '🌿';
      const moodText = entry.mood || 'Bình yên';
      const timeOfDay = entry.time_of_day || 'Ngày';

      // Parse tags
      const tagsArray = entry.tags ? entry.tags.split(',').map(t => t.trim()).filter(Boolean) : [];
      const tagsHtml = tagsArray.map(t => `<span class="inline-block bg-purple-500/10 text-purple-300 text-[11px] font-semibold px-2.5 py-0.5 rounded-lg border border-purple-500/20">#${t}</span>`).join(' ');

      // Image element
      let imageHtml = '';
      if (entry.image_path) {
        imageHtml = `
          <div class="mb-4 rounded-2xl overflow-hidden border border-slate-800 group relative max-h-96 bg-black/40">
            <img src="${entry.image_path}" alt="${entry.title}" class="w-full h-auto max-h-96 object-cover cursor-pointer transition duration-300 group-hover:scale-[1.02]" onclick="window.appController.openLightbox('${entry.image_path}')">
            <div class="absolute bottom-2 right-2 bg-slate-950/70 backdrop-blur px-2 py-1 rounded-lg text-[11px] text-slate-300 flex items-center space-x-1 pointer-events-none">
              <i class="fa-solid fa-expand"></i>
              <span>Xem phóng to</span>
            </div>
          </div>
        `;
      }

      // Audio element
      let audioHtml = '';
      if (entry.audio_path) {
        audioHtml = `
          <div class="mb-4 p-3 bg-slate-950/70 border border-slate-800/80 rounded-2xl flex items-center space-x-3">
            <div class="w-10 h-10 rounded-xl bg-pink-500/10 text-pink-400 flex items-center justify-center shrink-0">
              <i class="fa-solid fa-microphone"></i>
            </div>
            <div class="flex-1">
              <div class="text-xs font-semibold text-slate-300 mb-1">Ghi âm khoảnh khắc gốc:</div>
              <audio src="${entry.audio_path}" controls class="w-full h-8"></audio>
            </div>
          </div>
        `;
      }

      // Transcript accordion (if available)
      let transcriptHtml = '';
      if (entry.raw_transcript && entry.raw_transcript.trim()) {
        transcriptHtml = `
          <details class="mb-4 text-xs bg-slate-950/40 border border-slate-800/50 rounded-xl p-2.5">
            <summary class="cursor-pointer font-semibold text-purple-300 hover:text-purple-200 select-none flex items-center space-x-1.5">
              <i class="fa-solid fa-align-left"></i>
              <span>Xem gỡ băng lời nói gốc</span>
            </summary>
            <p class="mt-2 text-slate-300 italic pl-2 border-l border-purple-500/40 whitespace-pre-wrap">${escapeHtml(entry.raw_transcript)}</p>
          </details>
        `;
      }

      // Star favorite styling
      const favClass = entry.is_favorite ? 'fa-solid fa-star text-amber-400' : 'fa-regular fa-star text-slate-500 hover:text-amber-400';

      item.innerHTML = `
        <!-- Timeline dot -->
        <div class="timeline-dot bg-purple-500"></div>

        <!-- Entry Header -->
        <div class="flex flex-col sm:flex-row sm:items-center justify-between pb-3 mb-3 border-b border-slate-800/80 gap-2">
          <div class="flex items-center flex-wrap gap-2">
            <span class="text-xs font-mono font-bold px-2.5 py-1 rounded-xl bg-purple-500/10 text-purple-300 border border-purple-500/20">
              <i class="fa-regular fa-clock mr-1"></i>${entry.entry_time.slice(0, 5)} &bull; ${timeOfDay}
            </span>
            <span class="text-xs px-2.5 py-1 rounded-xl bg-slate-800/80 text-slate-300">
              ${moodEmoji} ${moodText}
            </span>
            ${entry.ai_generated ? '<span class="text-[11px] px-2 py-0.5 rounded-lg bg-indigo-500/10 text-indigo-300 font-semibold border border-indigo-500/20"><i class="fa-solid fa-wand-magic-sparkles mr-1 text-amber-300"></i>AI Tóm tắt</span>' : ''}
            <span class="text-xs text-slate-500">${entry.entry_date}</span>
          </div>

          <!-- Actions -->
          <div class="flex items-center space-x-1 self-end sm:self-auto">
            <button onclick="window.appController.toggleFav(${entry.id})" title="Yêu thích" class="p-1.5 rounded-lg hover:bg-slate-800 transition">
              <i class="${favClass}"></i>
            </button>
            <button onclick="window.appController.openEdit(${entry.id})" title="Chỉnh sửa" class="p-1.5 rounded-lg text-slate-500 hover:text-slate-200 hover:bg-slate-800 transition">
              <i class="fa-solid fa-pen"></i>
            </button>
            <button onclick="window.appController.deleteEntry(${entry.id})" title="Xóa" class="p-1.5 rounded-lg text-slate-500 hover:text-rose-400 hover:bg-slate-800 transition">
              <i class="fa-solid fa-trash-can"></i>
            </button>
          </div>
        </div>

        <!-- Entry Title -->
        <h3 class="text-lg md:text-xl font-bold text-slate-100 mb-3 font-serif tracking-tight">
          ${escapeHtml(entry.title)}
        </h3>

        <!-- Media: Photo & Voice -->
        ${imageHtml}
        ${audioHtml}

        <!-- Entry Content -->
        <div class="text-sm md:text-base text-slate-300 leading-relaxed font-sans mb-4 whitespace-pre-wrap">
          ${escapeHtml(entry.content)}
        </div>

        <!-- Transcript if available -->
        ${transcriptHtml}

        <!-- Tags footer -->
        ${tagsHtml ? `<div class="flex flex-wrap gap-1.5 pt-2 border-t border-slate-800/40">${tagsHtml}</div>` : ''}
      `;

      timelineContainer.appendChild(item);
    });
  }

  // 7. Check and load Daily Summary
  async function checkAndLoadDailySummary(date) {
    if (!date) {
      dailySummaryCard.classList.add('hidden');
      return;
    }

    try {
      const resp = await fetch(`/api/ai/daily-summary/${encodeURIComponent(date)}`);
      const data = await resp.json();

      if (data.summary && data.summary.summary) {
        dailySummaryText.textContent = `“${data.summary.summary}”`;
        dailySummaryMood.textContent = data.summary.mood_overview || '';
        dailySummaryHighlights.textContent = data.summary.highlights ? `Điểm nhấn: ${data.summary.highlights}` : '';
        dailySummaryCard.classList.remove('hidden');
      } else {
        dailySummaryCard.classList.add('hidden');
      }
    } catch (e) {
      console.error('Error fetching daily summary:', e);
      dailySummaryCard.classList.add('hidden');
    }
  }

  refreshDailySummaryBtn.addEventListener('click', async () => {
    const dateToSummarize = selectedDate || new Date().toISOString().split('T')[0];
    refreshDailySummaryBtn.disabled = true;
    refreshDailySummaryBtn.innerHTML = '<i class="fa-solid fa-spinner animate-spin"></i><span>Đang tạo tổng kết...</span>';

    try {
      const resp = await fetch('/api/ai/daily-summary', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ date: dateToSummarize })
      });
      const data = await resp.json();

      dailySummaryText.textContent = `“${data.summary}”`;
      dailySummaryMood.textContent = data.mood_overview || '';
      dailySummaryHighlights.textContent = data.highlights ? `Điểm nhấn: ${data.highlights}` : '';
      dailySummaryCard.classList.remove('hidden');

      if (window.aiCoordinator) window.aiCoordinator.showToast('Đã cập nhật AI tổng kết ngày!', 'success');
    } catch (e) {
      alert('Không thể tạo tổng kết ngày: ' + e.message);
    } finally {
      refreshDailySummaryBtn.disabled = false;
      refreshDailySummaryBtn.innerHTML = '<i class="fa-solid fa-rotate-right"></i><span>Tạo lại tổng kết AI</span>';
    }
  });

  // 8. Filters & Search listeners
  dateFilterSelect.addEventListener('change', () => {
    selectedDate = dateFilterSelect.value;
    loadEntries();
  });

  todayQuickBtn.addEventListener('click', () => {
    const todayStr = new Date().toISOString().split('T')[0];
    dateFilterSelect.value = todayStr;
    selectedDate = todayStr;
    loadEntries();
  });

  searchInput.addEventListener('input', debounce(loadEntries, 300));

  filterFavoritesBtn.addEventListener('click', () => {
    onlyFavorites = !onlyFavorites;
    filterFavoritesBtn.className = onlyFavorites 
      ? 'p-2 rounded-xl bg-amber-500/20 border border-amber-500/40 text-amber-400 transition'
      : 'p-2 rounded-xl bg-slate-900 border border-slate-800 hover:bg-slate-800 text-slate-400 hover:text-amber-400 transition';
    loadEntries();
  });

  // 9. Manual Entry Form Submit
  manualEntryForm.addEventListener('submit', async (e) => {
    e.preventDefault();
    const moodVal = manualMood.value.split('|');
    const payload = {
      title: manualTitle.value.trim(),
      content: manualContent.value.trim(),
      entry_date: manualDate.value,
      entry_time: manualTime.value + ':00',
      mood: moodVal[0],
      mood_emoji: moodVal[1],
      tags: manualTags.value.trim(),
      time_of_day: manualTimeOfDay.value,
      image_path: manualUploadedImagePath,
      audio_path: manualUploadedAudioPath,
      ai_generated: false
    };

    try {
      const resp = await fetch('/api/entries', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
      });
      if (resp.ok) {
        manualEntryForm.reset();
        manualUploadedImagePath = '';
        manualUploadedAudioPath = '';
        tabAiModeBtn.click();
        if (window.aiCoordinator) window.aiCoordinator.showToast('Đã lưu nhật ký thành công!', 'success');
        await loadStats();
        await loadDates();
        await loadEntries();
      } else {
        alert('Lỗi lưu nhật ký.');
      }
    } catch (err) {
      alert('Không thể lưu: ' + err.message);
    }
  });

  // 10. Settings Management
  async function loadSettings() {
    try {
      const resp = await fetch('/api/settings');
      currentSettings = await resp.json();

      // Update UI
      if (currentSettings.ai_provider === 'gemini') {
        selectGeminiProvider();
      } else {
        selectOpenaiProvider();
      }

      geminiModelSelect.value = currentSettings.gemini_model || 'gemini-2.5-flash';
      openaiModelSelect.value = currentSettings.openai_model || 'gpt-4o-mini';

      if (currentSettings.has_gemini_key) {
        apiKeyStatusDot.className = 'w-2 h-2 rounded-full bg-emerald-400';
        geminiKeyStatusText.textContent = `✓ Đã lưu Key: ${currentSettings.gemini_api_key_masked}`;
        geminiKeyStatusText.className = 'text-[11px] text-emerald-400 mt-1';
      } else {
        apiKeyStatusDot.className = 'w-2 h-2 rounded-full bg-amber-400';
        geminiKeyStatusText.textContent = 'Chưa có Key (Hệ thống sẽ chạy ở chế độ mô phỏng thông minh)';
        geminiKeyStatusText.className = 'text-[11px] text-amber-400 mt-1';
      }
    } catch (e) {
      console.error('Failed to load settings:', e);
    }
  }

  function selectGeminiProvider() {
    selectGeminiProviderBtn.className = 'p-2.5 rounded-xl border border-purple-500 bg-purple-500/10 text-purple-300 text-xs font-bold flex items-center justify-center space-x-1.5';
    selectOpenaiProviderBtn.className = 'p-2.5 rounded-xl border border-slate-800 bg-slate-950/60 text-slate-400 text-xs font-bold flex items-center justify-center space-x-1.5';
    geminiSettingsFields.classList.remove('hidden');
    openaiSettingsFields.classList.add('hidden');
  }

  function selectOpenaiProvider() {
    selectOpenaiProviderBtn.className = 'p-2.5 rounded-xl border border-purple-500 bg-purple-500/10 text-purple-300 text-xs font-bold flex items-center justify-center space-x-1.5';
    selectGeminiProviderBtn.className = 'p-2.5 rounded-xl border border-slate-800 bg-slate-950/60 text-slate-400 text-xs font-bold flex items-center justify-center space-x-1.5';
    openaiSettingsFields.classList.remove('hidden');
    geminiSettingsFields.classList.add('hidden');
  }

  selectGeminiProviderBtn.addEventListener('click', selectGeminiProvider);
  selectOpenaiProviderBtn.addEventListener('click', selectOpenaiProvider);

  toggleGeminiKeyVisibility.addEventListener('click', () => {
    const isPass = geminiApiKeyInput.type === 'password';
    geminiApiKeyInput.type = isPass ? 'text' : 'password';
    toggleGeminiKeyVisibility.innerHTML = isPass ? '<i class="fa-solid fa-eye-slash"></i>' : '<i class="fa-solid fa-eye"></i>';
  });

  openSettingsBtn.addEventListener('click', () => {
    settingsModal.classList.remove('hidden');
    testResultMsg.classList.add('hidden');
  });

  closeSettingsBtn.addEventListener('click', () => {
    settingsModal.classList.add('hidden');
  });

  testApiKeyBtn.addEventListener('click', async () => {
    const isGemini = !geminiSettingsFields.classList.contains('hidden');
    const provider = isGemini ? 'gemini' : 'openai';
    const apiKey = isGemini ? geminiApiKeyInput.value.trim() : openaiApiKeyInput.value.trim();
    const model = isGemini ? geminiModelSelect.value : openaiModelSelect.value;

    if (!apiKey) {
      testResultMsg.textContent = 'Vui lòng nhập API Key trước khi kiểm tra.';
      testResultMsg.className = 'text-xs mt-2 text-center text-amber-400 block';
      return;
    }

    testApiKeyBtn.disabled = true;
    testApiKeyBtn.innerHTML = '<i class="fa-solid fa-spinner animate-spin"></i><span>Đang kiểm tra kết nối...</span>';
    testResultMsg.classList.add('hidden');

    try {
      const resp = await fetch('/api/settings/test-key', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ provider, api_key: apiKey, model })
      });
      const data = await resp.json();

      if (data.valid) {
        testResultMsg.textContent = '✓ ' + data.message;
        testResultMsg.className = 'text-xs mt-2 text-center text-emerald-400 font-semibold block';
      } else {
        testResultMsg.textContent = '✗ ' + data.message;
        testResultMsg.className = 'text-xs mt-2 text-center text-rose-400 block';
      }
    } catch (err) {
      testResultMsg.textContent = 'Lỗi kết nối mạng: ' + err.message;
      testResultMsg.className = 'text-xs mt-2 text-center text-rose-400 block';
    } finally {
      testApiKeyBtn.disabled = false;
      testApiKeyBtn.innerHTML = '<i class="fa-solid fa-circle-check text-emerald-400"></i><span>Kiểm tra kết nối API Key</span>';
    }
  });

  saveSettingsBtn.addEventListener('click', async () => {
    const isGemini = !geminiSettingsFields.classList.contains('hidden');
    const provider = isGemini ? 'gemini' : 'openai';
    const payload = {
      ai_provider: provider,
      gemini_model: geminiModelSelect.value,
      openai_model: openaiModelSelect.value
    };

    if (geminiApiKeyInput.value.trim()) {
      payload.gemini_api_key = geminiApiKeyInput.value.trim();
    }
    if (openaiApiKeyInput.value.trim()) {
      payload.openai_api_key = openaiApiKeyInput.value.trim();
    }

    try {
      const resp = await fetch('/api/settings', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
      });
      if (resp.ok) {
        settingsModal.classList.add('hidden');
        if (window.aiCoordinator) window.aiCoordinator.showToast('Đã lưu cấu hình AI thành công!', 'success');
        await loadSettings();
      }
    } catch (e) {
      alert('Không thể lưu cài đặt: ' + e.message);
    }
  });

  // 11. Edit Entry Modal
  async function openEdit(entryId) {
    try {
      const resp = await fetch(`/api/entries/${entryId}`);
      const entry = await resp.json();
      editEntryId.value = entry.id;
      editTitle.value = entry.title;
      editContent.value = entry.content;
      editMood.value = entry.mood;
      editTags.value = entry.tags;
      editModal.classList.remove('hidden');
    } catch (e) {
      alert('Không thể lấy thông tin mục nhật ký: ' + e.message);
    }
  }

  closeEditModalBtn.addEventListener('click', () => editModal.classList.add('hidden'));
  cancelEditBtn.addEventListener('click', () => editModal.classList.add('hidden'));

  editEntryForm.addEventListener('submit', async (e) => {
    e.preventDefault();
    const id = editEntryId.value;
    const payload = {
      title: editTitle.value.trim(),
      content: editContent.value.trim(),
      mood: editMood.value.trim(),
      tags: editTags.value.trim()
    };

    try {
      const resp = await fetch(`/api/entries/${id}`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
      });
      if (resp.ok) {
        editModal.classList.add('hidden');
        if (window.aiCoordinator) window.aiCoordinator.showToast('Đã cập nhật mục nhật ký!', 'success');
        loadEntries();
      }
    } catch (e) {
      alert('Lỗi cập nhật: ' + e.message);
    }
  });

  // 12. Delete Entry
  async function deleteEntry(entryId) {
    if (!confirm('Bạn có chắc chắn muốn xóa mục nhật ký này?')) return;
    try {
      const resp = await fetch(`/api/entries/${entryId}`, { method: 'DELETE' });
      if (resp.ok) {
        if (window.aiCoordinator) window.aiCoordinator.showToast('Đã xóa mục nhật ký!', 'info');
        await loadStats();
        await loadDates();
        await loadEntries();
      }
    } catch (e) {
      alert('Lỗi xóa: ' + e.message);
    }
  }

  // 13. Favorite Toggle
  async function toggleFav(entryId) {
    try {
      const resp = await fetch(`/api/entries/${entryId}/toggle-favorite`, { method: 'POST' });
      if (resp.ok) {
        loadEntries();
        loadStats();
      }
    } catch (e) {
      console.error('Error toggling favorite:', e);
    }
  }

  // 14. Lightbox Photo viewer
  function openLightbox(src) {
    lightboxImg.src = src;
    lightboxModal.classList.remove('hidden');
  }

  lightboxModal.addEventListener('click', () => {
    lightboxModal.classList.add('hidden');
    lightboxImg.src = '';
  });

  // Utility helpers
  function escapeHtml(str) {
    if (!str) return '';
    return str
      .replace(/&/g, '&amp;')
      .replace(/</g, '&lt;')
      .replace(/>/g, '&gt;')
      .replace(/"/g, '&quot;')
      .replace(/'/g, '&#039;');
  }

  function debounce(fn, delay) {
    let timer = null;
    return function(...args) {
      clearTimeout(timer);
      timer = setTimeout(() => fn.apply(this, args), delay);
    };
  }

  // Expose controller methods
  window.appController = {
    loadStats,
    loadDates,
    loadEntries,
    openEdit,
    deleteEntry,
    toggleFav,
    openLightbox,
    setSelectedDate: (date) => {
      selectedDate = date;
      if (dateFilterSelect) dateFilterSelect.value = date;
    },
    switchToManualTab: (aiResult, imgPath, audioPath) => {
      tabManualModeBtn.click();
      if (aiResult) {
        manualTitle.value = aiResult.title || '';
        manualContent.value = aiResult.content || '';
        manualTags.value = Array.isArray(aiResult.tags) ? aiResult.tags.join(', ') : (aiResult.tags || '');
        if (aiResult.mood && aiResult.mood_emoji) {
          manualMood.value = `${aiResult.mood}|${aiResult.mood_emoji}`;
        }
      }
      manualUploadedImagePath = imgPath || '';
      manualUploadedAudioPath = audioPath || '';
    }
  };

  // Initial load
  loadSettings();
  loadStats();
  loadDates();
  loadEntries();

})();
