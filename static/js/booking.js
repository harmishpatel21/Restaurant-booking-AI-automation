document.addEventListener('DOMContentLoaded', function() {
    // Initialize audio recorder
    const recorder = new AudioRecorder();
    let recordedAudio = null;
    
    // Get DOM elements
    const startRecordBtn = document.getElementById('start-record');
    const stopRecordBtn = document.getElementById('stop-record');
    const audioCanvas = document.getElementById('audio-visualizer');
    const audioPlayback = document.getElementById('audio-playback');
    const transcriptDisplay = document.getElementById('transcript');
    const responseDisplay = document.getElementById('ai-response');
    const bookingForm = document.getElementById('booking-form');
    const loadingIndicator = document.getElementById('loading-indicator');
    const errorMessage = document.getElementById('error-message');
    
    // Initialize recorder if elements exist
    if (startRecordBtn && stopRecordBtn && audioCanvas) {
        recorder.initializeAudio('audio-visualizer')
            .then(success => {
                if (success) {
                    startRecordBtn.disabled = false;
                    console.log('Audio recorder initialized successfully');
                } else {
                    showError('Failed to initialize audio. Please check your microphone permissions.');
                }
            })
            .catch(err => {
                showError('Error accessing microphone: ' + err.message);
                console.error('Error initializing recorder:', err);
            });
    }
    
    // Event listeners for recording
    if (startRecordBtn) {
        startRecordBtn.addEventListener('click', function() {
            hideError();
            const success = recorder.startRecording();
            if (success) {
                startRecordBtn.disabled = true;
                stopRecordBtn.disabled = false;
                if (transcriptDisplay) transcriptDisplay.textContent = '';
                if (responseDisplay) responseDisplay.textContent = '';
            } else {
                showError('Could not start recording. Please refresh the page and try again.');
            }
        });
    }
    
    if (stopRecordBtn) {
        stopRecordBtn.addEventListener('click', function() {
            stopRecordBtn.disabled = true;
            showLoading();
            
            recorder.stopRecording()
                .then(audioBlob => {
                    recordedAudio = audioBlob;
                    recorder.playAudio(audioBlob, 'audio-playback');
                    
                    // Process audio and get transcription
                    const formData = new FormData();
                    formData.append('audio', audioBlob, 'recording.wav');
                    
                    return fetch('/voice/process', {
                        method: 'POST',
                        body: formData
                    });
                })
                .then(response => {
                    if (!response.ok) {
                        throw new Error('Network response was not ok');
                    }
                    return response.json();
                })
                .then(data => {
                    hideLoading();
                    startRecordBtn.disabled = false;
                    
                    if (transcriptDisplay) {
                        transcriptDisplay.textContent = data.transcript || 'No transcript available';
                    }
                    
                    if (responseDisplay) {
                        responseDisplay.textContent = data.response || 'No response available';
                    }
                    
                    // Fill booking form if booking data is available
                    if (data.booking_data && bookingForm) {
                        fillBookingForm(data.booking_data);
                    }
                    
                    // Play AI response if available
                    if (data.audio_response_url) {
                        const audioElement = document.getElementById('ai-audio-response');
                        if (audioElement) {
                            audioElement.src = data.audio_response_url;
                            audioElement.play();
                        }
                    }
                })
                .catch(error => {
                    hideLoading();
                    startRecordBtn.disabled = false;
                    showError('Error processing audio: ' + error.message);
                    console.error('Error processing recording:', error);
                });
        });
    }
    
    // Booking form submission
    if (bookingForm) {
        bookingForm.addEventListener('submit', function(e) {
            e.preventDefault();
            showLoading();
            
            const formData = new FormData(bookingForm);
            
            fetch('/booking/create', {
                method: 'POST',
                body: formData
            })
            .then(response => {
                if (!response.ok) {
                    throw new Error('Network response was not ok');
                }
                return response.json();
            })
            .then(data => {
                hideLoading();
                if (data.success) {
                    // Show success message
                    const successMessage = document.getElementById('success-message');
                    if (successMessage) {
                        successMessage.textContent = 'Booking created successfully!';
                        successMessage.classList.remove('d-none');
                        setTimeout(() => {
                            successMessage.classList.add('d-none');
                        }, 5000);
                    }
                    
                    // Clear form
                    bookingForm.reset();
                } else {
                    showError(data.message || 'Failed to create booking');
                }
            })
            .catch(error => {
                hideLoading();
                showError('Error creating booking: ' + error.message);
                console.error('Error submitting form:', error);
            });
        });
    }
    
    // Helper functions
    function fillBookingForm(data) {
        for (const [key, value] of Object.entries(data)) {
            const input = bookingForm.querySelector(`[name="${key}"]`);
            if (input) {
                input.value = value;
            }
        }
    }
    
    function showLoading() {
        if (loadingIndicator) {
            loadingIndicator.classList.remove('d-none');
        }
    }
    
    function hideLoading() {
        if (loadingIndicator) {
            loadingIndicator.classList.add('d-none');
        }
    }
    
    function showError(message) {
        if (errorMessage) {
            errorMessage.textContent = message;
            errorMessage.classList.remove('d-none');
        }
    }
    
    function hideError() {
        if (errorMessage) {
            errorMessage.classList.add('d-none');
        }
    }
    
    // Cleanup when leaving the page
    window.addEventListener('beforeunload', function() {
        if (recorder) {
            recorder.cleanup();
        }
    });
});
