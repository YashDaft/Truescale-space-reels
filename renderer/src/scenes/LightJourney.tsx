// Scene "light_journey" (cinematic): the camera starts at the Sun's surface and
// flies backwards with the sunlight, past streaking stars, until Earth sweeps in
// as a sunlit crescent. Distances are NOT to scale: this style is about mood,
// so the numbers live in the text, not the picture.

import React, {useMemo} from 'react';
import * as THREE from 'three';
import {useThree} from '@react-three/fiber';
import {AbsoluteFill, Easing, interpolate, random, useCurrentFrame, useVideoConfig} from 'remotion';
import {ThreeCanvas} from '@remotion/three';
import {Earth, Sun, glowTexture} from '../Planets';
import {SceneProps} from '../types';

const PATH_LENGTH = 300; // how far the camera travels, in scene units
const PHOTONS = 1400;
const STREAKS = 700;

// Where the camera is on a given frame: slow near the Sun, fast in the middle, slow at the end
const cameraZ = (frame: number, total: number) =>
	interpolate(frame, [0, total], [7, PATH_LENGTH], {easing: Easing.inOut(Easing.cubic)});

const CameraRig: React.FC<{frame: number; total: number}> = ({frame, total}) => {
	const {camera} = useThree();
	camera.position.set(0.7 + Math.sin(frame / 60) * 0.25, 0.35, cameraZ(frame, total));
	camera.lookAt(0, 0, 0);
	return null;
};

// Points of light flowing outwards from the Sun, faster than the camera
const Photons: React.FC<{frame: number}> = ({frame}) => {
	const seeds = useMemo(
		() =>
			new Array(PHOTONS).fill(0).map((_, i) => ({
				z: random(`pz${i}`) * PATH_LENGTH,
				angle: random(`pa${i}`) * Math.PI * 2,
				spread: 0.4 + random(`pr${i}`) * 2.2,
			})),
		[],
	);
	const geometry = useMemo(() => new THREE.BufferGeometry(), []);
	const positions = new Float32Array(PHOTONS * 3);
	seeds.forEach((p, i) => {
		const z = (p.z + frame * 2.2) % PATH_LENGTH;
		const r = p.spread * (1 + z / 25); // the stream widens as it travels
		positions[i * 3] = Math.cos(p.angle) * r;
		positions[i * 3 + 1] = Math.sin(p.angle) * r;
		positions[i * 3 + 2] = z;
	});
	geometry.setAttribute('position', new THREE.BufferAttribute(positions, 3));

	const map = useMemo(() => glowTexture('#ffd08a'), []);
	return (
		<points geometry={geometry}>
			<pointsMaterial map={map} size={0.22} color="#ffd9a0" transparent opacity={0.75} depthWrite={false} blending={THREE.AdditiveBlending} />
		</points>
	);
};

// Stars beside the path, drawn as lines that stretch when the camera moves fast
const Streaks: React.FC<{frame: number; total: number}> = ({frame, total}) => {
	const seeds = useMemo(
		() =>
			new Array(STREAKS).fill(0).map((_, i) => ({
				x: (random(`sx${i}`) - 0.5) * 120,
				y: (random(`sy${i}`) - 0.5) * 200,
				z: random(`sz${i}`) * (PATH_LENGTH + 60),
			})),
		[],
	);
	const speed = cameraZ(frame + 1, total) - cameraZ(frame, total);
	const geometry = useMemo(() => new THREE.BufferGeometry(), []);
	const positions = new Float32Array(STREAKS * 6);
	seeds.forEach((s, i) => {
		positions.set([s.x, s.y, s.z, s.x, s.y, s.z - 0.2 - speed * 5], i * 6);
	});
	geometry.setAttribute('position', new THREE.BufferAttribute(positions, 3));
	return (
		<lineSegments geometry={geometry}>
			<lineBasicMaterial color="#cfd8ff" transparent opacity={0.55} />
		</lineSegments>
	);
};

export const LightJourney: React.FC<SceneProps> = () => {
	const frame = useCurrentFrame();
	const {width, height, durationInFrames} = useVideoConfig();
	const fadeIn = interpolate(frame, [0, 20], [0, 1], {extrapolateRight: 'clamp'});

	return (
		<AbsoluteFill style={{background: '#000'}}>
			<AbsoluteFill style={{opacity: fadeIn}}>
				<ThreeCanvas width={width} height={height} camera={{fov: 50, near: 0.1, far: 2000}}>
					<CameraRig frame={frame} total={durationInFrames} />
					<ambientLight intensity={0.02} />
					<pointLight position={[0, 0, 0]} intensity={9} decay={0} color="#fff1dd" />
					<Sun radius={2} spin={frame * 0.004} />
					<Photons frame={frame} />
					<Streaks frame={frame} total={durationInFrames} />
					{/* Placed so the camera passes it near the end and it sweeps in from the bottom right */}
					<Earth radius={3.1} spin={2.2 + frame * 0.003} position={[4.2, -6.4, PATH_LENGTH - 20]} />
				</ThreeCanvas>
			</AbsoluteFill>
		</AbsoluteFill>
	);
};
