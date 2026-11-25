// Cinematic style: large serif text that fades in from a soft blur,
// plus dark edges and moving film grain over the whole picture.

import React from 'react';
import {AbsoluteFill, Easing, interpolate, useCurrentFrame, useVideoConfig} from 'remotion';
import {useFacts} from '../facts';
import {Beat} from '../types';

const TEXT = '#f4ede2';
const ACCENT = '#ffd28f';

export const CinematicText: React.FC<{beat: Beat}> = ({beat}) => {
	const frame = useCurrentFrame();
	const {durationInFrames} = useVideoConfig();
	const facts = useFacts();
	const appear = interpolate(frame, [0, 18], [0, 1], {extrapolateRight: 'clamp', easing: Easing.out(Easing.quad)});
	const leave = interpolate(frame, [durationInFrames - 12, durationInFrames], [1, 0], {extrapolateLeft: 'clamp'});

	return (
		<div
			style={{
				position: 'absolute',
				left: 80,
				right: 80,
				top: 1180,
				textAlign: 'center',
				color: TEXT,
				opacity: appear * leave,
				filter: `blur(${(1 - appear) * 12}px)`,
				transform: `scale(${1.04 - appear * 0.04})`,
				textShadow: '0 2px 30px rgba(0,0,0,0.8)',
			}}
		>
			<div style={{fontFamily: 'Cormorant Garamond', fontWeight: 500, fontSize: 84, lineHeight: 1.15}}>
				{facts.parts(beat.text).map((part, i) => (
					<span key={i} style={{color: part.isFact ? ACCENT : undefined, whiteSpace: part.isFact ? 'nowrap' : 'normal'}}>
						{part.text}
					</span>
				))}
			</div>
			{beat.subtext ? (
				<div style={{fontFamily: 'Cormorant Garamond', fontWeight: 500, fontSize: 46, opacity: 0.75, marginTop: 20}}>
					{facts.text(beat.subtext)}
				</div>
			) : null}
		</div>
	);
};

export const CinematicOverlay: React.FC = () => {
	const frame = useCurrentFrame();
	const {width, height} = useVideoConfig();
	return (
		<>
			<AbsoluteFill style={{background: 'radial-gradient(ellipse at center, transparent 45%, rgba(0,0,0,0.75) 100%)'}} />
			<AbsoluteFill style={{opacity: 0.09, mixBlendMode: 'screen'}}>
				<svg width={width} height={height}>
					<filter id="grain">
						<feTurbulence type="fractalNoise" baseFrequency="0.9" numOctaves="2" seed={frame} />
					</filter>
					<rect width={width} height={height} filter="url(#grain)" />
				</svg>
			</AbsoluteFill>
		</>
	);
};
