// The shapes of the data the renderer receives.
// The Python pipeline writes these as JSON; examples/ has one of each.

// --- Fact sheet ---

export type Fact = {
	value: number;
	source?: string; // link to the official source, for facts copied from one
	level?: string; // e.g. "measured data"
	formula?: string; // for facts worked out by code from other facts
};

export type FactSheet = {
	facts: Record<string, Fact>;
	// Ready-to-show text for numbers that appear on screen, e.g. "8 minutes 19 seconds"
	display: Record<string, string>;
};

// --- Storyboard ---

// A line of on-screen text, shown from `at` to `until` seconds within its scene
export type Beat = {at: number; until: number; text: string; subtext?: string};

// A sound effect played `at` seconds into its scene
export type Sound = {at: number; file: string; volume?: number};

export type SceneSpec = {
	scene: string; // must be a scene in scene_catalog.json
	seconds: number;
	params?: Record<string, string | string[]>;
	beats?: Beat[];
	sounds?: Sound[];
};

export type Storyboard = {
	title: string;
	style: string; // must be a style in scene_catalog.json
	music: string;
	music_volume: number;
	scenes: SceneSpec[];
};

// What every scene receives: its parameters from the storyboard,
// already checked against scene_catalog.json
export type SceneProps = {params: Record<string, string | string[]>};

// What every video receives
export type ReelProps = {storyboard: Storyboard; factSheet: FactSheet};

// --- Scene catalog (scene_catalog.json) ---

export type ParamSpec = {
	// fact: a key in the fact sheet's facts
	// display_fact: a key in both facts and display (its value is shown on screen)
	// text: free text, no digits allowed
	// choice: one of `allowed`
	// list: several of `allowed`
	type: 'fact' | 'display_fact' | 'text' | 'choice' | 'list';
	required: boolean;
	description: string;
	allowed?: string[];
	// For lists: facts each item needs, with {item} replaced by the item, e.g. "{item}_period_days"
	requires_facts?: string[];
	// For choices: the value must also be one of the items in this other list param
	one_of_param?: string;
};

export type CatalogScene = {
	style: string;
	description: string;
	min_seconds: number;
	max_seconds: number;
	requires_facts: string[];
	params: Record<string, ParamSpec>;
};

export type Catalog = {
	styles: Record<string, {description: string; music: string[]}>;
	sounds: string[];
	scenes: Record<string, CatalogScene>;
};
