/**
 * ULTRON — Arc Reactor 3D Component
 * 
 * MCU-accurate Arc Reactor facing the camera — concentric glowing rings,
 * bright core, hexagonal pattern, energy pulses, scanning lines.
 */

import * as THREE from 'https://cdn.jsdelivr.net/npm/three@0.160.0/build/three.module.js';

const COLORS = {
  core: 0x00bbff,
  coreHot: 0x66eeff,
  ring1: 0x0099dd,
  ring2: 0x0077bb,
  ring3: 0x005599,
  glow: 0x00aaff,
  energy: 0x00ddff,
};

export class ArcReactor {
  constructor(scene) {
    this.scene = scene;
    this.group = new THREE.Group();
    this.state = 'idle';
    this.breathPhase = 0;
    this.pulseIntensity = 0;
    this.targetColor = new THREE.Color(COLORS.core);
    this.currentColor = new THREE.Color(COLORS.core);
    
    this._buildCore();
    this._buildRings();
    this._buildEnergyLines();
    this._buildHexGrid();
    this._buildScanLine();
    this._buildGlow();
    
    scene.add(this.group);
  }

  _buildCore() {
    // Bright central sphere
    const coreGeo = new THREE.SphereGeometry(0.25, 32, 32);
    const coreMat = new THREE.MeshBasicMaterial({
      color: COLORS.coreHot,
      transparent: true,
      opacity: 0.95,
    });
    this.core = new THREE.Mesh(coreGeo, coreMat);
    this.group.add(this.core);

    // Strong point light from core
    this.coreLight = new THREE.PointLight(COLORS.core, 3, 12);
    this.group.add(this.coreLight);

    // Inner thin ring right around core
    const innerGeo = new THREE.RingGeometry(0.28, 0.3, 64);
    const innerMat = new THREE.MeshBasicMaterial({
      color: COLORS.coreHot,
      transparent: true,
      opacity: 0.6,
      side: THREE.DoubleSide,
    });
    this.innerRing = new THREE.Mesh(innerGeo, innerMat);
    this.group.add(this.innerRing);
  }

  _buildRings() {
    this.rings = [];

    // FLAT rings facing camera (using RingGeometry, NOT torus)
    // [innerR, outerR, color, speed, opacity]
    const ringConfigs = [
      [0.45, 0.47, COLORS.ring1, 0.4, 0.6],
      [0.60, 0.615, COLORS.ring1, -0.3, 0.5],
      [0.75, 0.76, COLORS.ring2, 0.2, 0.4],
      [0.90, 0.91, COLORS.ring3, -0.15, 0.35],
      [1.05, 1.055, COLORS.ring3, 0.1, 0.25],
    ];

    for (const [innerR, outerR, color, speed, opacity] of ringConfigs) {
      const geo = new THREE.RingGeometry(innerR, outerR, 128);
      const mat = new THREE.MeshBasicMaterial({
        color,
        transparent: true,
        opacity,
        side: THREE.DoubleSide,
      });
      const ring = new THREE.Mesh(geo, mat);
      ring.userData = { speed, baseOpacity: opacity };
      this.rings.push(ring);
      this.group.add(ring);
    }

    // Dashed ring (segmented, like gauge marks)
    this._buildDashedRing(1.15, 80);
    this._buildDashedRing(0.52, 40);
  }

  _buildDashedRing(radius, segments) {
    const group = new THREE.Group();
    for (let i = 0; i < segments; i++) {
      const angle = (i / segments) * Math.PI * 2;
      const isMajor = i % 5 === 0;
      const length = isMajor ? 0.06 : 0.03;
      const width = isMajor ? 0.004 : 0.002;
      
      const geo = new THREE.PlaneGeometry(width, length);
      const mat = new THREE.MeshBasicMaterial({
        color: COLORS.ring2,
        transparent: true,
        opacity: isMajor ? 0.5 : 0.25,
        side: THREE.DoubleSide,
      });
      const tick = new THREE.Mesh(geo, mat);
      tick.position.x = Math.cos(angle) * radius;
      tick.position.y = Math.sin(angle) * radius;
      tick.rotation.z = angle + Math.PI / 2;
      group.add(tick);
    }
    this.group.add(group);
    if (!this.dashedRings) this.dashedRings = [];
    this.dashedRings.push(group);
  }

  _buildEnergyLines() {
    this.energyLines = [];
    const count = 16;
    
    for (let i = 0; i < count; i++) {
      const angle = (i / count) * Math.PI * 2;
      const innerR = 0.3;
      const outerR = 0.44;
      
      const points = [
        new THREE.Vector3(Math.cos(angle) * innerR, Math.sin(angle) * innerR, 0),
        new THREE.Vector3(Math.cos(angle) * outerR, Math.sin(angle) * outerR, 0),
      ];
      
      const geo = new THREE.BufferGeometry().setFromPoints(points);
      const mat = new THREE.LineBasicMaterial({
        color: COLORS.energy,
        transparent: true,
        opacity: 0.4,
      });
      const line = new THREE.Line(geo, mat);
      line.userData = { angle, phase: Math.random() * Math.PI * 2 };
      this.energyLines.push(line);
      this.group.add(line);
    }
  }

  _buildHexGrid() {
    // Subtle hexagonal pattern between rings
    this.hexGroup = new THREE.Group();
    const hexRadius = 0.04;
    const rings = 8;
    
    for (let ring = 3; ring < rings; ring++) {
      const circumference = ring * 6;
      const dist = ring * hexRadius * 1.8;
      
      for (let i = 0; i < circumference; i++) {
        const angle = (i / circumference) * Math.PI * 2;
        // Only draw if within reactor area
        if (dist > 0.35 && dist < 1.1) {
          const hex = this._createHexOutline(hexRadius * 0.7);
          hex.position.x = Math.cos(angle) * dist;
          hex.position.y = Math.sin(angle) * dist;
          hex.material.opacity = 0.08 + Math.random() * 0.06;
          this.hexGroup.add(hex);
        }
      }
    }
    this.group.add(this.hexGroup);
  }

  _createHexOutline(radius) {
    const points = [];
    for (let i = 0; i <= 6; i++) {
      const a = (i / 6) * Math.PI * 2;
      points.push(new THREE.Vector3(Math.cos(a) * radius, Math.sin(a) * radius, 0));
    }
    const geo = new THREE.BufferGeometry().setFromPoints(points);
    const mat = new THREE.LineBasicMaterial({
      color: COLORS.ring2,
      transparent: true,
      opacity: 0.1,
    });
    return new THREE.Line(geo, mat);
  }

  _buildScanLine() {
    // Rotating scan line (like radar sweep)
    const points = [
      new THREE.Vector3(0, 0, 0.01),
      new THREE.Vector3(1.2, 0, 0.01),
    ];
    const geo = new THREE.BufferGeometry().setFromPoints(points);
    const mat = new THREE.LineBasicMaterial({
      color: COLORS.energy,
      transparent: true,
      opacity: 0.15,
    });
    this.scanLine = new THREE.Line(geo, mat);
    this.group.add(this.scanLine);
  }

  _buildGlow() {
    // Multi-layer glow
    for (let i = 0; i < 3; i++) {
      const canvas = document.createElement('canvas');
      canvas.width = 256;
      canvas.height = 256;
      const ctx = canvas.getContext('2d');
      
      const size = [0.4, 0.2, 0.1][i];
      const alpha = [0.25, 0.4, 0.6][i];
      const gradient = ctx.createRadialGradient(128, 128, 0, 128, 128, 128);
      gradient.addColorStop(0, `rgba(0, 200, 255, ${alpha})`);
      gradient.addColorStop(0.4, `rgba(0, 140, 255, ${alpha * 0.4})`);
      gradient.addColorStop(1, 'rgba(0, 0, 0, 0)');
      ctx.fillStyle = gradient;
      ctx.fillRect(0, 0, 256, 256);
      
      const tex = new THREE.CanvasTexture(canvas);
      const sprite = new THREE.Sprite(new THREE.SpriteMaterial({
        map: tex,
        transparent: true,
        blending: THREE.AdditiveBlending,
      }));
      const scale = [4.5, 2.5, 1.5][i];
      sprite.scale.set(scale, scale, 1);
      
      if (i === 0) this.outerGlow = sprite;
      this.group.add(sprite);
    }
  }

  setState(state) {
    this.state = state;
    const colorMap = {
      idle: COLORS.core,
      listening: 0x00ff88,
      thinking: 0xffaa00,
      speaking: COLORS.coreHot,
    };
    this.targetColor.set(colorMap[state] || COLORS.core);
  }

  pulse(intensity = 1.0) {
    this.pulseIntensity = intensity;
  }

  update(time, deltaTime, audioLevel = 0) {
    const breathSpeed = this.state === 'idle' ? 0.8 : 
                        this.state === 'thinking' ? 2.5 : 1.3;
    this.breathPhase += deltaTime * breathSpeed;
    const breath = Math.sin(this.breathPhase) * 0.5 + 0.5;

    this.currentColor.lerp(this.targetColor, deltaTime * 3);
    
    // Core
    const coreScale = 1.0 + breath * 0.1 + this.pulseIntensity * 0.4 + audioLevel * 0.3;
    this.core.scale.setScalar(coreScale);
    this.core.material.color.copy(this.currentColor);
    this.core.material.opacity = 0.8 + breath * 0.2;
    
    this.coreLight.color.copy(this.currentColor);
    this.coreLight.intensity = 2 + breath * 1.5 + this.pulseIntensity * 4 + audioLevel * 3;
    
    // Inner ring
    this.innerRing.rotation.z += deltaTime * 0.3;
    this.innerRing.material.color.copy(this.currentColor);
    
    // Concentric rings
    for (const ring of this.rings) {
      ring.rotation.z += deltaTime * ring.userData.speed;
      ring.material.opacity = ring.userData.baseOpacity + breath * 0.15 + audioLevel * 0.2;
      ring.material.color.copy(this.currentColor);
    }

    // Dashed rings
    if (this.dashedRings) {
      for (const dr of this.dashedRings) {
        dr.rotation.z -= deltaTime * 0.08;
      }
    }

    // Energy lines
    for (const line of this.energyLines) {
      const p = Math.sin(line.userData.phase + time * 3) * 0.5 + 0.5;
      line.material.opacity = 0.15 + p * 0.35 + audioLevel * 0.3;
      line.material.color.copy(this.currentColor);
    }

    // Scan line rotation
    if (this.scanLine) {
      this.scanLine.rotation.z = time * 0.5;
      this.scanLine.material.opacity = 0.08 + breath * 0.08;
    }

    // Hex grid subtle pulse
    if (this.hexGroup) {
      this.hexGroup.rotation.z += deltaTime * 0.02;
    }

    // Outer glow
    if (this.outerGlow) {
      const glowScale = 4.0 + breath * 0.8 + this.pulseIntensity * 2 + audioLevel * 1.5;
      this.outerGlow.scale.set(glowScale, glowScale, 1);
    }

    // Decay pulse
    this.pulseIntensity *= Math.max(0, 1 - deltaTime * 4);
  }
}
