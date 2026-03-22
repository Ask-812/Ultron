/**
 * ULTRON — Main Entry Point
 * 
 * Orchestrates all components into the unified JARVIS experience:
 * 
 *   Three.js Scene (Arc Reactor + Particles)
 *     + Waveform Visualizer
 *     + HUD Overlays
 *     + Voice I/O
 *     + WebSocket Backend
 *     + State Machine
 * 
 * Flow:
 *   IDLE → (wake word) → LISTENING → (silence) → THINKING → SPEAKING → IDLE
 */

import * as THREE from 'https://cdn.jsdelivr.net/npm/three@0.160.0/build/three.module.js';
import { ArcReactor } from './reactor.js';
import { ParticleSystem } from './particles.js';
import { Waveform } from './waveform.js';
import { HUD } from './hud.js';
import { VoiceIO } from './voice.js';
import { WS } from './ws.js';

// ── Scene Setup ─────────────────────────────────────────
const container = document.getElementById('scene-container');

const scene = new THREE.Scene();
scene.background = new THREE.Color(0x050810);
scene.fog = new THREE.FogExp2(0x050810, 0.06);

const camera = new THREE.PerspectiveCamera(
  50, window.innerWidth / window.innerHeight, 0.1, 100
);
camera.position.set(0, 0, 5);

const renderer = new THREE.WebGLRenderer({
  antialias: true,
  alpha: false,
  powerPreference: 'high-performance',
});
renderer.setSize(window.innerWidth, window.innerHeight);
renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
renderer.toneMapping = THREE.ACESFilmicToneMapping;
renderer.toneMappingExposure = 1.2;
container.appendChild(renderer.domElement);

// Ambient light
const ambientLight = new THREE.AmbientLight(0x112233, 0.3);
scene.add(ambientLight);

// ── Components ──────────────────────────────────────────
const reactor = new ArcReactor(scene);
const particles = new ParticleSystem(scene);
const waveform = new Waveform(scene);
const hud = new HUD(container);
const voice = new VoiceIO();

// ── State Machine ───────────────────────────────────────
let currentState = 'idle';

function setState(newState) {
  if (currentState === newState) return;
  const prevState = currentState;
  currentState = newState;
  
  reactor.setState(newState);
  particles.setState(newState);
  hud.setState(newState);
  
  switch (newState) {
    case 'idle':
      waveform.showInput(false);
      waveform.showOutput(false);
      hud.setTranscript('');
      break;
    case 'listening':
      waveform.showInput(true);
      waveform.showOutput(false);
      reactor.pulse(0.5);
      break;
    case 'thinking':
      waveform.showInput(false);
      waveform.showOutput(false);
      reactor.pulse(0.3);
      break;
    case 'speaking':
      waveform.showInput(false);
      waveform.showOutput(true);
      break;
  }
}

// ── WebSocket ───────────────────────────────────────────
const wsUrl = `ws://${location.hostname}:3001`;
const ws = new WS(wsUrl);

ws.onConnect = () => {
  hud.addActivity('<span style="color:#0f0">Connected</span>');
  ws.send('status');
};

ws.onDisconnect = () => {
  hud.addActivity('<span style="color:#f00">Disconnected</span>');
};

ws.onMessage = async (data) => {
  switch (data.type) {
    case 'status':
      hud.setSystemStats({
        uptime: data.uptime,
        memories: data.memories,
      });
      break;

    case 'thinking':
      setState('thinking');
      break;

    case 'assistant_message':
      hud.setResponse(data.text);
      // Wait for voice — edge-tts can take 5-8s to generate
      clearTimeout(window._voiceWaitTimer);
      window._voiceWaitTimer = setTimeout(() => {
        if (currentState === 'thinking') setState('idle');
      }, 12000);
      break;

    case 'voice':
      clearTimeout(window._voiceWaitTimer);
      setState('speaking');
      await voice.playAudio(data.audio);
      setState('idle');
      break;

    case 'done':
      // Server signals processing complete (no voice or voice failed)
      if (currentState !== 'speaking') {
        setState('idle');
      }
      break;

    case 'tool_call':
      hud.addActivity(`<span style="color:#fa0">⚡ ${data.name}</span>`);
      reactor.pulse(0.3);
      break;

    case 'tool_result':
      const ok = data.result && data.result.startsWith('[OK]');
      const color = ok ? '#0f0' : '#f00';
      hud.addActivity(`<span style="color:${color}">${data.result?.substring(0, 60) || ''}</span>`);
      break;

    case 'error':
      hud.addActivity(`<span style="color:#f00">ERR: ${data.text?.substring(0, 60)}</span>`);
      break;
      
    case 'user_message':
      // Already shown via transcript
      break;
  }
};

// ── Voice Callbacks ─────────────────────────────────────
voice.onStateChange = (state) => {
  setState(state);
};

voice.onTranscript = (text, isFinal) => {
  hud.setTranscript(text);
};

voice.onCommand = (command) => {
  setState('thinking');
  hud.setTranscript('');
  ws.send('message', { text: command });
};

// ── Input Handler (Text Input Fallback) ─────────────────
const inputBar = document.getElementById('input-bar');
const inputField = document.getElementById('input-field');

if (inputField) {
  inputField.addEventListener('keydown', (e) => {
    if (e.key === 'Enter') {
      const text = inputField.value.trim();
      if (text) {
        inputField.value = '';
        setState('thinking');
        hud.setTranscript(text);
        ws.send('message', { text });
        setTimeout(() => hud.setTranscript(''), 2000);
      }
    }
  });

  // Input bar is always visible (opacity managed by CSS hover)
}

// ── Mic button ──────────────────────────────────────────
const micBtn = document.getElementById('mic-btn');
let micActive = false;

if (micBtn) {
  micBtn.addEventListener('click', async () => {
    if (!micActive) {
      // First click: start continuous listening
      const started = voice.startListening();
      if (started) {
        micActive = true;
        micBtn.classList.add('active');
        // Setup mic waveform
        await waveform.setupMicInput();
        hud.addActivity('Mic enabled — say "Ultron" to activate');
      }
    } else {
      // Toggle manual activation (skip wake word)
      if (voice.isAwake) {
        voice.deactivate();
      } else {
        voice.activate();
      }
    }
  });
}

// ── Keyboard shortcut ───────────────────────────────────
document.addEventListener('keydown', (e) => {
  // Space to toggle listening (when input not focused)
  if (e.code === 'Space' && document.activeElement !== inputField) {
    e.preventDefault();
    if (voice.isAwake) {
      voice.deactivate();
    } else {
      voice.activate();
      if (!micActive && voice.startListening()) {
        micActive = true;
        waveform.setupMicInput();
      }
    }
  }
  
  // Escape to stop speaking
  if (e.code === 'Escape') {
    voice.stopSpeaking();
    setState('idle');
  }
});

// ── Resize Handler ──────────────────────────────────────
window.addEventListener('resize', () => {
  camera.aspect = window.innerWidth / window.innerHeight;
  camera.updateProjectionMatrix();
  renderer.setSize(window.innerWidth, window.innerHeight);
});

// ── Render Loop ─────────────────────────────────────────
const clock = new THREE.Clock();

function animate() {
  requestAnimationFrame(animate);
  
  const time = clock.getElapsedTime();
  const delta = Math.min(clock.getDelta(), 0.05); // Cap delta

  // Get audio levels
  const inputLevel = waveform.getInputLevel();
  const outputLevel = waveform.getOutputLevel();
  const audioLevel = Math.max(inputLevel, outputLevel);

  // Update components
  reactor.update(time, delta, audioLevel);
  particles.update(time, delta, audioLevel);
  waveform.update(time, delta);
  
  // Subtle camera breathing
  camera.position.x = Math.sin(time * 0.1) * 0.03;
  camera.position.y = Math.cos(time * 0.15) * 0.02;
  
  renderer.render(scene, camera);
}

animate();

// ── Initial State ───────────────────────────────────────
setState('idle');
hud.addActivity('System initialized');

// Request status every 10s
setInterval(() => {
  if (ws.connected) ws.send('status');
}, 10000);
