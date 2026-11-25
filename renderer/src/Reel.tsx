// Turns a storyboard and a fact sheet into the video.
// For each scene in order: the scene's pictures, then the style's text beats,
// then its sound effects. The music plays under the whole reel, and the
// style's overlay (if it has one) sits on top of everything.

import React, {useEffect, useState} from 'react';
import {AbsoluteFill, Audio, continueRender, delayRender, Sequence, Series, staticFile, useVideoConfig} from 'remotion';
import './loadFonts';
import {FactsProvider} from './facts';
import {texturesReady} from './Planets';
import {SCENES} from './scenes';
import {STYLES} from './styles';
import {Beat, ReelProps, Sound} from './types';

export const FPS = 30;
export const toFrames = (seconds: number) => Math.round(seconds * FPS);

// Shows each text beat between its start and end time
const Beats: React.FC<{beats: Beat[]; Text: React.FC<{beat: Beat}>}> = ({beats, Text}) => {
	const {fps} = useVideoConfig();
	return (
		<>
			{beats.map((beat, i) => (
				<Sequence key={i} from={Math.round(beat.at * fps)} durationInFrames={Math.round((beat.until - beat.at) * fps)} layout="none">
					<Text beat={beat} />
				</Sequence>
			))}
		</>
	);
};

// Plays each sound effect at its start time
const Sounds: React.FC<{sounds: Sound[]}> = ({sounds}) => {
	const {fps} = useVideoConfig();
	return (
		<>
			{sounds.map((sound, i) => (
				<Sequence key={i} from={Math.round(sound.at * fps)} layout="none">
					<Audio src={staticFile(`sfx/${sound.file}`)} volume={sound.volume ?? 0.8} />
				</Sequence>
			))}
		</>
	);
};

export const Reel: React.FC<ReelProps> = ({storyboard, factSheet}) => {
	// Wait for the Earth and Sun images before showing any scene
	const [handle] = useState(() => delayRender('Loading textures'));
	const [ready, setReady] = useState(false);
	useEffect(() => {
		texturesReady.then(() => {
			setReady(true);
			continueRender(handle);
		});
	}, [handle]);

	if (!ready) {
		return null;
	}

	// The storyboard was already checked in calculateMetadata (Root.tsx),
	// so the style and every scene name exist here
	const style = STYLES[storyboard.style];

	return (
		<FactsProvider factSheet={factSheet}>
			<AbsoluteFill style={{background: '#000'}}>
				<Audio src={staticFile(`sfx/${storyboard.music}`)} volume={storyboard.music_volume} />
				<Series>
					{storyboard.scenes.map((spec, i) => {
						const Scene = SCENES[spec.scene];
						return (
							<Series.Sequence key={i} durationInFrames={toFrames(spec.seconds)}>
								<Scene params={spec.params ?? {}} />
								<Beats beats={spec.beats ?? []} Text={style.Text} />
								<Sounds sounds={spec.sounds ?? []} />
							</Series.Sequence>
						);
					})}
				</Series>
				{style.Overlay ? <style.Overlay /> : null}
			</AbsoluteFill>
		</FactsProvider>
	);
};
