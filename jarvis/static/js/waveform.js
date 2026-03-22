/**
 * ULTRON — Audio Waveform Visualizer
 * 
 * Circular waveform that surrounds the Arc Reactor.
 * Responds in real-time to audio input (microphone) and output (speech).
 * 
 * Two rings:
 * - Inner ring (blue): User's voice input
 * - Outer ring (gold): Ultron's voice output
 */

import * as THREE from 'https://cdn.jsdelivr.net/npm/three@0.160.0/build/three.module.js';

const WAVE_SEGMENTS = 128;
const INPUT_RADIUS = 1.15;
const OUTPUT_RADIUS = 1.35;

export class Waveform {
  constructor(scene) {
    this.scene = scene;
    this.inputVisible = false;
    this.outputVisible = false;
    
    // Audio analysis
    this.inputData = new Float32Array(WAVE_SEGMENTS);
    this.outputData = new Float32Array(WAVE_SEGMENTS);
    this.smoothInputData = new Float32Array(WAVE_SEGMENTS);
    this.smoothOutputData = new Float32Array(WAVE_SEGMENTS);
    
    // Audio context for analysis
    this.audioContext = null;
    this.micAnalyser = null;
    this.outputAnalyser = null;
    
    this._buildWaveform('input', INPUT_RADIUS, 0x0088ff);
    this._buildWaveform('output', OUTPUT_RADIUS, 0xffaa00);
  }

  _buildWaveform(type, radius, color) {
    const points = [];
    for (let i = 0; i <= WAVE_SEGMENTS; i++) {
      const angle = (i / WAVE_SEGMENTS) * Math.PI * 2;
      points.push(new THREE.Vector3(
        Math.cos(angle) * radius,
        Math.sin(angle) * radius,
        0
      ));
    }

    const geometry = new THREE.BufferGeometry().setFromPoints(points);
    const material = new THREE.LineBasicMaterial({
      color,
      transparent: true,
      opacity: 0,
      linewidth: 2,
    });
    const line = new THREE.Line(geometry, material);
    
    if (type === 'input') {
      this.inputLine = line;
      this.inputGeometry = geometry;
    } else {
      this.outputLine = line;
      this.outputGeometry = geometry;
    }
    
    this.scene.add(line);
  }

  // ── Audio Setup ──────────────────────────────────────

  async setupMicInput() {
    try {
      this.audioContext = this.audioContext || new AudioContext();
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      const source = this.audioContext.createMediaStreamSource(stream);
      this.micAnalyser = this.audioContext.createAnalyser();
      this.micAnalyser.fftSize = WAVE_SEGMENTS * 2;
      this.micAnalyser.smoothingTimeConstant = 0.7;
      source.connect(this.micAnalyser);
      return true;
    } catch (e) {
      console.warn('[WAVEFORM] Mic access denied:', e);
      return false;
    }
  }

  connectOutputAudio(audioElement) {
    try {
      this.audioContext = this.audioContext || new AudioContext();
      const source = this.audioContext.createMediaElementSource(audioElement);
      this.outputAnalyser = this.audioContext.createAnalyser();
      this.outputAnalyser.fftSize = WAVE_SEGMENTS * 2;
      this.outputAnalyser.smoothingTimeConstant = 0.7;
      source.connect(this.outputAnalyser);
      source.connect(this.audioContext.destination);
    } catch (e) {
      console.warn('[WAVEFORM] Output audio setup failed:', e);
    }
  }

  // ── Visibility ───────────────────────────────────────

  showInput(visible) {
    this.inputVisible = visible;
  }

  showOutput(visible) {
    this.outputVisible = visible;
  }

  // ── Get Audio Level ──────────────────────────────────

  getInputLevel() {
    if (!this.micAnalyser) return 0;
    const data = new Uint8Array(this.micAnalyser.frequencyBinCount);
    this.micAnalyser.getByteFrequencyData(data);
    let sum = 0;
    for (let i = 0; i < data.length; i++) sum += data[i];
    return sum / (data.length * 255);
  }

  getOutputLevel() {
    if (!this.outputAnalyser) return 0;
    const data = new Uint8Array(this.outputAnalyser.frequencyBinCount);
    this.outputAnalyser.getByteFrequencyData(data);
    let sum = 0;
    for (let i = 0; i < data.length; i++) sum += data[i];
    return sum / (data.length * 255);
  }

  // ── Animation ────────────────────────────────────────

  update(time, deltaTime) {
    this._updateWave(
      this.inputLine, this.inputGeometry, this.inputVisible,
      this.micAnalyser, this.smoothInputData, INPUT_RADIUS, time, deltaTime
    );
    this._updateWave(
      this.outputLine, this.outputGeometry, this.outputVisible,
      this.outputAnalyser, this.smoothOutputData, OUTPUT_RADIUS, time, deltaTime
    );
  }

  _updateWave(line, geometry, visible, analyser, smoothData, radius, time, dt) {
    // Fade opacity
    const targetOpacity = visible ? 0.6 : 0;
    line.material.opacity += (targetOpacity - line.material.opacity) * dt * 4;

    if (line.material.opacity < 0.01) return;

    const positions = geometry.attributes.position.array;
    let freqData = null;
    
    if (analyser) {
      freqData = new Uint8Array(analyser.frequencyBinCount);
      analyser.getByteFrequencyData(freqData);
    }

    for (let i = 0; i <= WAVE_SEGMENTS; i++) {
      const idx = i % WAVE_SEGMENTS;
      const angle = (i / WAVE_SEGMENTS) * Math.PI * 2;
      
      // Get frequency amplitude  
      let amp = 0;
      if (freqData) {
        const freqIdx = Math.floor((idx / WAVE_SEGMENTS) * freqData.length);
        amp = freqData[freqIdx] / 255;
      }
      
      // Smooth the data
      smoothData[idx] += (amp - smoothData[idx]) * dt * 12;
      
      // Add subtle sine wave when no audio
      const idleWave = Math.sin(angle * 3 + time * 2) * 0.01 + 
                       Math.sin(angle * 7 + time * 1.3) * 0.005;
      
      const displacement = smoothData[idx] * 0.15 + idleWave;
      const r = radius + displacement;
      
      const i3 = i * 3;
      positions[i3] = Math.cos(angle) * r;
      positions[i3 + 1] = Math.sin(angle) * r;
      positions[i3 + 2] = 0;
    }

    geometry.attributes.position.needsUpdate = true;
  }
}
