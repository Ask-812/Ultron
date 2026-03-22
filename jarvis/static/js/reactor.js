/**
 * ULTRON — Arc Reactor 3D Component
 * 
 * The visual heart of the system. A multi-layered rotating reactor
 * with concentric rings, glowing core, and energy pulse effects.
 * 
 * Inspired by the MCU Arc Reactor — nested torus rings rotating
 * at different speeds, a bright core with volumetric glow, and
 * energy lines radiating outward.
 */

import * as THREE from 'https://cdn.jsdelivr.net/npm/three@0.160.0/build/three.module.js';

// ── Reactor Configuration ─────────────────────────────────
const COLORS = {
  core: 0x00bbff,
  coreHot: 0x44ddff,
  ring1: 0x0088cc,
  ring2: 0x0066aa,
  ring3: 0x004488,
  glow: 0x00aaff,
  energy: 0x00ccff,
  warning: 0xff8800,
  critical: 0xff2200,
};

export class ArcReactor {
  constructor(scene) {
    this.scene = scene;
    this.group = new THREE.Group();
    this.state = 'idle'; // idle | listening | thinking | speaking
    this.breathPhase = 0;
    this.pulseIntensity = 0;
    this.targetColor = new THREE.Color(COLORS.core);
    this.currentColor = new THREE.Color(COLORS.core);
    
    this._buildCore();
    this._buildRings();
    this._buildEnergyLines();
    this._buildGlow();
    
    scene.add(this.group);
  }

  _buildCore() {
    // Inner glowing sphere
    const coreGeo = new THREE.SphereGeometry(0.15, 32, 32);
    const coreMat = new THREE.MeshBasicMaterial({
      color: COLORS.coreHot,
      transparent: true,
      opacity: 0.9,
    });
    this.core = new THREE.Mesh(coreGeo, coreMat);
    this.group.add(this.core);

    // Core point light
    this.coreLight = new THREE.PointLight(COLORS.core, 2, 8);
    this.group.add(this.coreLight);

    // Inner detail ring (thin, close to core)
    const innerDetailGeo = new THREE.TorusGeometry(0.2, 0.008, 8, 64);
    const innerDetailMat = new THREE.MeshBasicMaterial({
      color: COLORS.coreHot,
      transparent: true,
      opacity: 0.7,
    });
    this.innerDetail = new THREE.Mesh(innerDetailGeo, innerDetailMat);
    this.group.add(this.innerDetail);
  }

  _buildRings() {
    this.rings = [];

    // Ring configurations: [radius, tubeRadius, segments, color, speed, tilt]
    const ringConfigs = [
      [0.4, 0.012, 80, COLORS.ring1, 0.3, 0.1],
      [0.55, 0.008, 100, COLORS.ring2, -0.2, -0.15],
      [0.7, 0.006, 120, COLORS.ring3, 0.15, 0.2],
      [0.85, 0.004, 140, COLORS.ring3, -0.1, -0.05],
    ];

    for (const [radius, tube, segs, color, speed, tilt] of ringConfigs) {
      const geo = new THREE.TorusGeometry(radius, tube, 8, segs);
      const mat = new THREE.MeshBasicMaterial({
        color,
        transparent: true,
        opacity: 0.5,
      });
      const ring = new THREE.Mesh(geo, mat);
      ring.rotation.x = Math.PI / 2 + tilt;
      ring.userData = { speed, baseOpacity: 0.5 };
      this.rings.push(ring);
      this.group.add(ring);
    }

    // Segmented outer ring (tick marks like a gauge)
    this._buildSegmentedRing(1.0, 60);
  }

  _buildSegmentedRing(radius, segments) {
    const segGroup = new THREE.Group();
    
    for (let i = 0; i < segments; i++) {
      const angle = (i / segments) * Math.PI * 2;
      const length = i % 5 === 0 ? 0.08 : 0.04;
      const width = i % 5 === 0 ? 0.006 : 0.003;
      
      const geo = new THREE.PlaneGeometry(width, length);
      const mat = new THREE.MeshBasicMaterial({
        color: COLORS.ring3,
        transparent: true,
        opacity: 0.3,
        side: THREE.DoubleSide,
      });
      const seg = new THREE.Mesh(geo, mat);
      seg.position.x = Math.cos(angle) * radius;
      seg.position.y = Math.sin(angle) * radius;
      seg.rotation.z = angle + Math.PI / 2;
      segGroup.add(seg);
    }
    
    this.segmentedRing = segGroup;
    this.group.add(segGroup);
  }

  _buildEnergyLines() {
    // Radial energy lines emanating from core
    this.energyLines = [];
    const lineCount = 12;
    
    for (let i = 0; i < lineCount; i++) {
      const angle = (i / lineCount) * Math.PI * 2;
      const points = [];
      points.push(new THREE.Vector3(0.18 * Math.cos(angle), 0.18 * Math.sin(angle), 0));
      points.push(new THREE.Vector3(0.35 * Math.cos(angle), 0.35 * Math.sin(angle), 0));
      
      const geo = new THREE.BufferGeometry().setFromPoints(points);
      const mat = new THREE.LineBasicMaterial({
        color: COLORS.energy,
        transparent: true,
        opacity: 0.3,
      });
      const line = new THREE.Line(geo, mat);
      line.userData = { baseAngle: angle, phase: Math.random() * Math.PI * 2 };
      this.energyLines.push(line);
      this.group.add(line);
    }
  }

  _buildGlow() {
    // Outer glow sprite
    const canvas = document.createElement('canvas');
    canvas.width = 256;
    canvas.height = 256;
    const ctx = canvas.getContext('2d');
    
    const gradient = ctx.createRadialGradient(128, 128, 0, 128, 128, 128);
    gradient.addColorStop(0, 'rgba(0, 170, 255, 0.4)');
    gradient.addColorStop(0.3, 'rgba(0, 130, 255, 0.15)');
    gradient.addColorStop(0.7, 'rgba(0, 100, 255, 0.05)');
    gradient.addColorStop(1, 'rgba(0, 0, 0, 0)');
    
    ctx.fillStyle = gradient;
    ctx.fillRect(0, 0, 256, 256);
    
    const texture = new THREE.CanvasTexture(canvas);
    const spriteMat = new THREE.SpriteMaterial({
      map: texture,
      transparent: true,
      blending: THREE.AdditiveBlending,
    });
    this.glowSprite = new THREE.Sprite(spriteMat);
    this.glowSprite.scale.set(3.5, 3.5, 1);
    this.group.add(this.glowSprite);
  }

  // ── State Management ──────────────────────────────────
  setState(state) {
    this.state = state;
    switch (state) {
      case 'idle':
        this.targetColor.set(COLORS.core);
        break;
      case 'listening':
        this.targetColor.set(0x00ff88); // Green tint
        break;
      case 'thinking':
        this.targetColor.set(0xffaa00); // Gold
        break;
      case 'speaking':
        this.targetColor.set(COLORS.coreHot);
        break;
      case 'warning':
        this.targetColor.set(COLORS.warning);
        break;
      case 'critical':
        this.targetColor.set(COLORS.critical);
        break;
    }
  }

  pulse(intensity = 1.0) {
    this.pulseIntensity = intensity;
  }

  // ── Animation ─────────────────────────────────────────
  update(time, deltaTime, audioLevel = 0) {
    // Breathing effect
    const breathSpeed = this.state === 'idle' ? 0.8 : 
                        this.state === 'thinking' ? 2.0 : 1.2;
    this.breathPhase += deltaTime * breathSpeed;
    const breath = Math.sin(this.breathPhase) * 0.5 + 0.5;

    // Color lerp
    this.currentColor.lerp(this.targetColor, deltaTime * 3);
    
    // Core animation
    const coreScale = 1.0 + breath * 0.08 + this.pulseIntensity * 0.3 + audioLevel * 0.2;
    this.core.scale.setScalar(coreScale);
    this.core.material.color.copy(this.currentColor);
    this.core.material.opacity = 0.7 + breath * 0.3;
    
    // Core light
    this.coreLight.color.copy(this.currentColor);
    this.coreLight.intensity = 1.5 + breath * 1.0 + this.pulseIntensity * 3 + audioLevel * 2;
    
    // Inner detail ring
    this.innerDetail.rotation.z += deltaTime * 0.5;
    this.innerDetail.material.color.copy(this.currentColor);
    
    // Ring rotation and opacity
    for (const ring of this.rings) {
      ring.rotation.z += deltaTime * ring.userData.speed;
      const targetOpacity = ring.userData.baseOpacity + breath * 0.2 + audioLevel * 0.3;
      ring.material.opacity += (targetOpacity - ring.material.opacity) * deltaTime * 5;
      ring.material.color.copy(this.currentColor);
    }

    // Segmented ring rotation
    if (this.segmentedRing) {
      this.segmentedRing.rotation.z -= deltaTime * 0.05;
    }

    // Energy lines pulse
    for (const line of this.energyLines) {
      const phase = line.userData.phase + time * 2;
      const pulse = Math.sin(phase) * 0.5 + 0.5;
      line.material.opacity = 0.1 + pulse * 0.3 + audioLevel * 0.4;
      line.material.color.copy(this.currentColor);
    }

    // Glow sprite
    const glowScale = 3.0 + breath * 0.5 + this.pulseIntensity * 1.5 + audioLevel * 1.0;
    this.glowSprite.scale.set(glowScale, glowScale, 1);
    this.glowSprite.material.opacity = 0.6 + breath * 0.2 + audioLevel * 0.2;

    // Decay pulse
    this.pulseIntensity *= Math.max(0, 1 - deltaTime * 4);
  }
}
