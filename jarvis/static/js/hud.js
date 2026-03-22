/**
 * ULTRON — HUD Overlay Elements
 * 
 * CSS-positioned overlay elements on top of the Three.js canvas.
 * Minimal, atmospheric, always-visible system information.
 * 
 * Elements:
 * - Time/date (top-right)
 * - System stats (bottom-right)
 * - State indicator (bottom-center)
 * - Transcription display (center)
 * - Response display (center-below)
 * - Notification area (top-center)
 */

export class HUD {
  constructor(container) {
    this.container = container;
    this.elements = {};
    this._build();
    this._startClock();
    this.state = 'idle';
  }

  _build() {
    // Time/date — top right
    this.elements.time = this._createEl('hud-time', {
      position: 'absolute', top: '20px', right: '30px',
      fontFamily: "'Share Tech Mono', 'Courier New', monospace",
      fontSize: '14px', color: 'rgba(0, 170, 255, 0.6)',
      letterSpacing: '2px', textAlign: 'right',
    });

    // System status — bottom right
    this.elements.system = this._createEl('hud-system', {
      position: 'absolute', bottom: '80px', right: '30px',
      fontFamily: "'Share Tech Mono', 'Courier New', monospace",
      fontSize: '11px', color: 'rgba(0, 170, 255, 0.4)',
      letterSpacing: '1px', textAlign: 'right', lineHeight: '1.8',
    });

    // State indicator — bottom center
    this.elements.state = this._createEl('hud-state', {
      position: 'absolute', bottom: '80px', left: '50%',
      transform: 'translateX(-50%)',
      fontFamily: "'Rajdhani', 'Share Tech Mono', sans-serif",
      fontSize: '12px', color: 'rgba(0, 170, 255, 0.5)',
      letterSpacing: '6px', textTransform: 'uppercase',
      transition: 'color 0.5s, opacity 0.5s',
    });

    // Transcription — above reactor (user's voice input)
    this.elements.transcript = this._createEl('hud-transcript', {
      position: 'absolute', top: '25%', left: '50%',
      transform: 'translate(-50%, -50%)',
      fontFamily: "'Rajdhani', sans-serif",
      fontSize: '22px', color: 'rgba(100, 220, 255, 0.9)',
      letterSpacing: '1px', textAlign: 'center',
      maxWidth: '700px', opacity: '0',
      transition: 'opacity 0.3s',
      textShadow: '0 0 20px rgba(0,150,255,0.4)',
    });

    // Response — below reactor, large and clear
    this.elements.response = this._createEl('hud-response', {
      position: 'absolute', top: '68%', left: '50%',
      transform: 'translate(-50%, 0)',
      fontFamily: "'Rajdhani', sans-serif",
      fontSize: '20px', fontWeight: '400',
      color: 'rgba(220, 240, 255, 0.9)',
      letterSpacing: '0.5px', textAlign: 'center',
      maxWidth: '750px', lineHeight: '1.6',
      opacity: '0', transition: 'opacity 0.5s',
      textShadow: '0 0 15px rgba(0,100,200,0.3)',
    });

    // Notification — top center
    this.elements.notification = this._createEl('hud-notification', {
      position: 'absolute', top: '60px', left: '50%',
      transform: 'translateX(-50%)',
      fontFamily: "'Rajdhani', sans-serif",
      fontSize: '14px', color: 'rgba(255, 170, 0, 0.8)',
      letterSpacing: '2px', textAlign: 'center',
      opacity: '0', transition: 'opacity 0.5s',
    });

    // Title — top left
    this.elements.title = this._createEl('hud-title', {
      position: 'absolute', top: '18px', left: '30px',
      fontFamily: "'Rajdhani', sans-serif",
      fontSize: '22px', fontWeight: '600',
      color: 'rgba(0, 170, 255, 0.7)',
      letterSpacing: '10px',
    });
    this.elements.title.textContent = 'ULTRON';

    // Uptime — below title
    this.elements.uptime = this._createEl('hud-uptime', {
      position: 'absolute', top: '46px', left: '30px',
      fontFamily: "'Share Tech Mono', monospace",
      fontSize: '10px', color: 'rgba(0, 170, 255, 0.35)',
      letterSpacing: '2px',
    });

    // Activity feed — bottom left
    this.elements.activity = this._createEl('hud-activity', {
      position: 'absolute', bottom: '80px', left: '30px',
      fontFamily: "'Share Tech Mono', monospace",
      fontSize: '10px', color: 'rgba(0, 170, 255, 0.3)',
      lineHeight: '1.8', maxWidth: '300px',
      maxHeight: '120px', overflow: 'hidden',
    });
  }

  _createEl(id, styles) {
    const el = document.createElement('div');
    el.id = id;
    Object.assign(el.style, styles);
    el.style.pointerEvents = 'none';
    el.style.userSelect = 'none';
    el.style.zIndex = '100';
    this.container.appendChild(el);
    return el;
  }

  _startClock() {
    const update = () => {
      const now = new Date();
      const time = now.toLocaleTimeString('en-US', { hour12: false });
      const date = now.toLocaleDateString('en-US', { 
        weekday: 'short', month: 'short', day: 'numeric' 
      });
      this.elements.time.innerHTML = `${time}<br><span style="font-size:10px;opacity:0.6">${date}</span>`;
    };
    update();
    setInterval(update, 1000);
  }

  // ── Public API ────────────────────────────────────────

  setState(state) {
    this.state = state;
    const stateEl = this.elements.state;
    
    const stateLabels = {
      idle: 'STANDING BY',
      listening: 'LISTENING',
      thinking: 'PROCESSING',
      speaking: 'RESPONDING',
    };
    const stateColors = {
      idle: 'rgba(0, 170, 255, 0.3)',
      listening: 'rgba(0, 255, 136, 0.7)',
      thinking: 'rgba(255, 170, 0, 0.7)',
      speaking: 'rgba(0, 200, 255, 0.7)',
    };
    
    stateEl.textContent = stateLabels[state] || state.toUpperCase();
    stateEl.style.color = stateColors[state] || stateColors.idle;
  }

  setTranscript(text) {
    this.elements.transcript.textContent = text;
    this.elements.transcript.style.opacity = text ? '1' : '0';
  }

  setResponse(text) {
    clearTimeout(this._responseFadeTimer);
    clearInterval(this._typewriterInterval);
    
    if (!text) {
      this.elements.response.textContent = '';
      this.elements.response.style.opacity = '0';
      return;
    }

    // Typewriter effect — characters appear one by one
    this.elements.response.textContent = '';
    this.elements.response.style.opacity = '1';
    
    let i = 0;
    const speed = Math.max(15, Math.min(40, 1500 / text.length)); // Adaptive speed
    
    this._typewriterInterval = setInterval(() => {
      if (i < text.length) {
        this.elements.response.textContent += text[i];
        i++;
      } else {
        clearInterval(this._typewriterInterval);
        // Fade to dim after 20 seconds
        this._responseFadeTimer = setTimeout(() => {
          this.elements.response.style.transition = 'opacity 3s';
          this.elements.response.style.opacity = '0.25';
        }, 20000);
      }
    }, speed);
  }

  notify(text, duration = 5000) {
    this.elements.notification.textContent = text;
    this.elements.notification.style.opacity = '1';
    setTimeout(() => {
      this.elements.notification.style.opacity = '0';
    }, duration);
  }

  setSystemStats(stats) {
    const lines = [];
    if (stats.cpu !== undefined) lines.push(`CPU ${stats.cpu}%`);
    if (stats.ram !== undefined) lines.push(`RAM ${stats.ram}%`);
    if (stats.uptime) lines.push(`UP ${stats.uptime}`);
    if (stats.memories !== undefined) lines.push(`MEM ${stats.memories}`);
    this.elements.system.innerHTML = lines.join('<br>');
  }

  setUptime(text) {
    this.elements.uptime.textContent = text;
  }

  addActivity(text) {
    const el = this.elements.activity;
    const time = new Date().toLocaleTimeString('en-US', { hour12: false });
    const line = document.createElement('div');
    line.innerHTML = `<span style="opacity:0.5">${time}</span> ${text}`;
    el.appendChild(line);
    
    // Keep max 8 lines
    while (el.children.length > 8) el.removeChild(el.firstChild);
  }

  fadeAll(opacity) {
    for (const el of Object.values(this.elements)) {
      el.style.transition = 'opacity 1s';
      if (el !== this.elements.transcript && el !== this.elements.response) {
        const cur = parseFloat(getComputedStyle(el).opacity);
        // Don't override elements that are already hidden
        if (cur > 0.01) {
          el.style.opacity = String(Math.min(parseFloat(el.style.opacity || 1), opacity));
        }
      }
    }
  }
}
