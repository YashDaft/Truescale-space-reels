// Line style: light, precise, left-aligned text with a rule drawn under it.

import React from 'react';
import {Easing, interpolate, useCurrentFrame, useVideoConfig} from 'remotion';
import {useFacts} from '../facts';
import {Beat} from '../types';

export const LINE_COLORS = {
	ink: '#e9eef3',
	dim: '#5d6672',
	accent: '#ffb547',
	background: '#06080c',
};

export const LineText: React.FC<{beat: Beat}> = ({beat}) => {
	const frame = useCurrentFrame();
	const {durationInFrames} = useVideoConfig();
	const facts = useFacts();
	const show = interpolate(frame, [0, 10], [0, 1], {extrapolateRight: 'clamp'});
	const rule = interpolate(frame, [4, 24], [0, 1], {extrapolateRight: 'clamp', easing: Easing.out(Easing.cubic)});
	const leave = interpolate(frame, [durationInFrames - 8, durationInFrames], [1, 0], {extrapolateLeft: 'clamp'});

	return (
		<div style={{position: 'absolute', left: 80, right: 80, top: 190, opacity: show * leave}}>
			<div style={{fontFamily: 'Inter', fontWeight: 300, fontSize: 74, lineHeight: 1.12, color: LINE_COLORS.ink}}>
				{facts.parts(beat.text).map((part, i) => (
					<span key={i} style={{color: part.isFact ? LINE_COLORS.accent : undefined, whiteSpace: part.isFact ? 'nowrap' : 'normal'}}>
						{part.text}
					</span>
				))}
			</div>
			<div style={{height: 2, background: LINE_COLORS.ink, opacity: 0.5, width: `${rule * 100}%`, marginTop: 26}} />
			{beat.subtext ? (
				<div style={{fontFamily: 'Inter', fontWeight: 300, fontSize: 42, color: LINE_COLORS.dim, marginTop: 22}}>
					{facts.text(beat.subtext)}
				</div>
			) : null}
		</div>
	);
};
