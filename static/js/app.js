document.addEventListener('DOMContentLoaded', () => {
    // --- Elements ---
    // Mode Selection Elements
    const btnModeRecord = document.getElementById('btn-mode-record');
    const btnModeUpload = document.getElementById('btn-mode-upload');
    const sectionRecord = document.getElementById('section-record');
    const sectionUpload = document.getElementById('section-upload');

    // Notification Element
    const notification = document.getElementById('notification');

    // Recording Elements
    const btnRecord = document.getElementById('btn-record');
    const pulseRing = document.getElementById('pulse-ring');
    const recordStatus = document.getElementById('record-status');
    const recordTimer = document.getElementById('record-timer');
    const playbackArea = document.getElementById('playback-area');
    const audioPlayback = document.getElementById('audio-playback');
    const btnSubmitRecording = document.getElementById('btn-submit-recording');
    const btnDiscardRecording = document.getElementById('btn-discard-recording');

    // Uploading Elements
    const uploadDropzone = document.getElementById('upload-dropzone');
    const fileInput = document.getElementById('file-input');
    const btnBrowseFiles = document.getElementById('btn-browse-files');
    const selectedFileInfo = document.getElementById('selected-file-info');
    const fileNameDisplay = document.getElementById('file-name');
    const btnSubmitUpload = document.getElementById('btn-submit-upload');

    // --- State Variables ---
    let mediaRecorder = null;
    let audioChunks = [];
    let isRecording = false;
    let timerInterval = null;
    let recordingStartTime = 0;
    let currentAudioBlob = null;
    let selectedFile = null;

    // --- Tab Switching Logic ---
    function switchMode(mode) {
        if (mode === 'record') {
            btnModeRecord.classList.add('active');
            btnModeUpload.classList.remove('active');
            sectionRecord.classList.add('active');
            sectionRecord.classList.remove('hidden');
            sectionUpload.classList.remove('active');
            sectionUpload.classList.add('hidden');
        } else {
            btnModeUpload.classList.add('active');
            btnModeRecord.classList.remove('active');
            sectionUpload.classList.add('active');
            sectionUpload.classList.remove('hidden');
            sectionRecord.classList.remove('active');
            sectionRecord.classList.add('hidden');
        }
    }

    btnModeRecord.addEventListener('click', () => switchMode('record'));
    btnModeUpload.addEventListener('click', () => switchMode('upload'));


    // --- Notification Function ---
    function showNotification(message, type = 'success') {
        notification.textContent = message;
        if (type === 'error') {
            notification.classList.add('error');
        } else {
            notification.classList.remove('error');
        }
        notification.classList.add('show');
        
        setTimeout(() => {
            notification.classList.remove('show');
        }, 3000);
    }


    // --- Recording Logic ---
    function formatTime(seconds) {
        const mins = Math.floor(seconds / 60).toString().padStart(2, '0');
        const secs = (seconds % 60).toString().padStart(2, '0');
        return `${mins}:${secs}`;
    }

    function updateTimer() {
        const elapsed = Math.floor((Date.now() - recordingStartTime) / 1000);
        recordTimer.textContent = formatTime(elapsed);
    }

    async function toggleRecording() {
        if (!isRecording) {
            // Start Recording
            try {
                const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
                mediaRecorder = new MediaRecorder(stream);
                audioChunks = [];

                mediaRecorder.ondataavailable = (event) => {
                    if (event.data.size > 0) {
                        audioChunks.push(event.data);
                    }
                };

                mediaRecorder.onstop = () => {
                    currentAudioBlob = new Blob(audioChunks, { type: 'audio/webm' });
                    const audioUrl = URL.createObjectURL(currentAudioBlob);
                    audioPlayback.src = audioUrl;
                    playbackArea.classList.remove('hidden');
                    
                    // Cleanup visualizer
                    clearInterval(timerInterval);
                    pulseRing.classList.remove('recording');
                    btnRecord.classList.remove('recording');
                    recordStatus.textContent = 'Recording Stopped';
                };

                mediaRecorder.start();
                isRecording = true;
                
                // Update UI state
                recordingStartTime = Date.now();
                recordTimer.textContent = '00:00';
                timerInterval = setInterval(updateTimer, 1000);
                
                pulseRing.classList.add('recording');
                btnRecord.classList.add('recording');
                recordStatus.textContent = 'Recording in Progress...';
                playbackArea.classList.add('hidden');

            } catch (err) {
                console.error("Error accessing microphone: ", err);
                showNotification("Microphone access denied or not available.", 'error');
            }
        } else {
            // Stop Recording
            mediaRecorder.stop();
            isRecording = false;
            // stream tracks need to be stopped so microphone icon disappears
            mediaRecorder.stream.getTracks().forEach(track => track.stop());
        }
    }

    btnRecord.addEventListener('click', toggleRecording);

    btnDiscardRecording.addEventListener('click', () => {
        currentAudioBlob = null;
        audioPlayback.src = '';
        playbackArea.classList.add('hidden');
        recordTimer.textContent = '00:00';
        recordStatus.textContent = 'Click to Start Recording';
    });


    // --- File Upload Logic via Drag/Drop ---
    function handleFile(file) {
        if (file && file.type.startsWith('audio/')) {
            selectedFile = file;
            fileNameDisplay.textContent = file.name;
            selectedFileInfo.classList.remove('hidden');
        } else {
            showNotification('Please select a valid audio file.', 'error');
        }
    }

    uploadDropzone.addEventListener('dragover', (e) => {
        e.preventDefault();
        uploadDropzone.classList.add('dragover');
    });

    uploadDropzone.addEventListener('dragleave', () => {
        uploadDropzone.classList.remove('dragover');
    });

    uploadDropzone.addEventListener('drop', (e) => {
        e.preventDefault();
        uploadDropzone.classList.remove('dragover');
        
        if (e.dataTransfer.files.length) {
            handleFile(e.dataTransfer.files[0]);
        }
    });

    btnBrowseFiles.addEventListener('click', () => {
        fileInput.click();
    });

    fileInput.addEventListener('change', () => {
        if (fileInput.files.length) {
            handleFile(fileInput.files[0]);
        }
    });


    // --- API Submission Logic ---
    async function uploadToServer(fileOrBlob, filename = 'recording.webm') {
        const formData = new FormData();
        formData.append('file', fileOrBlob, filename);

        try {
            showNotification("Pipeline started! This might take a few minutes...", "success");
            
            const response = await fetch('/upload-audio', {
                method: 'POST',
                body: formData
            });

            if (!response.ok) {
                const result = await response.json().catch(() => ({}));
                throw new Error(result.message || 'Upload failed due to server error');
            }

            const contentType = response.headers.get('content-type');
            if (contentType && contentType.includes('application/pdf')) {
                const blob = await response.blob();
                const downloadUrl = window.URL.createObjectURL(blob);
                const link = document.createElement('a');
                link.href = downloadUrl;
                link.download = 'meeting_summary.pdf';
                document.body.appendChild(link);
                link.click();
                document.body.removeChild(link);
                window.URL.revokeObjectURL(downloadUrl);
                
                showNotification('Summary generated! Downloading PDF...', 'success');
                return true;
            } else {
                const result = await response.json();
                if (result.status === 'success') {
                    showNotification('Audio uploaded successfully!');
                    return true;
                }
                throw new Error(result.message || 'Unexpected response format');
            }
        } catch (error) {
            console.error('Error uploading:', error);
            showNotification(`Action failed: ${error.message}`, 'error');
            return false;
        }
    }

    btnSubmitRecording.addEventListener('click', async () => {
        if (!currentAudioBlob) return;
        
        btnSubmitRecording.textContent = 'Generating... (Please wait)';
        btnSubmitRecording.disabled = true;
        
        const success = await uploadToServer(currentAudioBlob, 'recorded_audio.webm');
        
        btnSubmitRecording.textContent = 'Upload Recording';
        btnSubmitRecording.disabled = false;

        if (success) {
            // Reset state
            btnDiscardRecording.click();
        }
    });

    btnSubmitUpload.addEventListener('click', async () => {
        if (!selectedFile) return;

        btnSubmitUpload.textContent = 'Generating... (Please wait)';
        btnSubmitUpload.disabled = true;
        
        const success = await uploadToServer(selectedFile, selectedFile.name);
        
        btnSubmitUpload.textContent = 'Upload File';
        btnSubmitUpload.disabled = false;

        if (success) {
            // Reset state
            selectedFile = null;
            selectedFileInfo.classList.add('hidden');
            fileInput.value = '';
        }
    });
});
