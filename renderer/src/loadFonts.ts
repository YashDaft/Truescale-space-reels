// Loads the font files from public/fonts before any frame is drawn.
// delayRender() tells Remotion to wait until continueRender() is called.

import {continueRender, delayRender, staticFile} from 'remotion';

const FONT_FILES = [
	{family: 'Inter', weight: '300', file: 'fonts/inter-latin-300-normal.woff2'}, // line style
	{family: 'Inter', weight: '500', file: 'fonts/inter-latin-500-normal.woff2'}, // line style labels
	{family: 'Fredoka', weight: '600', file: 'fonts/fredoka-latin-600-normal.woff2'}, // flat style
	{family: 'Cormorant Garamond', weight: '500', file: 'fonts/cormorant-garamond-latin-500-normal.woff2'}, // cinematic style
];

const waitForFonts = delayRender('Loading fonts');

Promise.all(
	FONT_FILES.map(({family, weight, file}) => {
		const font = new FontFace(family, `url(${staticFile(file)}) format('woff2')`, {weight});
		return font.load().then(() => document.fonts.add(font));
	}),
).then(() => continueRender(waitForFonts));
