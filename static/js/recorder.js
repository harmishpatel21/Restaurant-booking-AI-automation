// Audio recorder functionality for voice interactions
class AudioRecorder {
    constructor() {
        this.mediaRecorder = null;
        this.audioChunks = [];
        this.stream = null;
        this.isRecording = false;
        this.audioContext = null;
        this.analyser = null;
        this.canvas = null;
        this.canvasContext = null;
        this.animationFrameId = null;
    }

    async initializeAudio(canvasId) {
        try {
            this.stream = await navigator.mediaDevices.getUserMedia({ audio: true });
            this.mediaRecorder = new MediaRecorder(this.stream);
            
            this.mediaRecorder.ondataavailable = (event) => {
                if (event.data.size > 0) {
                    this.audioChunks.push(event.data);
                }
            };
            
            // Setup audio visualization if canvas is provided
            if (canvasId) {
                this.setupVisualization(canvasId);
            }
            
            return true;
        } catch (error) {
            console.error('Error initializing audio: ', error);
            return false;
        }
    }
    
    setupVisualization(canvasId) {
        this.canvas = document.getElementById(canvasId);
        if (!this.canvas) return;
        
        this.canvasContext = this.canvas.getContext('2d');
        this.audioContext = new (window.AudioContext || window.webkitAudioContext)();
        this.analyser = this.audioContext.createAnalyser();
        
        const source = this.audioContext.createMediaStreamSource(this.stream);
        source.connect(this.analyser);
        
        this.analyser.fftSize = 256;
        const bufferLength = this.analyser.frequencyBinCount;
        const dataArray = new Uint8Array(bufferLength);
        
        const drawVisualizer = () => {
            this.animationFrameId = requestAnimationFrame(drawVisualizer);
            
            this.analyser.getByteFrequencyData(dataArray);
            
            this.canvasContext.clearRect(0, 0, this.canvas.width, this.canvas.height);
            this.canvasContext.fillStyle = 'rgb(0, 0, 0)';
            this.canvasContext.fillRect(0, 0, this.canvas.width, this.canvas.height);
            
            const barWidth = (this.canvas.width / bufferLength) * 2.5;
            let barHeight;
            let x = 0;
            
            for (let i = 0; i < bufferLength; i++) {
                barHeight = dataArray[i] / 2;
                
                this.canvasContext.fillStyle = `rgb(50, ${barHeight + 100}, 150)`;
                this.canvasContext.fillRect(x, this.canvas.height - barHeight, barWidth, barHeight);
                
                x += barWidth + 1;
            }
        };
        
        drawVisualizer();
    }

    startRecording() {
        if (this.mediaRecorder && this.mediaRecorder.state !== 'recording') {
            this.audioChunks = [];
            this.mediaRecorder.start();
            this.isRecording = true;
            return true;
        }
        return false;
    }

    stopRecording() {
        return new Promise((resolve, reject) => {
            if (this.mediaRecorder && this.mediaRecorder.state === 'recording') {
                this.mediaRecorder.onstop = () => {
                    const audioBlob = new Blob(this.audioChunks, { type: 'audio/wav' });
                    this.isRecording = false;
                    if (this.animationFrameId) {
                        cancelAnimationFrame(this.animationFrameId);
                    }
                    resolve(audioBlob);
                };
                
                this.mediaRecorder.stop();
            } else {
                reject(new Error('Not recording'));
            }
        });
    }

    playAudio(audioBlob, audioElementId) {
        const audioElement = document.getElementById(audioElementId);
        if (!audioElement) {
            console.error('Audio element not found');
            return;
        }
        
        const audioUrl = URL.createObjectURL(audioBlob);
        audioElement.src = audioUrl;
        audioElement.play();
    }

    cleanup() {
        if (this.stream) {
            this.stream.getTracks().forEach(track => track.stop());
        }
        if (this.audioContext) {
            this.audioContext.close();
        }
        if (this.animationFrameId) {
            cancelAnimationFrame(this.animationFrameId);
        }
    }
}

// Export the AudioRecorder class
window.AudioRecorder = AudioRecorder;
