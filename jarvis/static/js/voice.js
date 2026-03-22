/**
 * ULTRON — Voice I/O Module
 * 
 * Handles:
 * - Continuous speech recognition (Web Speech API)
 * - Wake word detection ("Hey Ultron", "Ultron")
 * - Voice Activity Detection
 * - Audio playback of TTS responses
 * - State management for voice pipeline
 */

export class VoiceIO {
  constructor() {
    this.recognition = null;
    this.isListening = false;
    this.isAwake = false;  // Wake word detected
    this.isSpeaking = false;
    this.currentTranscript = '';
    this.finalTranscript = '';
    this.audioQueue = [];
    this.currentAudio = null;
    
    // Callbacks
    this.onStateChange = null;    // (state: string) => void
    this.onTranscript = null;     // (text: string, isFinal: boolean) => void
    this.onCommand = null;        // (text: string) => void
    this.onSpeakStart = null;     // () => void
    this.onSpeakEnd = null;       // () => void
    
    // Wake words
    this.wakeWords = ['ultron', 'hey ultron', 'jarvis', 'hey jarvis'];
    
    // Silence detection
    this._silenceTimer = null;
    this._silenceTimeout = 2000; // 2s silence = end of utterance
    
    this._initRecognition();
  }

  _initRecognition() {
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    if (!SpeechRecognition) {
      console.warn('[VOICE] Speech recognition not supported');
      return;
    }

    this.recognition = new SpeechRecognition();
    this.recognition.continuous = true;
    this.recognition.interimResults = true;
    this.recognition.lang = 'en-US';
    this.recognition.maxAlternatives = 1;

    this.recognition.onresult = (event) => {
      let interim = '';
      let final = '';

      for (let i = event.resultIndex; i < event.results.length; i++) {
        const transcript = event.results[i][0].transcript;
        if (event.results[i].isFinal) {
          final += transcript;
        } else {
          interim += transcript;
        }
      }

      this.currentTranscript = interim || final;
      
      if (this.onTranscript) {
        this.onTranscript(this.currentTranscript, !!final);
      }

      // Reset silence timer
      this._resetSilenceTimer();

      if (final) {
        this._handleFinalTranscript(final.trim());
      }
    };

    this.recognition.onerror = (event) => {
      if (event.error === 'no-speech' || event.error === 'aborted') return;
      console.warn('[VOICE] Recognition error:', event.error);
      // Auto-restart on error
      if (this.isListening) {
        setTimeout(() => this._restartRecognition(), 500);
      }
    };

    this.recognition.onend = () => {
      // Auto-restart for continuous listening
      if (this.isListening) {
        setTimeout(() => this._restartRecognition(), 200);
      }
    };
  }

  _restartRecognition() {
    if (!this.recognition || this.isSpeaking) return;
    try {
      this.recognition.start();
    } catch (e) {
      // Already started, ignore
    }
  }

  _resetSilenceTimer() {
    clearTimeout(this._silenceTimer);
    if (this.isAwake) {
      this._silenceTimer = setTimeout(() => {
        // User stopped talking — process the command
        if (this.finalTranscript) {
          this._processCommand(this.finalTranscript);
          this.finalTranscript = '';
        }
      }, this._silenceTimeout);
    }
  }

  _handleFinalTranscript(text) {
    const lower = text.toLowerCase().trim();
    
    if (!this.isAwake) {
      // Check for wake word
      for (const wake of this.wakeWords) {
        if (lower.includes(wake)) {
          this.isAwake = true;
          // Extract command after wake word
          const afterWake = lower.split(wake).pop().trim();
          if (afterWake.length > 2) {
            this._processCommand(afterWake);
          } else {
            // Just the wake word — wait for command
            if (this.onStateChange) this.onStateChange('listening');
          }
          return;
        }
      }
      // No wake word — ignore
      return;
    }

    // Already awake — accumulate transcript
    this.finalTranscript = (this.finalTranscript + ' ' + text).trim();
  }

  _processCommand(command) {
    if (!command || command.length < 2) return;
    
    this.isAwake = false;
    this.finalTranscript = '';
    this.currentTranscript = '';
    
    if (this.onCommand) {
      this.onCommand(command);
    }
  }

  // ── Public API ──────────────────────────────────────

  startListening() {
    if (!this.recognition) return false;
    this.isListening = true;
    try {
      this.recognition.start();
      return true;
    } catch (e) {
      return false;
    }
  }

  stopListening() {
    this.isListening = false;
    this.isAwake = false;
    if (this.recognition) {
      try { this.recognition.stop(); } catch (e) {}
    }
  }

  // Force-activate (skip wake word — for text input or button press)
  activate() {
    this.isAwake = true;
    if (this.onStateChange) this.onStateChange('listening');
  }

  // Deactivate listening state
  deactivate() {
    this.isAwake = false;
    if (this.onStateChange) this.onStateChange('idle');
  }

  // Play TTS audio (base64 encoded mp3)
  async playAudio(audioB64) {
    return new Promise((resolve) => {
      this.isSpeaking = true;
      if (this.onSpeakStart) this.onSpeakStart();
      if (this.onStateChange) this.onStateChange('speaking');
      
      // Pause recognition while speaking to avoid feedback
      if (this.recognition) {
        try { this.recognition.stop(); } catch (e) {}
      }

      const audio = new Audio('data:audio/mp3;base64,' + audioB64);
      this.currentAudio = audio;
      
      audio.onended = () => {
        this.isSpeaking = false;
        this.currentAudio = null;
        if (this.onSpeakEnd) this.onSpeakEnd();
        if (this.onStateChange) this.onStateChange('idle');
        // Resume recognition
        if (this.isListening) {
          setTimeout(() => this._restartRecognition(), 300);
        }
        resolve();
      };
      
      audio.onerror = () => {
        this.isSpeaking = false;
        this.currentAudio = null;
        if (this.onSpeakEnd) this.onSpeakEnd();
        if (this.onStateChange) this.onStateChange('idle');
        if (this.isListening) {
          setTimeout(() => this._restartRecognition(), 300);
        }
        resolve();
      };

      audio.play().catch((e) => {
        console.warn('[VOICE] Audio play failed (user interaction needed):', e);
        this.isSpeaking = false;
        if (this.onSpeakEnd) this.onSpeakEnd();
        if (this.onStateChange) this.onStateChange('idle');
        resolve();
      });
    });
  }

  stopSpeaking() {
    if (this.currentAudio) {
      this.currentAudio.pause();
      this.currentAudio = null;
    }
    this.isSpeaking = false;
    if (this.onSpeakEnd) this.onSpeakEnd();
  }
}
