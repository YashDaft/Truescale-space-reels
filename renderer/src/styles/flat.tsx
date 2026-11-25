// Flat style: chunky rounded letters that bounce in.

import React from 'react';
import {interpolate, spring, useCurrentFrame, useVideoConfig} from 'remotion';
import {useFacts} from '../facts';
import {Beat} from '../types';

const TEXT = '#ffffff';
const ACCENT = '#ffd166';

export const FlatText: React.FC<{beat: Beat}> = ({beat}) => {
	const frame = useCurrentFrame();
	const {fps, durationInFrames} = useVideoConfig();
	const facts = useFacts();
	const pop = spring({frame, fps, config: {damping: 9, stiffness: 160}});
	const leave = interpolate(frame, [durationInFrames - 6, durationInFrames], [1, 0], {extrapolateLeft: 'clamp'});

	return (
		<div
			style={{
				position: 'absolute',
				left: 70,
				right: 70,
				top: 200,
				textAlign: 'center',
				fontFamily: 'Fredoka',
				fontWeight: 600,
				color: TEXT,
				transform: `scale(${pop})`,
				opacity: leave,
			}}
		>
			<div style={{fontSize: 88, lineHeight: 1.08}}>
				{facts.parts(beat.text).map((part, i) => (
					<span key={i} style={{color: part.isFact ? ACCENT : undefined, whiteSpace: part.isFact ? 'nowrap' : 'normal'}}>
						{part.text}
					</span>
				))}
			</div>
			{beat.subtext ? <div style={{fontSize: 40, opacity: 0.75, marginTop: 18}}>{facts.text(beat.subtext)}</div> : null}
		</div>
	);
};
