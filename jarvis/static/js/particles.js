/**
 * ULTRON — Particle System
 * 
 * Ambient floating particles that drift through the scene.
 * Creates the atmosphere of a holographic environment.
 * 
 * Particles respond to system state:
 * - Idle: slow drift, low density
 * - Listening: particles flow toward center
 * - Thinking: orbital vortex
 * - Speaking: particles pulse outward with voice
 */

import * as THREE from 'https://cdn.jsdelivr.net/npm/three@0.160.0/build/three.module.js';

const PARTICLE_COUNT = 1500;

export class ParticleSystem {
  constructor(scene) {
    this.scene = scene;
    this.state = 'idle';
    
    this._buildParticles();
    this._buildDataStreams();
    
    scene.add(this.particleMesh);
  }

  _buildParticles() {
    const positions = new Float32Array(PARTICLE_COUNT * 3);
    const velocities = new Float32Array(PARTICLE_COUNT * 3);
    const sizes = new Float32Array(PARTICLE_COUNT);
    const alphas = new Float32Array(PARTICLE_COUNT);
    const phases = new Float32Array(PARTICLE_COUNT);

    for (let i = 0; i < PARTICLE_COUNT; i++) {
      const i3 = i * 3;
      // Distribute in a large sphere
      const r = 2 + Math.random() * 6;
      const theta = Math.random() * Math.PI * 2;
      const phi = Math.acos(2 * Math.random() - 1);
      
      positions[i3]     = r * Math.sin(phi) * Math.cos(theta);
      positions[i3 + 1] = r * Math.sin(phi) * Math.sin(theta);
      positions[i3 + 2] = (Math.random() - 0.5) * 3; // Flatter Z distribution
      
      velocities[i3]     = (Math.random() - 0.5) * 0.01;
      velocities[i3 + 1] = (Math.random() - 0.5) * 0.01;
      velocities[i3 + 2] = (Math.random() - 0.5) * 0.005;
      
      sizes[i] = 0.02 + Math.random() * 0.04;
      alphas[i] = 0.1 + Math.random() * 0.5;
      phases[i] = Math.random() * Math.PI * 2;
    }

    const geometry = new THREE.BufferGeometry();
    geometry.setAttribute('position', new THREE.BufferAttribute(positions, 3));
    geometry.setAttribute('aSize', new THREE.BufferAttribute(sizes, 1));
    geometry.setAttribute('aAlpha', new THREE.BufferAttribute(alphas, 1));
    
    this.velocities = velocities;
    this.phases = phases;

    // Custom shader for soft circular particles
    const material = new THREE.ShaderMaterial({
      uniforms: {
        uColor: { value: new THREE.Color(0x00aaff) },
        uTime: { value: 0 },
        uPixelRatio: { value: window.devicePixelRatio },
      },
      vertexShader: `
        attribute float aSize;
        attribute float aAlpha;
        varying float vAlpha;
        uniform float uTime;
        uniform float uPixelRatio;
        
        void main() {
          vAlpha = aAlpha;
          vec4 mvPos = modelViewMatrix * vec4(position, 1.0);
          gl_PointSize = aSize * uPixelRatio * (300.0 / -mvPos.z);
          gl_Position = projectionMatrix * mvPos;
        }
      `,
      fragmentShader: `
        uniform vec3 uColor;
        varying float vAlpha;
        
        void main() {
          // Soft circular particle
          float dist = length(gl_PointCoord - vec2(0.5));
          if (dist > 0.5) discard;
          
          float alpha = vAlpha * smoothstep(0.5, 0.1, dist);
          gl_FragColor = vec4(uColor, alpha);
        }
      `,
      transparent: true,
      blending: THREE.AdditiveBlending,
      depthWrite: false,
    });

    this.particleMesh = new THREE.Points(geometry, material);
    this.geometry = geometry;
    this.material = material;
  }

  _buildDataStreams() {
    // Vertical data stream lines (Matrix-style but subtle)
    this.dataStreams = [];
    const streamCount = 8;
    
    for (let i = 0; i < streamCount; i++) {
      const x = (Math.random() - 0.5) * 12;
      const z = (Math.random() - 0.5) * 2;
      const points = [];
      const segCount = 20;
      
      for (let j = 0; j < segCount; j++) {
        points.push(new THREE.Vector3(x, -4 + (j / segCount) * 8, z));
      }
      
      const geo = new THREE.BufferGeometry().setFromPoints(points);
      const mat = new THREE.LineBasicMaterial({
        color: 0x003366,
        transparent: true,
        opacity: 0.08,
      });
      const line = new THREE.Line(geo, mat);
      line.userData = { phase: Math.random() * Math.PI * 2, speed: 0.5 + Math.random() * 0.5 };
      this.dataStreams.push(line);
      this.scene.add(line);
    }
  }

  setState(state) {
    this.state = state;
    // Adjust particle color based on state
    switch (state) {
      case 'idle':
        this.material.uniforms.uColor.value.set(0x0088cc);
        break;
      case 'listening':
        this.material.uniforms.uColor.value.set(0x00cc88);
        break;
      case 'thinking':
        this.material.uniforms.uColor.value.set(0xccaa00);
        break;
      case 'speaking':
        this.material.uniforms.uColor.value.set(0x00bbff);
        break;
    }
  }

  update(time, deltaTime, audioLevel = 0) {
    this.material.uniforms.uTime.value = time;
    
    const positions = this.geometry.attributes.position.array;
    
    for (let i = 0; i < PARTICLE_COUNT; i++) {
      const i3 = i * 3;
      let x = positions[i3];
      let y = positions[i3 + 1];
      let z = positions[i3 + 2];
      
      const dist = Math.sqrt(x * x + y * y);
      
      if (this.state === 'idle') {
        // Gentle drift
        x += this.velocities[i3] + Math.sin(time * 0.3 + this.phases[i]) * 0.002;
        y += this.velocities[i3 + 1] + Math.cos(time * 0.2 + this.phases[i]) * 0.002;
        z += this.velocities[i3 + 2];
      } else if (this.state === 'listening') {
        // Flow toward center
        const pullStrength = 0.002;
        x -= x * pullStrength;
        y -= y * pullStrength;
        x += this.velocities[i3];
        y += this.velocities[i3 + 1];
      } else if (this.state === 'thinking') {
        // Orbital vortex
        const angle = Math.atan2(y, x);
        const orbitSpeed = 0.02 / Math.max(dist, 0.5);
        x += Math.cos(angle + Math.PI / 2) * orbitSpeed * dist;
        y += Math.sin(angle + Math.PI / 2) * orbitSpeed * dist;
        // Slight inward pull
        x -= x * 0.001;
        y -= y * 0.001;
      } else if (this.state === 'speaking') {
        // Pulse outward with audio
        const pushStrength = audioLevel * 0.01;
        const normalX = dist > 0.01 ? x / dist : 0;
        const normalY = dist > 0.01 ? y / dist : 0;
        x += normalX * pushStrength;
        y += normalY * pushStrength;
        x += this.velocities[i3];
        y += this.velocities[i3 + 1];
      }
      
      z += this.velocities[i3 + 2];
      
      // Boundary wrapping
      const maxR = 7;
      if (Math.sqrt(x * x + y * y) > maxR) {
        const angle = Math.random() * Math.PI * 2;
        const r = 1 + Math.random() * 2;
        x = Math.cos(angle) * r;
        y = Math.sin(angle) * r;
      }
      if (Math.abs(z) > 2) z *= -0.5;
      
      positions[i3] = x;
      positions[i3 + 1] = y;
      positions[i3 + 2] = z;
    }
    
    this.geometry.attributes.position.needsUpdate = true;

    // Data streams
    for (const stream of this.dataStreams) {
      const phase = stream.userData.phase + time * stream.userData.speed;
      stream.material.opacity = 0.03 + Math.sin(phase) * 0.05;
    }
  }
}
