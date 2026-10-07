#!/usr/bin/env node
/**
 * Contrôle léger de l'explorateur Revues.
 *
 * Objectif : détecter avant déploiement les erreurs JavaScript qui
 * n'apparaissent qu'au rendu ou lors d'une interaction avec les facettes.
 * Aucun navigateur ni dépendance npm n'est nécessaire.
 */

const fs = require('fs');
const vm = require('vm');

const scriptPath = 'docs/assets/javascripts/revues-exploration.js';
const source = fs.readFileSync(scriptPath, 'utf8');

new vm.Script(source, { filename: scriptPath });

const requiredPatterns = [
  ['lecture du modèle publié', /data\.model\?\.proximity_levels\|\|\[\]/],
  ['propagation vers les facettes', /buildFacets\(records,\s*proximityLevels\)/],
  ['signature des facettes', /function buildFacets\(records,\s*proximityLevels\)/],
  ['propagation vers le rendu', /render\(records,\s*proximityLevels\)/],
  ['signature du rendu', /function render\(records,\s*proximityLevels\)/],
  ['propagation vers le tri', /sortRecords\(filtered\(records\),\s*proximityLevels\)/],
  ['signature du tri', /function sortRecords\(rows,\s*proximityLevels\)/],
  ['interaction de facette', /addEventListener\('change',[\s\S]*?render\(records,\s*proximityLevels\)/],
  ['interaction de recherche', /addEventListener\('input',[\s\S]*?render\(records,\s*proximityLevels\)/],
  ['interaction de réinitialisation', /rx-reset[\s\S]*?addEventListener\('click',[\s\S]*?render\(records,\s*proximityLevels\)/],
];

const failures = requiredPatterns
  .filter(([, pattern]) => !pattern.test(source))
  .map(([label]) => label);

if (failures.length) {
  console.error('Échec du contrôle JavaScript Revues :');
  failures.forEach(label => console.error(`- ${label}`));
  process.exit(1);
}

console.log('OK — syntaxe et propagation des interactions Revues contrôlées.');
