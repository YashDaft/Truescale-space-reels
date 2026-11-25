// The 3D objects: Earth and the Sun, each with a soft glow.

import React, {useMemo} from 'react';
import * as THREE from 'three';
import {staticFile} from 'remotion';

// All textures are loaded once, before any scene is shown.
// The 3D canvas only redraws when the frame changes, so a texture that arrived
// after the first draw would stay black. Reel.tsx waits for texturesReady.
const loadTexture = (file: string) =>
	new Promise<THREE.Texture>((resolve, reject) => {
		new THREE.TextureLoader().load(
			staticFile(file),
			(texture) => {
				texture.colorSpace = THREE.SRGBColorSpace;
				resolve(texture);
			},
			undefined,
			reject,
		);
	});

const textures: Record<string, THREE.Texture> = {};

export const texturesReady = Promise.all([
	loadTexture('textures/earth.jpg').then((t) => (textures.earth = t)),
	loadTexture('textures/sun.png').then((t) => (textures.sun = t)),
]);

// A round, soft glow drawn on a small canvas, used for sprites and points
export const glowTexture = (color: string) => {
	const canvas = document.createElement('canvas');
	canvas.width = 256;
	canvas.height = 256;
	const ctx = canvas.getContext('2d')!;
	const gradient = ctx.createRadialGradient(128, 128, 0, 128, 128, 128);
	gradient.addColorStop(0, color);
	gradient.addColorStop(0.35, color + '88');
	gradient.addColorStop(1, color + '00');
	ctx.fillStyle = gradient;
	ctx.fillRect(0, 0, 256, 256);
	return new THREE.CanvasTexture(canvas);
};

const useGlow = (color: string) => useMemo(() => glowTexture(color), [color]);

export const Earth: React.FC<{radius: number; spin: number; position: [number, number, number]}> = ({radius, spin, position}) => {
	const glow = useGlow('#6fb4ff');
	return (
		<group position={position}>
			<sprite scale={[radius * 2.5, radius * 2.5, 1]}>
				<spriteMaterial map={glow} transparent opacity={0.35} depthWrite={false} blending={THREE.AdditiveBlending} />
			</sprite>
			{/* Tilted by Earth's axial tilt, about 0.41 radians */}
			<mesh rotation={[0.41, spin, 0]}>
				<sphereGeometry args={[radius, 96, 96]} />
				<meshStandardMaterial map={textures.earth} roughness={0.9} metalness={0} />
			</mesh>
		</group>
	);
};

export const Sun: React.FC<{radius: number; spin: number}> = ({radius, spin}) => {
	const glow = useGlow('#ffb347');
	return (
		<group>
			{/* A wide, faint glow, so the Sun still shines when far away */}
			<sprite scale={[radius * 18, radius * 18, 1]}>
				<spriteMaterial map={glow} transparent opacity={0.4} depthWrite={false} blending={THREE.AdditiveBlending} />
			</sprite>
			<sprite scale={[radius * 3.2, radius * 3.2, 1]}>
				<spriteMaterial map={glow} transparent opacity={0.55} depthWrite={false} blending={THREE.AdditiveBlending} />
			</sprite>
			{/* Tilted back so the texture's poles stay out of view */}
			<mesh rotation={[-0.8, spin, 0]}>
				<sphereGeometry args={[radius, 96, 96]} />
				<meshBasicMaterial map={textures.sun} />
			</mesh>
		</group>
	);
};
