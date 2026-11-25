// Registers the videos Remotion can render.
//
// "Reel" is the one the pipeline uses: it receives a storyboard and a fact
// sheet as input (--props=file.json). The three "Example..." videos use the
// files in examples/, for previewing in Remotion Studio and for the CI check.

import React from 'react';
import {CalculateMetadataFunction, Composition} from 'remotion';
import {Reel, FPS, toFrames} from './Reel';
import {SCENES} from './scenes';
import {STYLES} from './styles';
import {ReelProps, Storyboard} from './types';
import {catalog, validateStoryboard} from './validate';
import factSheet from '../examples/fact_sheet.json';
import cinematic from '../examples/cinematic_light.json';
import flat from '../examples/flat_jupiter.json';
import line from '../examples/line_orbits.json';

// The catalog and the code must list the same scenes and styles
const sameKeys = (a: object, b: object) => Object.keys(a).sort().join() === Object.keys(b).sort().join();
if (!sameKeys(catalog.scenes, SCENES) || !sameKeys(catalog.styles, STYLES)) {
	throw new Error('scene_catalog.json and the code list different scenes or styles');
}

// Runs before rendering: checks the storyboard, then works out the video's length
const calculateMetadata: CalculateMetadataFunction<ReelProps> = ({props}) => {
	validateStoryboard(props.storyboard, props.factSheet);
	const total = props.storyboard.scenes.reduce((sum, scene) => sum + toFrames(scene.seconds), 0);
	return {durationInFrames: total};
};

const EXAMPLES: [string, Storyboard][] = [
	['ExampleCinematic', cinematic as Storyboard],
	['ExampleFlat', flat as Storyboard],
	['ExampleLine', line as Storyboard],
];

const video = {fps: FPS, width: 1080, height: 1920, durationInFrames: 1, calculateMetadata};

export const RemotionRoot: React.FC = () => (
	<>
		<Composition id="Reel" component={Reel} defaultProps={{storyboard: flat as Storyboard, factSheet}} {...video} />
		{EXAMPLES.map(([id, storyboard]) => (
			<Composition key={id} id={id} component={Reel} defaultProps={{storyboard, factSheet}} {...video} />
		))}
	</>
);
