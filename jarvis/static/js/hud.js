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

    // System status — bottom right (styled HUD panel)
    this.elements.system = this._createEl('hud-system', {
      position: 'absolute', bottom: '75px', right: '20px',
      fontFamily: "'Share Tech Mono', 'Courier New', monospace",
      fontSize: '11px', color: 'rgba(0, 170, 255, 0.5)',
      letterSpacing: '1px', textAlign: 'right', lineHeight: '1.9',
      padding: '10px 15px',
      background: 'rgba(0, 30, 60, 0.3)',
      border: '1px solid rgba(0, 100, 200, 0.12)',
      borderRadius: '3px',
      backdropFilter: 'blur(3px)',
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

    // Notification — top center (holographic panel style)
    this.elements.notification = this._createEl('hud-notification', {
      position: 'absolute', top: '70px', left: '50%',
      transform: 'translateX(-50%)',
      fontFamily: "'Rajdhani', sans-serif",
      fontSize: '15px', color: 'rgba(255, 200, 50, 0.9)',
      letterSpacing: '2px', textAlign: 'center',
      padding: '10px 30px',
      background: 'rgba(255, 170, 0, 0.08)',
      border: '1px solid rgba(255, 170, 0, 0.2)',
      borderRadius: '3px',
      opacity: '0', transition: 'opacity 0.5s, transform 0.5s',
      textShadow: '0 0 10px rgba(255, 150, 0, 0.3)',
      backdropFilter: 'blur(5px)',
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

    // Activity feed — bottom left (styled HUD panel)
    this.elements.activity = this._createEl('hud-activity', {
      position: 'absolute', bottom: '75px', left: '20px',
      fontFamily: "'Share Tech Mono', monospace",
      fontSize: '10px', color: 'rgba(0, 170, 255, 0.4)',
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
    if (stats.cpu !== undefined) {
      const cpuColor = stats.cpu > 80 ? '#f44' : stats.cpu > 50 ? '#fa0' : '#0af';
      lines.push(`<span style="color:${cpuColor}">CPU ${stats.cpu}%</span>`);
    }
    if (stats.ram !== undefined) {
      const ramColor = stats.ram > 85 ? '#f44' : stats.ram > 60 ? '#fa0' : '#0af';
      lines.push(`<span style="color:${ramColor}">RAM ${stats.ram}%</span>`);
      if (stats.ram_used_gb) lines.push(`<span style="opacity:0.5">${stats.ram_used_gb}/${stats.ram_total_gb}GB</span>`);
    }
    if (stats.disk !== undefined) {
      lines.push(`DISK ${stats.disk}%`);
    }
    if (stats.battery) {
      const batIcon = stats.battery.charging ? '⚡' : '🔋';
      lines.push(`${batIcon} ${stats.battery.percent}%`);
    }
    if (stats.uptime) lines.push(`UP ${stats.uptime}`);
    if (stats.memories !== undefined) lines.push(`MEM ${stats.memories}`);
    if (stats.conversations !== undefined) lines.push(`CONV ${stats.conversations}`);
    this.elements.system.innerHTML = lines.join('<br>');

    // Store CPU for reactor pulsing
    this._lastCpu = stats.cpu || 0;
  }

  getCpuLevel() {
    return (this._lastCpu || 0) / 100;
  }

  setUptime(text) {
    this.elements.uptime.textContent = text;
  }

  addActivity(text) {
    const el = this.elements.activity;
    const time = new Date().toLocaleTimeString('en-US', { hour12: false });
    const line = document.createElement('div');
    line.innerHTML = `<span style="opacity:0.5">${time}</span> ${text}`;
    line.style.animation = 'fadeSlideIn 0.3s ease forwards';
    el.appendChild(line);
    
    // Keep max 8 lines
    while (el.children.length > 8) el.removeChild(el.firstChild);
  }

  /**
   * Show a floating holographic panel near the reactor.
   * Used for tool execution results, notifications, etc.
   */
  showPanel(text, duration = 4000, type = 'info') {
    const colors = {
      info: { border: 'rgba(0,150,255,0.3)', bg: 'rgba(0,30,60,0.4)', text: 'rgba(180,220,255,0.9)' },
      success: { border: 'rgba(0,200,100,0.3)', bg: 'rgba(0,40,20,0.4)', text: 'rgba(150,255,200,0.9)' },
      warning: { border: 'rgba(255,170,0,0.3)', bg: 'rgba(40,30,0,0.4)', text: 'rgba(255,220,150,0.9)' },
      error: { border: 'rgba(255,50,50,0.3)', bg: 'rgba(40,0,0,0.4)', text: 'rgba(255,180,180,0.9)' },
    };
    const c = colors[type] || colors.info;

    // Position randomly around the reactor
    const angle = Math.random() * Math.PI * 2;
    const dist = 180 + Math.random() * 80;
    const cx = window.innerWidth / 2 + Math.cos(angle) * dist;
    const cy = window.innerHeight * 0.42 + Math.sin(angle) * dist * 0.5;

    const panel = document.createElement('div');
    panel.style.cssText = `
      position: absolute;
      left: ${cx}px; top: ${cy}px;
      transform: translate(-50%, -50%) scale(0.8);
      font-family: 'Share Tech Mono', monospace;
      font-size: 10px;
      color: ${c.text};
      padding: 8px 14px;
      background: ${c.bg};
      border: 1px solid ${c.border};
      border-radius: 3px;
      backdrop-filter: blur(5px);
      opacity: 0;
      transition: opacity 0.4s, transform 0.4s;
      pointer-events: none;
      user-select: none;
      z-index: 150;
      max-width: 250px;
      white-space: nowrap;
      overflow: hidden;
      text-overflow: ellipsis;
    `;
    panel.textContent = text;
    this.container.appendChild(panel);

    // Animate in
    requestAnimationFrame(() => {
      panel.style.opacity = '1';
      panel.style.transform = 'translate(-50%, -50%) scale(1)';
    });

    // Animate out and remove
    setTimeout(() => {
      panel.style.opacity = '0';
      panel.style.transform = 'translate(-50%, -50%) scale(0.9)';
      setTimeout(() => panel.remove(), 500);
    }, duration);
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
