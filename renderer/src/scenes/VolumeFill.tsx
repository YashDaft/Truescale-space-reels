// Scene "volume_fill" (flat): Earth pops in, the view zooms out as Jupiter rises
// (both drawn at their true size ratio), then Earths are thrown into Jupiter while
// it fills up and a counter runs to the fact-sheet number.
// The thrown Earths are an illustration; the counter is the real number.
//
// Parameters (see scene_catalog.json):
//   radius_ratio_fact: Jupiter's radius / Earth's, for the drawing
//   count_fact: the number the counter runs to

import React from 'react';
import {AbsoluteFill, Easing, interpolate, random, spring, useCurrentFrame, useVideoConfig} from 'remotion';
import {useFacts} from '../facts';
import {SceneProps} from '../types';

const C = {
	bg: '#23306e',
	bgDeep: '#18214f',
	ocean: '#3d8bfd',
	land: '#5cc57a',
	cream: '#f6dfb8',
	tan: '#e4ad72',
	rust: '#c97b4b',
	brown: '#8f5b3d',
	spot: '#d0543e',
};

const EARTH_R = 40;
const JUP = {x: 540, y: 1150};
const EARTH_SPOT = {x: 540, y: 600}; // where Earth waits above Jupiter
const FILL_START = 100; // frame when Earths start going in
const FILL_FINISH_BEFORE_END = 72; // frames left after the counter finishes
const DROPS = 45;

// A flat, friendly Earth: ocean, two land shapes and a soft shadow
const FlatEarth: React.FC<{x: number; y: number; r: number; turn?: number}> = ({x, y, r, turn = 0}) => (
	<g transform={`translate(${x} ${y}) rotate(${turn})`}>
		<clipPath id={`e${Math.round(x)}${Math.round(y)}`}>
			<circle r={r} />
		</clipPath>
		<g clipPath={`url(#e${Math.round(x)}${Math.round(y)})`}>
			<circle r={r} fill={C.ocean} />
			<ellipse cx={-r * 0.35} cy={-r * 0.2} rx={r * 0.45} ry={r * 0.32} fill={C.land} />
			<ellipse cx={r * 0.4} cy={r * 0.35} rx={r * 0.3} ry={r * 0.4} fill={C.land} />
			<circle cx={r * 0.45} cy={r * 0.15} r={r} fill="#000" opacity={0.16} />
		</g>
	</g>
);

const FlatJupiter: React.FC<{r: number; fill: number; frame: number; squash: number}> = ({r, fill, frame, squash}) => {
	const bands = [
		{y: -0.85, h: 0.25, c: C.tan},
		{y: -0.55, h: 0.18, c: C.rust},
		{y: -0.3, h: 0.2, c: C.cream},
		{y: -0.05, h: 0.22, c: C.brown},
		{y: 0.2, h: 0.16, c: C.tan},
		{y: 0.42, h: 0.2, c: C.rust},
		{y: 0.66, h: 0.3, c: C.tan},
	];
	// The fill level, with a gently moving wavy top edge
	const level = r - fill * 2 * r;
	let wave = `M ${-r} ${r} L ${-r} ${level}`;
	for (let x = -r; x <= r; x += 20) {
		wave += ` L ${x} ${level + Math.sin(x / 40 + frame / 5) * 10 * (fill > 0 && fill < 1 ? 1 : 0)}`;
	}
	wave += ` L ${r} ${level} L ${r} ${r} Z`;

	return (
		<g transform={`translate(${JUP.x} ${JUP.y}) scale(${1 + squash * 0.03} ${1 - squash * 0.03})`}>
			<clipPath id="jup">
				<circle r={r} />
			</clipPath>
			<pattern id="earths" width="34" height="34" patternUnits="userSpaceOnUse">
				<circle cx="10" cy="10" r="8" fill={C.ocean} />
				<circle cx="8" cy="8" r="3.5" fill={C.land} />
				<circle cx="27" cy="27" r="8" fill={C.ocean} />
				<circle cx="29" cy="25" r="3.5" fill={C.land} />
			</pattern>
			<g clipPath="url(#jup)">
				<circle r={r} fill={C.cream} />
				{bands.map((b, i) => (
					<rect key={i} x={-r} y={b.y * r} width={r * 2} height={b.h * r} fill={b.c} />
				))}
				<ellipse cx={r * 0.32} cy={r * 0.5} rx={r * 0.2} ry={r * 0.11} fill={C.spot} />
				<path d={wave} fill="#2b4fa8" />
				<path d={wave} fill="url(#earths)" />
				<circle cx={r * 0.35} cy={r * 0.2} r={r * 1.05} fill="#000" opacity={0.14} />
			</g>
		</g>
	);
};

export const VolumeFill: React.FC<SceneProps> = ({params}) => {
	const frame = useCurrentFrame();
	const {fps, durationInFrames} = useVideoConfig();
	const facts = useFacts();
	const radiusRatioFact = params.radius_ratio_fact as string;
	const countFact = params.count_fact as string;
	const FILL_END = durationInFrames - FILL_FINISH_BEFORE_END;

	// True sizes: Jupiter's radius is Earth's times the fact-sheet ratio
	const jupiterR = EARTH_R * facts.value(radiusRatioFact);
	const target = facts.value(countFact);

	// Earth pops in, zoomed in close
	const earthPop = spring({frame: frame - 3, fps, config: {damping: 8, stiffness: 140}});
	// Then the view zooms out while Jupiter rises into place
	const zoomOut = interpolate(frame, [48, 82], [0, 1], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp', easing: Easing.inOut(Easing.cubic)});
	const jupiterRise = spring({frame: frame - 52, fps, config: {damping: 12, stiffness: 90}});
	const zoom = 2.7 - 1.7 * zoomOut;
	const focusX = 540 + (EARTH_SPOT.x - 540) * zoomOut;
	const focusY = 960 + (EARTH_SPOT.y - 960) * zoomOut;

	// Filling up: speeds up as it goes
	const fill = interpolate(frame, [FILL_START, FILL_END], [0, 1], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp', easing: Easing.in(Easing.quad)});
	const done = frame >= FILL_END;
	// While counting, the number is worked out from the fact; at the end it shows the fact sheet's own text
	const counter = done ? facts.display[countFact] : Math.round(target * fill).toLocaleString('en-US');

	// Jupiter wobbles a little each time an Earth lands, and once more at the end
	const drops = new Array(DROPS).fill(0).map((_, i) => FILL_START + (FILL_END - FILL_START - 18) * (i / DROPS) ** 0.7);
	const lastLanding = Math.max(...drops.map((d) => d + 16).filter((t) => t <= frame), -100);
	const squash =
		Math.exp(-(frame - lastLanding) / 4) * Math.sin((frame - lastLanding) / 1.5) * 0.6 +
		(frame > FILL_END ? Math.exp(-(frame - FILL_END) / 8) * Math.sin((frame - FILL_END) / 2) * 2 : 0);

	const earthVisible = frame < FILL_START + 4;
	const earthDrop = interpolate(frame, [FILL_START - 6, FILL_START + 10], [0, 1], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp', easing: Easing.in(Easing.quad)});

	return (
		<AbsoluteFill style={{background: `radial-gradient(circle at 50% 60%, ${C.bg}, ${C.bgDeep} 75%)`}}>
			<svg width={1080} height={1920}>
				{/* Simple flat stars */}
				{new Array(40).fill(0).map((_, i) => (
					<circle key={i} cx={random(`fx${i}`) * 1080} cy={random(`fy${i}`) * 1920} r={2 + random(`fr${i}`) * 3} fill="#fff" opacity={0.25 + 0.2 * Math.sin(frame / 10 + i)} />
				))}

				<g transform={`translate(${focusX} ${focusY}) scale(${zoom}) translate(${-EARTH_SPOT.x} ${-EARTH_SPOT.y})`}>
					{/* Falling Earths, drawn before Jupiter so they disappear into it */}
					{drops.map((start, i) => {
						const t = (frame - start) / 16;
						if (t < 0 || t > 1.1) return null;
						// Thrown in from alternate sides, landing on Jupiter's top
						const side = i % 2 === 0 ? -1 : 1;
						const startX = JUP.x + side * 620;
						const endX = JUP.x + (random(`dx${i}`) - 0.5) * 200;
						const x = startX + (endX - startX) * t;
						const top = JUP.y - jupiterR;
						const y = top + 60 - Math.sin(Math.min(t, 1) * Math.PI) * 240 + (t > 1 ? (t - 1) * 600 : 0);
						return <FlatEarth key={i} x={x} y={y} r={EARTH_R} turn={t * 200} />;
					})}

					<g transform={`translate(0 ${(1 - jupiterRise) * 1300})`}>
						<FlatJupiter r={jupiterR} fill={fill} frame={frame} squash={squash} />
					</g>

					{earthVisible ? (
						<g transform={`translate(${EARTH_SPOT.x} ${EARTH_SPOT.y + earthDrop * 140}) scale(${earthPop}) translate(${-EARTH_SPOT.x} ${-EARTH_SPOT.y})`}>
							<FlatEarth x={EARTH_SPOT.x} y={EARTH_SPOT.y} r={EARTH_R} turn={frame * 0.6} />
						</g>
					) : null}
				</g>
			</svg>

			{/* The counter, sitting on Jupiter while it fills */}
			{frame >= FILL_START ? (
				<div
					style={{
						position: 'absolute',
						left: 0,
						right: 0,
						top: JUP.y - 90,
						textAlign: 'center',
						fontFamily: 'Fredoka',
						fontWeight: 600,
						fontSize: done ? 170 : 150,
						color: '#fff',
						textShadow: '0 8px 0 rgba(0,0,0,0.25)',
						transform: `scale(${done ? 1 + Math.max(0, Math.sin((frame - FILL_END) / 3)) * Math.exp(-(frame - FILL_END) / 10) * 0.2 : 1})`,
					}}
				>
					{counter}
				</div>
			) : null}

		</AbsoluteFill>
	);
};
