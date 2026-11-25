// The style "skins". A style decides how text looks and moves, and can add
// an overlay over the whole picture. Scenes decide what is drawn.
// Adding a style: write its Text (and Overlay if needed) and list it here
// and in scene_catalog.json.

import React from 'react';
import {Beat} from '../types';
import {CinematicOverlay, CinematicText} from './cinematic';
import {FlatText} from './flat';
import {LineText} from './line';

export type Style = {
	Text: React.FC<{beat: Beat}>;
	Overlay?: React.FC;
};

export const STYLES: Record<string, Style> = {
	cinematic: {Text: CinematicText, Overlay: CinematicOverlay},
	flat: {Text: FlatText},
	line: {Text: LineText},
};
