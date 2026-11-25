// Scene "orbit_clock" (line): planets drawn as thin circles and dots at their
// real relative distances, moving at their real relative speeds through one
// Earth year. Each planet's label counts its laps (or, for planets slower than
// Earth, how much of one lap it has done). The highlighted planet clicks on each lap.
// Orbits are drawn as circles (the real ones are slightly oval); the footnote says so.
//
// Parameters (see scene_catalog.json): planets, highlight, footnote

import React from 'react';
import {AbsoluteFill, Audio, Easing, interpolate, Sequence, staticFile, useCurrentFrame, useVideoConfig} from 'remotion';
import {useFacts} from '../facts';
import {LINE_COLORS} from '../styles/line';
import {SceneProps} from '../types';

const {ink: INK, dim: DIM, accent: ACCENT, background: BACKGROUND} = LINE_COLORS;
const CENTER = {x: 540, y: 1000};
const OUTER_ORBIT_PX = 460; // the outermost planet's orbit gets this radius
const RUN_START = 50; // frame when the year starts (after the orbits are drawn)
const RUN_FINISH_BEFORE_END = 45; // frames left after the year ends

const NAMES: Record<string, string> = {mercury: 'Mercury', venus: 'Venus', earth: 'Earth', mars: 'Mars'};

export const OrbitClock: React.FC<SceneProps> = ({params}) => {
	const frame = useCurrentFrame();
	const {durationInFrames} = useVideoConfig();
	const facts = useFacts();
	const planets = params.planets as string[];
	const highlight = params.highlight as string;
	const footnote = params.footnote as string;
	const RUN_END = durationInFrames - RUN_FINISH_BEFORE_END;

	// Distances to scale: the outermost planet shown sets the scale
	const maxDistance = Math.max(...planets.map((p) => facts.value(`${p}_distance_mkm`)));
	const pxPerMkm = OUTER_ORBIT_PX / maxDistance;
	const yearDays = facts.value('earth_period_days');

	// Days pass slowly at first, faster in the middle, slowly at the end
	const dayOnFrame = (f: number) =>
		interpolate(f, [RUN_START, RUN_END], [0, yearDays], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp', easing: Easing.inOut(Easing.sin)});
	const days = dayOnFrame(frame);
	const zoom = interpolate(frame, [0, durationInFrames], [1.0, 1.07]);

	// A click each time the highlighted planet finishes a lap
	const highlightPeriod = facts.value(`${highlight}_period_days`);
	const lapCount = Math.floor(yearDays / highlightPeriod);
	const lapClickFrames = Array.from({length: lapCount}, (_, k) => {
		const lapDay = (k + 1) * highlightPeriod;
		let f = RUN_START;
		while (f < RUN_END && dayOnFrame(f) < lapDay) f++;
		return f;
	});

	return (
		<AbsoluteFill style={{background: BACKGROUND}}>
			<svg width={1080} height={1920}>
				<g transform={`translate(${CENTER.x} ${CENTER.y}) scale(${zoom})`}>
					{/* Faint cross-hair through the Sun */}
					<line x1={-520} y1={0} x2={520} y2={0} stroke={DIM} strokeWidth={1} opacity={0.35} />
					<line x1={0} y1={-520} x2={0} y2={520} stroke={DIM} strokeWidth={1} opacity={0.35} />

					<circle r={9 + Math.sin(frame / 8) * 1.5} fill={ACCENT} />
					<circle r={22} fill="none" stroke={ACCENT} strokeWidth={1} opacity={0.4} />

					{planets.map((name, i) => {
						const r = facts.value(`${name}_distance_mkm`) * pxPerMkm;
						const period = facts.value(`${name}_period_days`);
						const circumference = 2 * Math.PI * r;
						const draw = interpolate(frame, [i * 6, i * 6 + 30], [0, 1], {
							extrapolateLeft: 'clamp',
							extrapolateRight: 'clamp',
							easing: Easing.out(Easing.cubic),
						});

						// Position on the orbit, starting at the top and going clockwise
						const turns = days / period;
						const angle = -Math.PI / 2 + turns * 2 * Math.PI;
						const x = Math.cos(angle) * r;
						const y = Math.sin(angle) * r;

						// A trail behind the planet: up to a third of its orbit
						const trailTurns = Math.min(turns, 0.33);
						const trailStart = angle - trailTurns * 2 * Math.PI;
						const trail =
							trailTurns > 0.001 ? `M ${Math.cos(trailStart) * r} ${Math.sin(trailStart) * r} A ${r} ${r} 0 0 1 ${x} ${y}` : '';

						// Planets slower than Earth show how much of one lap they've done
						const laps = Math.floor(turns + 1e-9);
						const label = period > yearDays ? `${Math.round(turns * 100)}%` : `${laps} ${laps === 1 ? 'lap' : 'laps'}`;
						const isHighlight = name === highlight;

						// Labels go on the left of the dot near the right edge, so they never run off screen
						const labelOnLeft = x > 150;
						const labelX = labelOnLeft ? x - 20 : x + 20;
						const anchor = labelOnLeft ? 'end' : 'start';

						return (
							<g key={name}>
								<circle
									r={r}
									fill="none"
									stroke={INK}
									strokeOpacity={0.28}
									strokeWidth={1.5}
									strokeDasharray={circumference}
									strokeDashoffset={circumference * (1 - draw)}
									transform="rotate(-90)"
								/>
								{trail ? <path d={trail} fill="none" stroke={isHighlight ? ACCENT : INK} strokeWidth={3} strokeOpacity={0.8} strokeLinecap="round" /> : null}
								<g opacity={draw}>
									<circle cx={x} cy={y} r={isHighlight ? 11 : 9} fill={isHighlight ? ACCENT : INK} />
									<text x={labelX} y={y - 14} textAnchor={anchor} fill={isHighlight ? ACCENT : INK} fontFamily="Inter" fontWeight={500} fontSize={30}>
										{NAMES[name]}
									</text>
									<text x={labelX} y={y + 22} textAnchor={anchor} fill={DIM} fontFamily="Inter" fontWeight={300} fontSize={28}>
										{frame >= RUN_START ? label : ''}
									</text>
								</g>
							</g>
						);
					})}
				</g>
			</svg>

			<div style={{position: 'absolute', left: 80, right: 80, top: 1540, fontFamily: 'Inter', fontWeight: 300, fontSize: 46, color: INK}}>
				Day <span style={{color: ACCENT}}>{Math.floor(days)}</span>
				<span style={{color: DIM}}> of one Earth year</span>
			</div>
			<div style={{position: 'absolute', left: 80, right: 80, top: 1620, fontFamily: 'Inter', fontWeight: 300, fontSize: 26, color: DIM, lineHeight: 1.5}}>
				{facts.text(footnote)}
			</div>

			{lapClickFrames.map((f, i) => (
				<Sequence key={i} from={f} layout="none">
					<Audio src={staticFile('sfx/click.wav')} volume={0.9} />
				</Sequence>
			))}
		</AbsoluteFill>
	);
};
