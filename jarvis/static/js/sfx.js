/**
 * ULTRON — Sound Effects
 * 
 * Procedurally generated sci-fi sound effects using Web Audio API.
 * No external audio files needed — all synthesized in real-time.
 */

let audioCtx = null;

function getCtx() {
  if (!audioCtx) {
    audioCtx = new (window.AudioContext || window.webkitAudioContext)();
  }
  return audioCtx;
}

// ── Tone generator ──────────────────────────────────────
function playTone(freq, duration, type = 'sine', volume = 0.1, fadeOut = true) {
  const ctx = getCtx();
  const osc = ctx.createOscillator();
  const gain = ctx.createGain();
  
  osc.type = type;
  osc.frequency.setValueAtTime(freq, ctx.currentTime);
  gain.gain.setValueAtTime(volume, ctx.currentTime);
  
  if (fadeOut) {
    gain.gain.exponentialRampToValueAtTime(0.001, ctx.currentTime + duration);
  }
  
  osc.connect(gain);
  gain.connect(ctx.destination);
  osc.start(ctx.currentTime);
  osc.stop(ctx.currentTime + duration);
}

// ── JARVIS-style sound effects ──────────────────────────

export function sfxActivate() {
  // Two rising tones — "wake up" sound
  playTone(400, 0.15, 'sine', 0.06);
  setTimeout(() => playTone(600, 0.2, 'sine', 0.08), 100);
}

export function sfxDeactivate() {
  // Descending tone
  playTone(500, 0.15, 'sine', 0.05);
  setTimeout(() => playTone(350, 0.2, 'sine', 0.04), 80);
}

export function sfxThinking() {
  // Soft pulsing tone
  playTone(300, 0.3, 'sine', 0.04);
  setTimeout(() => playTone(320, 0.25, 'sine', 0.03), 200);
}

export function sfxResponse() {
  // Rising chime — response incoming
  playTone(500, 0.1, 'sine', 0.05);
  setTimeout(() => playTone(700, 0.15, 'sine', 0.06), 80);
  setTimeout(() => playTone(900, 0.2, 'sine', 0.04), 160);
}

export function sfxToolCall() {
  // Quick blip
  playTone(800, 0.08, 'square', 0.03);
  setTimeout(() => playTone(1000, 0.06, 'square', 0.02), 50);
}

export function sfxError() {
  // Low warning buzz
  playTone(200, 0.3, 'sawtooth', 0.04);
  setTimeout(() => playTone(180, 0.3, 'sawtooth', 0.03), 200);
}

export function sfxConnect() {
  // Three rising tones — connection established
  playTone(400, 0.12, 'sine', 0.04);
  setTimeout(() => playTone(550, 0.12, 'sine', 0.05), 100);
  setTimeout(() => playTone(700, 0.2, 'sine', 0.06), 200);
}
