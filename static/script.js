let selectedMode = null;
let isDarkMode = false;
let currentLanguage = 'ar';

const translations = {
    'ar': {
        'title': 'Nazzel',
        'heading': 'أهلاً بك في Nazzel',
        'description': 'مع Nazzel، حمّل فيديوهاتك وصوتياتك المفضلة من يوتيوب، إنستغرام، تيك توك، وفيسبوك بسهولة وسرعة!',
        'placeholder.url': 'أدخل الرابط هنا',
        'paste': 'لصق',
        'auto': 'تلقائي',
        'audio': 'صوت فقط',
        'trim': 'جزء من الفيديو/الصوت',
        'trim.video': 'فيديو',
        'trim.audio': 'صوت',
        'preview': 'معاينة',
        'loading.preview': 'جاري المعاينة، يرجى التحلي بالصبر...',
        'duration': 'المدة',
        'quality.select': 'اختر الجودة:',
        'download': 'تحميل',
        'ok': 'موافق',
        'loading.download': 'جاري التحميل، يرجى التحلي بالصبر... ولا تنسى الاستغفار',
        'mute.developing': 'وظيفة كتم الصوت قيد التطوير!',
        'paste.failed': 'فشل لصق النص: ',
        'mode.select': 'يرجى اختيار وضع التحميل (تلقائي، صوت فقط، أو جزء من الفيديو/الصوت)!',
        'error': 'خطأ: ',
        'success.video': 'تم تحميل الفيديو بنجاح!',
        'success.audio': 'تم تحميل الصوت بنجاح!',
        'copyright': '© 2025 جميع الحقوق محفوظة للمهندس حسان ضعيف',
        'invalid.url': 'الرابط غير صالح.',
        'download.error': 'فشل التنزيل. يرجى التحقق من الرابط وحاول مرة أخرى.',
        'minutes': 'دقيقة',
        'audioOnlyText': 'صوت فقط',
        'trim.start': 'وقت البداية (دقائق:ثواني):',
        'trim.end': 'وقت النهاية (دقائق:ثواني):',
        'invalid.time.format': 'يرجى إدخال الوقت بصيغة صحيحة (MM:SS)', // Added translation
        'end.time.after.start': 'وقت النهاية يجب أن يكون أكبر من وقت البداية.', // Added translation
        'legal_notice': 'يرجى استخدام Nazzel وفقًا لشروط المنصات. نحن غير مسؤولين عن الاستخدام غير القانوني. ويرجى استخدام الموقع بما يرضي الله.',
        'legal_notice_title': 'إشعار قانوني',
        'footer_legal_notice': 'عرض الإشعار القانوني'
    },
    'en': {
        'title': 'Nazzel',
        'heading': 'Welcome to Nazzel',
        'description': 'With Nazzel, download your favorite videos and audios from YouTube, Instagram, TikTok, and Facebook easily and quickly!',
        'placeholder.url': 'Enter the link here',
        'paste': 'Paste',
        'auto': 'Auto',
        'audio': 'Audio Only',
        'trim': 'Part of Video/Audio',
        'trim.video': 'Video',
        'trim.audio': 'Audio',
        'preview': 'Preview',
        'loading.preview': 'Previewing, please be patient...',
        'duration': 'Duration',
        'quality.select': 'Select Quality:',
        'download': 'Download',
        'ok': 'OK',
        'loading.download': 'Downloading, please be patient... and remember to seek forgiveness',
        'mute.developing': 'Mute function is under development!',
        'paste.failed': 'Failed to paste text: ',
        'mode.select': 'Please select a download mode (auto, audio only, or part of video/audio)!',
        'error': 'Error: ',
        'success.video': 'Video downloaded successfully!',
        'success.audio': 'Audio downloaded successfully!',
        'copyright': '© 2025 All rights reserved to Eng. HASSAN DAEF',
        'invalid.url': 'Invalid URL.',
        'download.error': 'Download failed. Please check the URL and try again.',
        'minutes': 'minutes',
        'audioOnlyText': 'Audio Only',
        'trim.start': 'Start Time (MM:SS):',
        'trim.end': 'End Time (MM:SS):',
        'invalid.time.format': 'Please enter time in the correct format (MM:SS)', // Added translation
        'end.time.after.start': 'End time must be greater than start time.', // Added translation
        'legal_notice': 'Please use Nazzel in accordance with platform terms. We are not responsible for illegal use. Use the site in a way that pleases God.',
        'legal_notice_title': 'Legal Notice',
        'footer_legal_notice': 'Show Legal Notice'
    },
    'tr': {
        'title': 'Nazzel',
        'heading': 'Nazzel’e Hoş Geldiniz',
        'description': 'Nazzel ile YouTube, Instagram, TikTok ve Facebook’tan favori videolarınızı ve seslerinizi kolayca ve hızlıca indirin!',
        'placeholder.url': 'Bağlantıyı Buraya Girin',
        'paste': 'Yapıştır',
        'auto': 'Otomatik',
        'audio': 'Sadece Ses',
        'trim': 'Video/Ses Parçası',
        'trim.video': 'Video',
        'trim.audio': 'Ses',
        'preview': 'Önizleme',
        'loading.preview': 'Önizleme yapılıyor, lütfen bekleyin...',
        'duration': 'Süre',
        'quality.select': 'Kalite Seçin:',
        'download': 'İndir',
        'ok': 'Tamam',
        'loading.download': 'İndiriliyor, lütfen sabırlı olun... ve af dilemeyi unutmayın',
        'mute.developing': 'Sesi kapatma özelliği geliştirme aşamasında!',
        'paste.failed': 'Metin yapıştırma başarısız: ',
        'mode.select': 'Lütfen bir indirme modu seçin (otomatik, sadece ses, veya video/ses parçası)!',
        'error': 'Hata: ',
        'success.video': 'Video başarıyla indirildi!',
        'success.audio': 'Ses başarıyla indirildi!',
        'copyright': '© 2025 Tüm hakları Eng. Hassan Daef’e aittir',
        'invalid.url': 'Geçersiz URL.',
        'download.error': 'İndirme başarısız oldu. Lütfen URL’yi kontrol edin ve tekrar deneyin.',
        'minutes': 'dakika',
        'audioOnlyText': 'Sadece Ses',
        'trim.start': 'Başlangıç Zamanı (DD:SS):',
        'trim.end': 'Bitiş Zamanı (DD:SS):',
        'invalid.time.format': 'Lütfen zamanı doğru biçimde girin (DD:SS)', // Added translation
        'end.time.after.start': 'Bitiş zamanı başlangıç zamanından büyük olmalıdır.', // Added translation
        'legal_notice': 'Lütfen Nazzel’i platform şartlarına uygun kullanın. Yasadışı kullanımdan sorumlu değiliz. Siteyi Allah’ı memnun edecek şekilde kullanın.',
        'legal_notice_title': 'Yasal Bildirim',
        'footer_legal_notice': 'Yasal Bildirimi Göster'
    }
};

function translatePage(language) {
    document.querySelectorAll('[data-i18n]').forEach(element => {
        const key = element.dataset.i18n;
        if (translations[language][key]) {
            // Handle specific element types that need innerHTML or textContent
            if (element.tagName === 'BUTTON' || element.tagName === 'LABEL' || element.tagName === 'P' || element.tagName === 'H1' || element.tagName === 'H2' || element.tagName === 'SPAN' || element.tagName === 'A') {
                 // Preserve icons if present
                 const icon = element.querySelector('i');
                 if (icon) {
                    element.innerHTML = `${icon.outerHTML} ${translations[language][key]}`;
                 } else {
                    element.textContent = translations[language][key];
                 }
            } else if (element.tagName === 'TITLE') {
                 element.textContent = translations[language][key];
            }

            if (element.placeholder) element.placeholder = translations[language][key];
        }
    });

    // Translate legal notice modal content
    const legalNoticeTitle = document.getElementById('legalNoticeTitle');
    const legalNoticeContent = document.querySelector('.legal-notice-content p');
    const legalNoticeButton = document.querySelector('.legal-notice-content button');
    if (legalNoticeTitle && translations[language]['legal_notice_title']) {
        legalNoticeTitle.textContent = translations[language]['legal_notice_title'];
    }
    if (legalNoticeContent && translations[language]['legal_notice']) {
        legalNoticeContent.textContent = translations[language]['legal_notice'];
    }
     if (legalNoticeButton && translations[language]['ok']) {
        legalNoticeButton.textContent = translations[language]['ok'];
    }

    // Translate popup buttons
    const successPopupButton = document.querySelector('#successPopup button');
    const errorPopupButton = document.querySelector('#errorPopup button');
    if (successPopupButton && translations[language]['ok']) {
        successPopupButton.textContent = translations[language]['ok'];
    }
    if (errorPopupButton && translations[language]['ok']) {
        errorPopupButton.textContent = translations[language]['ok'];
    }


    document.getElementById('htmlTag').setAttribute('dir', language === 'ar' ? 'rtl' : 'ltr');
    document.body.style.direction = language === 'ar' ? 'rtl' : 'ltr';

    adjustInputPosition(language === 'ar' ? 'rtl' : 'ltr');
    updateDurationText(); // Ensure this is called after translation
    updateAudioOnlyText(); // Ensure this is called after translation
}

function adjustInputPosition(dir) {
    const inputContainer = document.querySelector('.input-container');
    inputContainer.classList.remove('ltr-input', 'rtl-input');
    inputContainer.classList.add(dir === 'rtl' ? 'rtl-input' : 'ltr-input');
}

document.getElementById('languageButton').addEventListener('click', function() {
    if (currentLanguage === 'ar') {
        currentLanguage = 'en';
    } else if (currentLanguage === 'en') {
        currentLanguage = 'tr';
    } else {
        currentLanguage = 'ar';
    }
    translatePage(currentLanguage);
});

document.getElementById('themeToggle').addEventListener('click', function() {
    isDarkMode = !isDarkMode;
    document.documentElement.setAttribute('data-theme', isDarkMode ? 'dark' : 'light');
    document.getElementById('themeToggle').innerHTML = isDarkMode ? '<i class="fas fa-moon"></i>' : '<i class="fas fa-sun"></i>';
});

document.querySelectorAll('.options button[data-mode]').forEach(button => {
    button.addEventListener('click', function() {
        selectedMode = this.dataset.mode;
        document.getElementById('selectedMode').value = selectedMode;

        document.querySelectorAll('.options button[data-mode]').forEach(btn => {
            btn.classList.remove('selected');
        });

        this.classList.add('selected');
        document.getElementById('previewButton').disabled = false;

        // Show/hide trim fields based on mode
        const trimContainer = document.getElementById('trimContainer');
        if (selectedMode === 'trim') {
            trimContainer.style.display = 'block';
        } else {
            trimContainer.style.display = 'none';
        }
    });
});

document.getElementById('pasteButton').addEventListener('click', function() {
    navigator.clipboard.readText()
        .then(text => {
            document.getElementById('videoUrl').value = text;
        })
        .catch(err => {
            console.error('Failed to paste text: ', err);
            alert(translations[currentLanguage]['paste.failed'] + err);
        });
});

document.getElementById('previewForm').addEventListener('submit', function(e) {
    e.preventDefault();

    const url = document.getElementById('videoUrl').value;
    if (!isValidUrl(url)) {
        showErrorPopup(translations[currentLanguage]['invalid.url']);
        return;
    }

    if (!selectedMode) {
        showErrorPopup(translations[currentLanguage]['mode.select']);
        return;
    }

    document.getElementById('loading').style.display = 'block';
    document.getElementById('preview').style.display = 'none';
    document.getElementById('downloadButton').disabled = true; // Disable download initially

    const trimTypeSelection = document.getElementById('trimTypeSelection');
    const qualityContainer = document.getElementById('qualityOptions');
    qualityContainer.innerHTML = ''; // Clear previous qualities

    if (selectedMode === 'trim') {
        document.getElementById('loading').style.display = 'none';
        document.getElementById('preview').style.display = 'block';
        // Clear preview details until trim type is selected
        document.getElementById('videoTitle').textContent = '';
        document.getElementById('thumbnail').src = ''; // Or a placeholder
        document.getElementById('duration').textContent = '';
        document.getElementById('qualityOptions').innerHTML = ''; // Clear quality options
        trimTypeSelection.style.display = 'block'; // Show trim type buttons
         // Reset trim type buttons selection
        document.querySelectorAll('#trimTypeSelection button[data-trim-type]').forEach(btn => {
            btn.classList.remove('selected');
        });
        document.getElementById('trimType').value = ''; // Clear hidden trim type
        return; // Wait for user to select trim type
    }

    // For 'auto' or 'audio' mode, fetch preview directly
    fetchPreview(url, selectedMode);
});

document.querySelectorAll('#trimTypeSelection button[data-trim-type]').forEach(button => {
    button.addEventListener('click', function() {
        const trimType = this.dataset.trimType;
        document.getElementById('trimType').value = trimType; // Set the hidden input

        // Update selected button style
        document.querySelectorAll('#trimTypeSelection button[data-trim-type]').forEach(btn => {
            btn.classList.remove('selected');
        });
        this.classList.add('selected');

        // Fetch preview information based on the URL and selected trim type (video/audio)
        const url = document.getElementById('videoUrl').value;
        fetchPreview(url, trimType); // Use trimType (video/audio) as the mode for preview fetch
    });
});

function fetchPreview(url, mode) {
    document.getElementById('loading').style.display = 'block';
    const trimTypeSelection = document.getElementById('trimTypeSelection'); // Hide selection buttons after choice
    trimTypeSelection.style.display = 'none';

    // Determine the effective mode for yt-dlp based on the context
    // If the original mode was 'trim', the 'mode' parameter here is actually 'video' or 'audio' (trimType)
    // Otherwise, it's 'auto' or 'audio'
    let fetchMode = (selectedMode === 'trim') ? mode : selectedMode;


    fetch('/preview', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/x-www-form-urlencoded'
        },
        // Send the correct mode to the backend for fetching appropriate formats
        body: `url=${encodeURIComponent(url)}&mode=${fetchMode}`
    })
    .then(response => response.json())
    .then(data => {
        document.getElementById('loading').style.display = 'none';
        if (data.error) {
            showErrorPopup(translations[currentLanguage]['error'] + data.error);
            // Optionally show preview section again if needed, or reset state
             document.getElementById('preview').style.display = 'none';
            return;
        }

        document.getElementById('preview').style.display = 'block';
        document.getElementById('videoTitle').textContent = data.title;
        document.getElementById('thumbnail').src = data.thumbnail || '/static/placeholder.png'; // Use placeholder if no thumbnail
        document.getElementById('thumbnail').alt = data.title; // Set alt text

        // Format duration as MM:SS
        const durationInSeconds = data.duration;
        const minutes = Math.floor(durationInSeconds / 60);
        const seconds = Math.floor(durationInSeconds % 60).toString().padStart(2, '0');
        document.getElementById('duration').textContent = `${minutes}:${seconds}`;
        updateDurationText(); // Update the text with language

        document.getElementById('downloadUrl').value = url;
        // IMPORTANT: Set the correct download mode ('trim', 'auto', 'audio')
        document.getElementById('downloadMode').value = selectedMode;
        // Set audio_only based on the *final* intended download type
        document.getElementById('audioOnly').value = (fetchMode === 'audio').toString();


        const qualityContainer = document.getElementById('qualityOptions');
        qualityContainer.innerHTML = ''; // Clear previous options
        document.getElementById('selectedQuality').value = ''; // Clear selected quality
        document.getElementById('downloadButton').disabled = true; // Disable download until quality selected

        if (data.qualities && data.qualities.length > 0) {
            data.qualities.forEach(q => {
                const qualityDiv = document.createElement('div');
                qualityDiv.classList.add('quality-option');
                let icon = '';
                let qualityText = q[1]; // e.g., '1080', '720', 'صوت فقط'

                if (fetchMode === 'audio') {
                    icon = '<i class="fas fa-music"></i> ';
                    qualityText = translations[currentLanguage]['audioOnlyText']; // Use translated text
                    qualityDiv.dataset.quality = q[0]; // e.g., 'bestaudio/best'
                    qualityDiv.innerHTML = `${icon}<span data-i18n="audioOnlyText">${qualityText}</span>`;
                } else {
                    icon = '<i class="fas fa-video"></i> ';
                    qualityDiv.dataset.quality = q[0]; // e.g., '137', '22'
                    qualityDiv.innerHTML = `${icon}${qualityText}p`; // Append 'p' for pixel height
                }


                qualityDiv.addEventListener('click', function() {
                    document.querySelectorAll('.quality-option').forEach(opt => opt.classList.remove('selected'));
                    qualityDiv.classList.add('selected');
                    document.getElementById('selectedQuality').value = this.dataset.quality;
                    document.getElementById('downloadButton').disabled = false;
                    // Ensure audioOnly reflects the current selection type
                    document.getElementById('audioOnly').value = (fetchMode === 'audio').toString();
                });
                qualityContainer.appendChild(qualityDiv);
            });

             // Auto-select if only one option or if it's audio mode
            if (data.qualities.length === 1 || fetchMode === 'audio') {
                 const firstOption = qualityContainer.querySelector('.quality-option');
                 if (firstOption) {
                     firstOption.click(); // Simulate click to select and enable download
                 }
            }

        } else {
            // Handle case with no qualities found
             qualityContainer.innerHTML = `<p>${translations[currentLanguage]['error']} No qualities found.</p>`; // Adapt translation
        }

    })
    .catch(error => {
        document.getElementById('loading').style.display = 'none';
        document.getElementById('preview').style.display = 'none'; // Hide preview on error
        console.error('Error fetching preview:', error);
        showErrorPopup(translations[currentLanguage]['error'] + (error.message || 'Preview failed.'));
    });
}

// Function to format time input fields (MM:SS) automatically
function formatTimeInput(event) {
    const input = event.target;
    let value = input.value;
    const cursorPosition = input.selectionStart; // Remember cursor position

    // Remove non-digit characters
    let digits = value.replace(/\D/g, '');

    // Limit to 4 digits (MMSS)
    if (digits.length > 4) {
        digits = digits.slice(0, 4);
    }

    let formattedValue = digits;
    let newCursorPosition = cursorPosition;
    const hadColon = value.includes(':'); // Check if there was a colon before formatting

    // Insert colon if more than 2 digits
    if (digits.length > 2) {
        formattedValue = digits.slice(0, 2) + ':' + digits.slice(2);
        // Adjust cursor position if it was after the colon insertion point and a colon was actually inserted
        if (!hadColon && cursorPosition > 2) {
             newCursorPosition++;
        }
    }

    // Handle backspace potentially removing the colon or digits around it
    if (value.length > formattedValue.length) {
        // Calculate the difference in length
        const lengthDiff = value.length - formattedValue.length;
        // If backspace was pressed right after the colon (pos 3)
        if (hadColon && cursorPosition === 3 && value.charAt(2) === ':') {
            newCursorPosition = 2; // Move cursor before the (now removed) colon position
        } else {
             // General case for backspace/delete: adjust cursor backwards by length difference
              newCursorPosition = Math.max(0, cursorPosition - lengthDiff);
               // Special case: if deleting the colon itself from position 2
              if (hadColon && cursorPosition === 2 && value.charAt(2) === ':') {
                   newCursorPosition = 2; // Keep cursor at pos 2
              }
        }

    } else if (formattedValue.length > value.length && formattedValue.includes(':') && !hadColon) {
         // If colon was added, and cursor was after insertion point
         if (cursorPosition > 2) {
             newCursorPosition = cursorPosition + 1;
         } else {
             newCursorPosition = cursorPosition; // Keep position if cursor was before colon
         }

    } else {
         // Normal typing or pasting, ensure cursor tracks correctly
          newCursorPosition = cursorPosition + (formattedValue.length - value.length);
    }


    input.value = formattedValue;

    // Restore cursor position (crucial for good UX)
     // Use requestAnimationFrame to ensure the update happens after the value is set
    requestAnimationFrame(() => {
         if (document.activeElement === input) {
            input.setSelectionRange(newCursorPosition, newCursorPosition);
         }
    });
}


function convertTimeToSeconds(timeStr) {
    if (!timeStr || timeStr.trim() === '') return ''; // Handle empty or whitespace string

    // Basic format check
    if (!/^\d{1,2}:\d{2}$/.test(timeStr)) {
         throw new Error(translations[currentLanguage]['invalid.time.format']);
    }

    const parts = timeStr.split(':');
    const minutes = parseInt(parts[0], 10);
    const seconds = parseInt(parts[1], 10);

    if (isNaN(minutes) || isNaN(seconds) || minutes < 0 || seconds < 0 || seconds >= 60) {
        throw new Error(translations[currentLanguage]['invalid.time.format']);
    }
    return (minutes * 60 + seconds).toString();
}

document.getElementById('downloadForm').addEventListener('submit', function(e) {
    e.preventDefault();

    const url = document.getElementById('downloadUrl').value;
    const quality = document.getElementById('selectedQuality').value;
    const audioOnly = document.getElementById('audioOnly').value; // This should be correctly set by fetchPreview/quality selection
    const mode = document.getElementById('downloadMode').value; // Should be 'trim', 'auto', or 'audio'

    let startTimeSeconds = '0'; // Default start time in seconds
    let endTimeSeconds = '';   // Default end time in seconds (meaning full duration)

    if (mode === 'trim') {
        const startTimeInput = document.getElementById('startTime').value;
        const endTimeInput = document.getElementById('endTime').value;

        try {
            // Convert start time (default to 0 if empty or invalid, though formatTimeInput helps)
             if (startTimeInput && startTimeInput.trim() !== '00:00' && startTimeInput.trim() !== '') {
                 startTimeSeconds = convertTimeToSeconds(startTimeInput);
             } else {
                 startTimeSeconds = '0'; // Explicitly set to 0 if default/empty
             }


            // Convert end time only if provided
            if (endTimeInput && endTimeInput.trim() !== '') {
                endTimeSeconds = convertTimeToSeconds(endTimeInput);

                // Validate end time > start time
                const startSec = parseInt(startTimeSeconds);
                const endSec = parseInt(endTimeSeconds);
                if (!isNaN(startSec) && !isNaN(endSec) && endSec <= startSec) {
                    showErrorPopup(translations[currentLanguage]['end.time.after.start']);
                    return;
                }
            }
        } catch (error) {
            // convertTimeToSeconds throws error with translated message
            showErrorPopup(error.message);
            return;
        }
    }

    document.getElementById('loadingMessage').style.display = 'block';
    document.getElementById('preview').style.display = 'none';

    fetch('/download', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/x-www-form-urlencoded'
        },
        // Send data to backend
        body: `url=${encodeURIComponent(url)}&quality=${quality}&audio_only=${audioOnly}&mode=${mode}&start_time=${startTimeSeconds}&end_time=${endTimeSeconds}`
    })
    .then(response => response.json())
    .then(data => {
        document.getElementById('loadingMessage').style.display = 'none';
        if (data.error) {
            showErrorPopup(translations[currentLanguage]['error'] + data.error);
            document.getElementById('preview').style.display = 'block'; // Show preview section again on error
            return;
        }

        // Trigger file download (assuming backend provides filename for a separate download route)
        if (data.success && data.filename) {
             // Construct the download URL dynamically
             const downloadUrl = `/downloads/${encodeURIComponent(data.filename)}?folder=${audioOnly === 'true' ? 'audio' : 'video'}`; // Pass folder info if needed by backend

             // Create a temporary link and click it
             const link = document.createElement('a');
             link.href = downloadUrl;
             link.download = data.filename; // Suggest filename to browser
             document.body.appendChild(link);
             link.click();
             document.body.removeChild(link);


            // Show success message
            let successMessageKey = (audioOnly === 'true') ? 'success.audio' : 'success.video';
            showSuccessPopup(translations[currentLanguage][successMessageKey]);

             // Reset form/UI elements if desired
             // document.getElementById('previewForm').reset();
             // document.getElementById('preview').style.display = 'none';
             // ... etc.

        } else {
             // Handle unexpected success response without filename
              showErrorPopup(translations[currentLanguage]['download.error']);
              document.getElementById('preview').style.display = 'block';
        }

    })
    .catch(error => {
        document.getElementById('loadingMessage').style.display = 'none';
        console.error('Download Error:', error);
        showErrorPopup(translations[currentLanguage]['download.error'] + (error.message || ''));
        document.getElementById('preview').style.display = 'block'; // Show preview section again
    });
});

function showSuccessPopup(message) {
    document.getElementById('successMessage').textContent = message; // Use textContent for safety
    document.getElementById('successPopup').classList.add('show');
    document.getElementById('overlay').classList.add('show');
}

function showErrorPopup(message) {
    document.getElementById('errorMessage').textContent = message; // Use textContent for safety
    document.getElementById('errorPopup').classList.add('show');
    document.getElementById('overlay').classList.add('show');
}

function closePopup() {
    document.getElementById('successPopup').classList.remove('show');
    document.getElementById('overlay').classList.remove('show');
}

function closeErrorPopup() {
    document.getElementById('errorPopup').classList.remove('show');
    document.getElementById('overlay').classList.remove('show');
}

function isValidUrl(url) {
     // Basic check for protocol and non-empty host
     if (!url || typeof url !== 'string') return false;
     try {
         const parsedUrl = new URL(url);
         // Allow common protocols and ensure hostname exists
         return ['http:', 'https:', 'ftp:', 'ftps:'].includes(parsedUrl.protocol) && parsedUrl.hostname;
     } catch (e) {
         return false; // Invalid URL format
     }
}


function updateDurationText() {
    const durationSpan = document.getElementById('duration');
    const durationContainer = durationSpan ? durationSpan.parentElement : null;

    if (durationContainer && durationSpan.textContent) {
         // Assuming durationSpan.textContent is like "MM:SS"
         const durationValue = durationSpan.textContent;
          // Reconstruct the HTML ensuring the span with id="duration" is preserved
         durationContainer.innerHTML = `<i class="fas fa-clock"></i> ${translations[currentLanguage]['duration']}: <span id="duration">${durationValue}</span> ${translations[currentLanguage]['minutes']}`;
    } else if (durationContainer) {
        // Handle case where duration might be cleared or not yet set
         durationContainer.innerHTML = `<i class="fas fa-clock"></i> ${translations[currentLanguage]['duration']}: <span id="duration">--:--</span> ${translations[currentLanguage]['minutes']}`;
    }
}


function updateAudioOnlyText() {
    document.querySelectorAll('.quality-option span[data-i18n="audioOnlyText"]').forEach(element => {
        element.textContent = translations[currentLanguage]['audioOnlyText'];
    });
}

// Initialize page
document.addEventListener('DOMContentLoaded', () => {
    // Set initial theme and language
    const prefersDark = window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches;
    isDarkMode = prefersDark; // Set initial state based on preference
    document.documentElement.setAttribute('data-theme', isDarkMode ? 'dark' : 'light');
    document.getElementById('themeToggle').innerHTML = isDarkMode ? '<i class="fas fa-moon"></i>' : '<i class="fas fa-sun"></i>';

    // Detect browser language or default to 'ar'
    const browserLang = navigator.language.split('-')[0]; // e.g., 'en-US' -> 'en'
    if (translations[browserLang]) {
        currentLanguage = browserLang;
    } else {
        currentLanguage = 'ar'; // Default
    }
    translatePage(currentLanguage); // Apply initial translation


    // --- Add input event listeners for time formatting ---
    const startTimeInput = document.getElementById('startTime');
    const endTimeInput = document.getElementById('endTime');

    if (startTimeInput) {
        startTimeInput.addEventListener('input', formatTimeInput);
        startTimeInput.setAttribute('maxlength', '5'); // Visual length limit
        startTimeInput.setAttribute('inputmode', 'numeric'); // Hint for mobile keyboards
        startTimeInput.setAttribute('pattern', '[0-9:]*'); // Basic pattern hint
    }
    if (endTimeInput) {
        endTimeInput.addEventListener('input', formatTimeInput);
        endTimeInput.setAttribute('maxlength', '5');
        endTimeInput.setAttribute('inputmode', 'numeric');
        endTimeInput.setAttribute('pattern', '[0-9:]*');
    }
    // --- End time formatting listeners ---

     // Add click listener to overlay to close popups
    const overlay = document.getElementById('overlay');
    if(overlay) {
        overlay.addEventListener('click', () => {
            closePopup();
            closeErrorPopup();
            // Optionally close legal notice if needed, though it has its own button
            // const legalModal = document.getElementById('legalNoticeModal');
            // if (legalModal && legalModal.classList.contains('show')) {
            //     closeLegalNotice();
            // }
        });
    }
});