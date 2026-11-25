// The scene library. Each scene draws pictures only; the reel adds the
// style's text, the sound effects and the music on top.
// Adding a scene: write it in this folder, list it here, and describe it
// (style, length, parameters) in scene_catalog.json.

import React from 'react';
import {LightJourney} from './LightJourney';
import {OrbitClock} from './OrbitClock';
import {VolumeFill} from './VolumeFill';
import {SceneProps} from '../types';

export const SCENES: Record<string, React.FC<SceneProps>> = {
	light_journey: LightJourney,
	volume_fill: VolumeFill,
	orbit_clock: OrbitClock,
};
