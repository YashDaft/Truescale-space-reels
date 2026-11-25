// Checks a storyboard against the scene catalog and the fact sheet before
// anything is drawn. It collects every problem it finds, so one failed
// render lists all of them, not just the first.

import catalogJson from '../scene_catalog.json';
import {Catalog, FactSheet, Storyboard} from './types';

export const catalog = catalogJson as Catalog;

const PLACEHOLDER = /\{([a-z0-9_]+)\}/g;

// Text may only contain numbers through {placeholders} that are in the fact sheet's display
const checkText = (text: string, where: string, factSheet: FactSheet, errors: string[]) => {
	const withoutPlaceholders = text.replace(PLACEHOLDER, '');
	if (/\d/.test(withoutPlaceholders)) {
		errors.push(`${where}: number typed directly into "${text}". Use a fact-sheet placeholder.`);
	}
	for (const match of text.matchAll(PLACEHOLDER)) {
		if (!(match[1] in factSheet.display)) {
			errors.push(`${where}: "{${match[1]}}" is not in the fact sheet's display`);
		}
	}
};

export const validateStoryboard = (storyboard: Storyboard, factSheet: FactSheet): void => {
	const errors: string[] = [];
	const hasFact = (key: string) => key in factSheet.facts;

	const style = catalog.styles[storyboard.style];
	if (!style) {
		errors.push(`Unknown style "${storyboard.style}"`);
	} else if (!style.music.includes(storyboard.music)) {
		errors.push(`Music "${storyboard.music}" is not listed for the ${storyboard.style} style`);
	}
	if (storyboard.scenes.length === 0) {
		errors.push('The storyboard has no scenes');
	}

	storyboard.scenes.forEach((spec, i) => {
		const where = `Scene ${i + 1} (${spec.scene})`;
		const scene = catalog.scenes[spec.scene];
		if (!scene) {
			errors.push(`${where}: not in the scene catalog`);
			return;
		}
		if (scene.style !== storyboard.style) {
			errors.push(`${where}: belongs to the ${scene.style} style, but this reel is ${storyboard.style}`);
		}
		if (spec.seconds < scene.min_seconds || spec.seconds > scene.max_seconds) {
			errors.push(`${where}: ${spec.seconds} s is outside ${scene.min_seconds}-${scene.max_seconds} s`);
		}
		for (const key of scene.requires_facts) {
			if (!hasFact(key)) errors.push(`${where}: needs the fact "${key}"`);
		}

		// Parameters
		const params = spec.params ?? {};
		for (const name of Object.keys(params)) {
			if (!(name in scene.params)) errors.push(`${where}: unknown parameter "${name}"`);
		}
		for (const [name, rule] of Object.entries(scene.params)) {
			const value = params[name];
			if (value === undefined) {
				if (rule.required) errors.push(`${where}: missing parameter "${name}"`);
				continue;
			}
			const label = `${where}, parameter "${name}"`;

			if (rule.type === 'list') {
				if (!Array.isArray(value) || value.length === 0) {
					errors.push(`${label}: must be a non-empty list`);
					continue;
				}
				for (const item of value) {
					if (rule.allowed && !rule.allowed.includes(item)) errors.push(`${label}: "${item}" is not allowed`);
					for (const template of rule.requires_facts ?? []) {
						const key = template.replace('{item}', item);
						if (!hasFact(key)) errors.push(`${label}: needs the fact "${key}"`);
					}
				}
				continue;
			}

			if (typeof value !== 'string') {
				errors.push(`${label}: must be text, not a list`);
				continue;
			}
			if (rule.type === 'fact' && !hasFact(value)) {
				errors.push(`${label}: "${value}" is not in the fact sheet`);
			}
			if (rule.type === 'display_fact' && (!hasFact(value) || !(value in factSheet.display))) {
				errors.push(`${label}: "${value}" must be in both the facts and the display`);
			}
			if (rule.type === 'text') {
				checkText(value, label, factSheet, errors);
			}
			if (rule.type === 'choice') {
				if (rule.allowed && !rule.allowed.includes(value)) errors.push(`${label}: "${value}" is not allowed`);
				const other = rule.one_of_param ? params[rule.one_of_param] : undefined;
				if (rule.one_of_param && !(Array.isArray(other) && other.includes(value))) {
					errors.push(`${label}: "${value}" must also be in "${rule.one_of_param}"`);
				}
			}
		}

		// Text beats
		(spec.beats ?? []).forEach((beat, b) => {
			const label = `${where}, text ${b + 1}`;
			if (beat.at < 0 || beat.until <= beat.at || beat.until > spec.seconds) {
				errors.push(`${label}: times ${beat.at}-${beat.until} s don't fit in the ${spec.seconds} s scene`);
			}
			checkText(beat.text, label, factSheet, errors);
			if (beat.subtext) checkText(beat.subtext, `${label} (small line)`, factSheet, errors);
		});

		// Sound effects
		(spec.sounds ?? []).forEach((sound, s) => {
			const label = `${where}, sound ${s + 1}`;
			if (!catalog.sounds.includes(sound.file)) errors.push(`${label}: "${sound.file}" is not in the catalog`);
			if (sound.at < 0 || sound.at >= spec.seconds) errors.push(`${label}: starts outside the scene`);
		});
	});

	if (errors.length > 0) {
		throw new Error(`The storyboard has ${errors.length} problem(s):\n- ${errors.join('\n- ')}`);
	}
};
