
'use strict';

const fs = require('node:fs');
const path = require('node:path');
const vm = require('node:vm');

const ROOT = path.resolve(__dirname, '..');

const configPath = path.join(
  ROOT,
  'docs/assets/javascripts/revues-config.js'
);

const dataPath = path.join(
  ROOT,
  'docs/assets/data/revues-exploration.json'
);

// Charger la configuration anglaise dans un contexte isolé.
const sandbox = {
  window: {},
  document: {
    getElementById: () => ({
      getAttribute: () => 'en'
    })
  }
};

vm.runInNewContext(
  fs.readFileSync(configPath, 'utf8'),
  sandbox,
  { filename: configPath }
);

const translations = sandbox.window.MOSAR_REVUES_CONFIG?.values;

if (!translations || typeof translations !== 'object') {
  console.error('ERREUR — dictionnaire anglais introuvable.');
  process.exit(1);
}

const records = JSON.parse(
  fs.readFileSync(dataPath, 'utf8')
).records;

if (!Array.isArray(records)) {
  console.error('ERREUR — liste des revues introuvable.');
  process.exit(1);
}

const fields = {
  'Thématiques': r => r.themes || [],
  'Accès': r => [r.mosar?.open_access],
  'Formats': r => [r.publication_format],
  'Périodicités': r => [r.periodicity]
};

let errors = 0;

for (const [label, getter] of Object.entries(fields)) {
  const values = [...new Set(
    records.flatMap(getter).filter(
      value => typeof value === 'string' && value.trim()
    )
  )].sort((a, b) => a.localeCompare(b, 'fr'));

  const missing = values.filter(
    value =>
      !Object.hasOwn(translations, value) ||
      typeof translations[value] !== 'string' ||
      !translations[value].trim()
  );

  console.log(
    `${label} : ${values.length} valeurs, ` +
    `${missing.length} traduction(s) manquante(s)`
  );

  for (const value of missing) {
    console.error(`  - ${JSON.stringify(value)}`);
  }

  errors += missing.length;
}

if (errors) {
  console.error(
    `\nÉCHEC — ${errors} traduction(s) à compléter.`
  );
  process.exit(1);
}

console.log('\nOK — couverture des traductions anglaises complète.');