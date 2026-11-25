// Gives every scene access to the fact sheet.
// Numbers on screen come from here and nowhere else.

import React, {createContext, useContext} from 'react';
import {FactSheet} from './types';

const FactsContext = createContext<FactSheet | null>(null);

export const FactsProvider: React.FC<{factSheet: FactSheet; children: React.ReactNode}> = ({factSheet, children}) => (
	<FactsContext.Provider value={factSheet}>{children}</FactsContext.Provider>
);

export const useFacts = () => {
	const factSheet = useContext(FactsContext);
	if (!factSheet) {
		throw new Error('useFacts() was used outside FactsProvider');
	}

	// A fact's number, for drawing (sizes, distances, speeds)
	const value = (key: string): number => {
		if (!(key in factSheet.facts)) throw new Error(`"${key}" is not in the fact sheet`);
		return factSheet.facts[key].value;
	};

	// Text with {placeholders} split into parts, marking which parts came from
	// the fact sheet so the style can show them in its accent colour.
	// validateStoryboard() has already checked every placeholder exists.
	const parts = (template: string): {text: string; isFact: boolean}[] =>
		template
			.split(/(\{[a-z0-9_]+\})/)
			.filter((part) => part !== '')
			.map((part) => {
				const match = part.match(/^\{([a-z0-9_]+)\}$/);
				return match ? {text: factSheet.display[match[1]], isFact: true} : {text: part, isFact: false};
			});

	// The same text as one plain string
	const text = (template: string): string =>
		parts(template)
			.map((p) => p.text)
			.join('');

	return {value, parts, text, display: factSheet.display};
};
