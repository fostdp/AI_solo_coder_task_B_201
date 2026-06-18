import * as THREE from "three";
import { OrbitControls } from "three/addons/controls/OrbitControls.js";
import type { GeometryPart, SimDefect } from "./api";

export class VirtualWaxViewer {
  private container: HTMLElement;
  private scene: THREE.Scene;
  private camera: THREE.PerspectiveCamera;
  private renderer: THREE.WebGLRenderer;
  private controls: OrbitControls;
  private waxGroup: THREE.Group;
  private shellGroup: THREE.Group;
  private particleSystem: THREE.Points | null = null;
  private defectMarkers: THREE.Group;
  private animationId: number = 0;
  private autoRotate: boolean = true;
  private fillingProgress: number = 0;
  private showingShell: boolean = false;
  private showDefects: boolean = false;
  private waxColor: string = "#ffd9a0";
  private metalColor: string = "#b87333";

  constructor(container: HTMLElement) {
    this.container = container;

    this.scene = new THREE.Scene();
    this.scene.background = new THREE.Color(0x05030a);
    this.scene.fog = new THREE.FogExp2(0x05030a, 0.12);

    const { clientWidth, clientHeight } = container;
    this.camera = new THREE.PerspectiveCamera(45, clientWidth / clientHeight, 0.1, 1000);
    this.camera.position.set(3.5, 2.2, 3.5);

    this.renderer = new THREE.WebGLRenderer({ antialias: true, alpha: true });
    this.renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
    this.renderer.setSize(clientWidth, clientHeight);
    this.renderer.shadowMap.enabled = true;
    this.renderer.shadowMap.type = THREE.PCFSoftShadowMap;
    this.renderer.toneMapping = THREE.ACESFilmicToneMapping;
    this.renderer.toneMappingExposure = 1.1;
    container.appendChild(this.renderer.domElement);

    this.controls = new OrbitControls(this.camera, this.renderer.domElement);
    this.controls.enableDamping = true;
    this.controls.dampingFactor = 0.08;
    this.controls.minDistance = 1.5;
    this.controls.maxDistance = 12;
    this.controls.autoRotate = this.autoRotate;
    this.controls.autoRotateSpeed = 0.8;

    this.waxGroup = new THREE.Group();
    this.scene.add(this.waxGroup);

    this.shellGroup = new THREE.Group();
    this.shellGroup.visible = false;
    this.scene.add(this.shellGroup);

    this.defectMarkers = new THREE.Group();
    this.defectMarkers.visible = false;
    this.scene.add(this.defectMarkers);

    this._setupLights();
    this._addGround();
    this._animate();

    window.addEventListener("resize", this._onResize);
  }

  private _setupLights() {
    const ambient = new THREE.AmbientLight(0x404060, 0.5);
    this.scene.add(ambient);

    const mainLight = new THREE.DirectionalLight(0xffeedd, 1.2);
    mainLight.position.set(4, 6, 3);
    mainLight.castShadow = true;
    mainLight.shadow.mapSize.width = 1024;
    mainLight.shadow.mapSize.height = 1024;
    mainLight.shadow.camera.near = 0.5;
    mainLight.shadow.camera.far = 20;
    mainLight.shadow.camera.left = -4;
    mainLight.shadow.camera.right = 4;
    mainLight.shadow.camera.top = 4;
    mainLight.shadow.camera.bottom = -4;
    this.scene.add(mainLight);

    const fillLight = new THREE.DirectionalLight(0x8899ff, 0.35);
    fillLight.position.set(-3, 2, -2);
    this.scene.add(fillLight);

    const rimLight = new THREE.PointLight(0xd4af37, 1.2, 8);
    rimLight.position.set(0, 2, -4);
    this.scene.add(rimLight);
  }

  private _addGround() {
    const groundGeo = new THREE.CircleGeometry(5, 48);
    const groundMat = new THREE.MeshStandardMaterial({
      color: 0x1a1208,
      roughness: 0.9,
      metalness: 0.1,
    });
    const ground = new THREE.Mesh(groundGeo, groundMat);
    ground.rotation.x = -Math.PI / 2;
    ground.position.y = -1.5;
    ground.receiveShadow = true;
    this.scene.add(ground);
  }

  private _createMaterial(color: string, emissive = 0, isWax = false): THREE.MeshStandardMaterial {
    return new THREE.MeshStandardMaterial({
      color: new THREE.Color(color),
      metalness: isWax ? 0.1 : 0.85,
      roughness: isWax ? 0.35 : 0.3,
      emissive: new THREE.Color(emissive),
      emissiveIntensity: isWax ? 0.15 : 0,
      transparent: isWax ? true : false,
      opacity: isWax ? 0.85 : 1,
    });
  }

  public buildWaxModel(parts: GeometryPart[], scale: number = 0.01) {
    while (this.waxGroup.children.length > 0) {
      const child = this.waxGroup.children[0];
      this.waxGroup.remove(child);
      if ((child as THREE.Mesh).geometry) (child as THREE.Mesh).geometry.dispose();
      if ((child as THREE.Mesh).material) {
        const mat = (child as THREE.Mesh).material as THREE.Material;
        mat.dispose();
      }
    }

    const waxMat = this._createMaterial(this.waxColor, 0x3a2815, true);

    parts.forEach((part) => {
      let mesh: THREE.Mesh | null = null;

      if (part.type === "cylinder") {
        const topR = (part.top_radius || 50) * scale;
        const botR = (part.bottom_radius || 50) * scale;
        const h = (part.height || 100) * scale;
        const geo = new THREE.CylinderGeometry(topR, botR, h, 32);
        mesh = new THREE.Mesh(geo, waxMat);
        const yOff = (part.y_offset || 0) * scale;
        mesh.position.y = yOff;
      } else if (part.type === "torus") {
        const r = (part.radius || 50) * scale;
        const tr = (part.tube_radius || 5) * scale;
        const geo = new THREE.TorusGeometry(r, tr, 16, 48);
        mesh = new THREE.Mesh(geo, waxMat);
        const yOff = (part.y_offset || 0) * scale;
        mesh.position.y = yOff;
      } else if (part.type === "sphere") {
        const r = (part.radius || 10) * scale;
        const geo = new THREE.SphereGeometry(r, 16, 16);
        mesh = new THREE.Mesh(geo, waxMat);
        mesh.position.set(
          (part.x || 0) * scale,
          (part.y || 0) * scale,
          (part.z || 0) * scale
        );
      } else if (part.type === "ellipsoid") {
        const xr = (part.x_radius || 10) * scale;
        const yr = (part.y_radius || 15) * scale;
        const zr = (part.z_radius || 3) * scale;
        const geo = new THREE.SphereGeometry(1, 16, 16);
        mesh = new THREE.Mesh(geo, waxMat);
        mesh.scale.set(xr, yr, zr);
        const yOff = (part.y_offset || 0) * scale;
        mesh.position.y = yOff;
      }

      if (mesh) {
        mesh.castShadow = true;
        mesh.receiveShadow = true;
        this.waxGroup.add(mesh);
      }
    });

    this._buildShellModel(parts, scale);
  }

  private _buildShellModel(parts: GeometryPart[], scale: number) {
    while (this.shellGroup.children.length > 0) {
      const child = this.shellGroup.children[0];
      this.shellGroup.remove(child);
      if ((child as THREE.Mesh).geometry) (child as THREE.Mesh).geometry.dispose();
    }

    const shellMat = new THREE.MeshStandardMaterial({
      color: 0x8b7355,
      metalness: 0.1,
      roughness: 0.9,
      transparent: true,
      opacity: 0.7,
    });

    parts.forEach((part) => {
      let mesh: THREE.Mesh | null = null;
      const shellThickness = 0.06;

      if (part.type === "cylinder") {
        const topR = ((part.top_radius || 50) * scale) + shellThickness;
        const botR = ((part.bottom_radius || 50) * scale) + shellThickness;
        const h = ((part.height || 100) * scale) + shellThickness * 2;
        const geo = new THREE.CylinderGeometry(topR, botR, h, 32, 1, true);
        mesh = new THREE.Mesh(geo, shellMat);
        const yOff = (part.y_offset || 0) * scale;
        mesh.position.y = yOff;
      } else if (part.type === "torus") {
        const r = ((part.radius || 50) * scale) + shellThickness;
        const tr = ((part.tube_radius || 5) * scale) + shellThickness * 0.5;
        const geo = new THREE.TorusGeometry(r, tr, 12, 32);
        mesh = new THREE.Mesh(geo, shellMat);
        const yOff = (part.y_offset || 0) * scale;
        mesh.position.y = yOff;
      }

      if (mesh) {
        this.shellGroup.add(mesh);
      }
    });
  }

  public updateFilling(progress: number, avgTemp: number) {
    this.fillingProgress = progress;

    if (progress > 0) {
      const fillRatio = progress / 100;
      this.waxGroup.children.forEach((child) => {
        const mesh = child as THREE.Mesh;
        const mat = mesh.material as THREE.MeshStandardMaterial;
        const bronzeColor = new THREE.Color(this.metalColor);
        const waxColor = new THREE.Color(this.waxColor);
        const mixed = waxColor.clone().lerp(bronzeColor, fillRatio * 0.8);
        mat.color.copy(mixed);

        const heatIntensity = Math.max(0, (avgTemp - 500) / 1000) * fillRatio;
        mat.emissive.setHex(0xff4400);
        mat.emissiveIntensity = heatIntensity * 0.6;
      });
    }
  }

  public setAsMetal() {
    this.waxGroup.children.forEach((child) => {
      const mesh = child as THREE.Mesh;
      const mat = mesh.material as THREE.MeshStandardMaterial;
      mat.color.set(this.metalColor);
      mat.metalness = 0.85;
      mat.roughness = 0.3;
      mat.opacity = 1;
      mat.transparent = false;
      mat.emissiveIntensity = 0;
    });
  }

  public showShell(show: boolean) {
    this.showingShell = show;
    this.shellGroup.visible = show;
  }

  public setDefects(defects: SimDefect[], modelSize: number = 1.5) {
    while (this.defectMarkers.children.length > 0) {
      const child = this.defectMarkers.children[0];
      this.defectMarkers.remove(child);
      if ((child as THREE.Mesh).geometry) (child as THREE.Mesh).geometry.dispose();
    }

    const colorMap: Record<string, number> = {
      low: 0xffd93d,
      medium: 0xff8c1a,
      high: 0xff4d4d,
      critical: 0xff1a1a,
    };

    defects.forEach((defect) => {
      const size = 0.05 + defect.volume_cm3 * 0.03;
      const geo = new THREE.SphereGeometry(size, 12, 12);
      const color = colorMap[defect.severity] || 0xffd93d;
      const mat = new THREE.MeshBasicMaterial({
        color,
        transparent: true,
        opacity: 0.8,
      });
      const sphere = new THREE.Mesh(geo, mat);
      sphere.position.set(
        (defect.position.x - 0.5) * modelSize,
        (defect.position.y - 0.5) * modelSize - 0.3,
        (defect.position.z - 0.5) * modelSize
      );
      this.defectMarkers.add(sphere);

      const ringGeo = new THREE.RingGeometry(size * 1.2, size * 1.6, 16);
      const ringMat = new THREE.MeshBasicMaterial({
        color,
        transparent: true,
        opacity: 0.5,
        side: THREE.DoubleSide,
      });
      const ring = new THREE.Mesh(ringGeo, ringMat);
      ring.position.copy(sphere.position);
      ring.lookAt(this.camera.position);
      this.defectMarkers.add(ring);
    });
  }

  public toggleDefects(show: boolean) {
    this.showDefects = show;
    this.defectMarkers.visible = show;
  }

  public createParticles(count: number = 2000) {
    if (this.particleSystem) {
      this.scene.remove(this.particleSystem);
      (this.particleSystem.geometry as THREE.BufferGeometry).dispose();
      (this.particleSystem.material as THREE.Material).dispose();
    }

    const positions = new Float32Array(count * 3);
    const velocities = new Float32Array(count * 3);

    for (let i = 0; i < count; i++) {
      const i3 = i * 3;
      positions[i3] = (Math.random() - 0.5) * 1.5;
      positions[i3 + 1] = -1.8 + Math.random() * 0.3;
      positions[i3 + 2] = (Math.random() - 0.5) * 1.5;

      velocities[i3] = (Math.random() - 0.5) * 0.002;
      velocities[i3 + 1] = 0.003 + Math.random() * 0.008;
      velocities[i3 + 2] = (Math.random() - 0.5) * 0.002;
    }

    const geo = new THREE.BufferGeometry();
    geo.setAttribute("position", new THREE.BufferAttribute(positions, 3));
    (geo as any).velocities = velocities;

    const mat = new THREE.PointsMaterial({
      color: 0xff7a2e,
      size: 0.025,
      transparent: true,
      opacity: 0.85,
      blending: THREE.AdditiveBlending,
      depthWrite: false,
    });

    this.particleSystem = new THREE.Points(geo, mat);
    this.particleSystem.visible = false;
    this.scene.add(this.particleSystem);
  }

  public showParticles(show: boolean) {
    if (this.particleSystem) {
      this.particleSystem.visible = show;
    }
  }

  public setAutoRotate(value: boolean) {
    this.autoRotate = value;
    this.controls.autoRotate = value;
  }

  public setMetalColor(color: string) {
    this.metalColor = color;
  }

  public resetToWax() {
    this.waxGroup.children.forEach((child) => {
      const mesh = child as THREE.Mesh;
      const mat = mesh.material as THREE.MeshStandardMaterial;
      mat.color.set(this.waxColor);
      mat.metalness = 0.1;
      mat.roughness = 0.35;
      mat.opacity = 0.85;
      mat.transparent = true;
      mat.emissive.setHex(0x3a2815);
      mat.emissiveIntensity = 0.15;
    });
    this.fillingProgress = 0;
    this.defectMarkers.visible = false;
  }

  private _animate = () => {
    this.animationId = requestAnimationFrame(this._animate);
    this.controls.update();

    if (this.particleSystem && this.particleSystem.visible) {
      const positions = (this.particleSystem.geometry as THREE.BufferGeometry).attributes.position.array as Float32Array;
      const velocities = (this.particleSystem.geometry as any).velocities as Float32Array;
      const maxY = -0.5 + this.fillingProgress / 100 * 1.2;

      for (let i = 0; i < positions.length / 3; i++) {
        const i3 = i * 3;
        positions[i3] += velocities[i3];
        positions[i3 + 1] += velocities[i3 + 1];
        positions[i3 + 2] += velocities[i3 + 2];

        if (positions[i3 + 1] > maxY || Math.random() < 0.002) {
          positions[i3] = (Math.random() - 0.5) * 1.5;
          positions[i3 + 1] = -1.8;
          positions[i3 + 2] = (Math.random() - 0.5) * 1.5;
        }
      }
      (this.particleSystem.geometry as THREE.BufferGeometry).attributes.position.needsUpdate = true;
    }

    this.renderer.render(this.scene, this.camera);
  };

  private _onResize = () => {
    const { clientWidth, clientHeight } = this.container;
    this.camera.aspect = clientWidth / clientHeight;
    this.camera.updateProjectionMatrix();
    this.renderer.setSize(clientWidth, clientHeight);
  };

  public dispose() {
    window.removeEventListener("resize", this._onResize);
    cancelAnimationFrame(this.animationId);
    this.renderer.dispose();
    this.controls.dispose();

    [this.waxGroup, this.shellGroup, this.defectMarkers].forEach((group) => {
      group.traverse((obj) => {
        if (obj instanceof THREE.Mesh) {
          obj.geometry.dispose();
          if (Array.isArray(obj.material)) {
            obj.material.forEach((m) => m.dispose());
          } else {
            obj.material.dispose();
          }
        }
      });
    });

    if (this.particleSystem) {
      this.particleSystem.geometry.dispose();
      (this.particleSystem.material as THREE.Material).dispose();
    }
  }
}
