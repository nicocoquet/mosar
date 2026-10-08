const REVUES_TRANSLATIONS = {
  fr: {
    locale: 'fr',
    values: {},
    unknownLabel: 'Non renseigné',
    facetsTitle: 'Filtrer la recherche',
    resetLabel: 'Réinitialiser les filtres',
    selectedFiltersLabel: 'Filtres sélectionnés',
    searchPlaceholder: 'Rechercher une revue, un ISSN, un éditeur…',
    searchAriaLabel: 'Rechercher',
    emptyLabel: 'Aucune revue ne correspond aux filtres sélectionnés.',
    resultsLabel: (count, total) =>
      `${count} revue${count > 1 ? 's' : ''} sur ${total}`,
    levelLabel: number => `Niveau ${number}`,
    formatTitle: 'Format de publication',
    diamondTitle: 'Labellisation : Diamond journal',
    ddhTitle: 'Voir la revue dans le Diamond Discovery Hub',
    mirabelTitle: 'Voir la revue dans Mir@bel',
    websiteTitle: 'Site web de la revue',
    websiteLabel: 'Site web',
    loadError: 'Impossible de charger les données',
    configError: 'Configuration de l’explorateur introuvable.',
    facets: [
      {key: 'proximity', label: 'Niveau de proximité'},
      {key: 'access', label: 'Accès'},
      {key: 'format', label: 'Format de publication'},
      {key: 'periodicity', label: 'Périodicité'},
      {key: 'themes', label: 'Thématiques'},
      {key: 'languages', label: 'Langues'},
      {key: 'publishers', label: 'Éditeur'}
    ],
    languages: {
      fre:'Français', fra:'Français', eng:'Anglais',
      deu:'Allemand', ger:'Allemand', ita:'Italien',
      spa:'Espagnol', por:'Portugais', dut:'Néerlandais',
      nld:'Néerlandais', cat:'Catalan', pol:'Polonais',
      rus:'Russe', ara:'Arabe', gre:'Grec moderne',
      ell:'Grec moderne', lat:'Latin', tur:'Turc',
      rum:'Roumain', ron:'Roumain', hun:'Hongrois',
      cze:'Tchèque', ces:'Tchèque', slo:'Slovaque',
      slk:'Slovaque', hrv:'Croate', srp:'Serbe',
      slv:'Slovène', bul:'Bulgare', ukr:'Ukrainien',
      heb:'Hébreu', jpn:'Japonais', chi:'Chinois',
      zho:'Chinois'
    }
  },

  en: {
    locale: 'en',
    values: {
      'Accès ouvert': 'Open access',
      'Accès restreint': 'Restricted access',
      'Papier et numérique': 'Print and online',
      'Papier': 'Print',
      'Numérique': 'Online',
      'annuel': 'Annual',
      'irrégulier': 'Irregular',
      'semestriel': 'Twice yearly',
      'trimestriel': 'Quarterly',
      'bimestriel': 'Every two months',
      'mensuel': 'Monthly',
      'quadrimestriel': 'Every four months',
      'bisannuel': 'Every two years',
      'triannuel': 'Every three years',
      '5 numéros par an': 'Five issues per year',
      'hebdomadaire': 'Weekly',
      'bimensuel': 'Twice monthly',
      'tri-hebdomadaire': 'Three times a week'
    },
    unknownLabel: 'Not specified',
    facetsTitle: 'Filter journals',
    resetLabel: 'Reset filters',
    selectedFiltersLabel: 'Selected filters',
    searchPlaceholder: 'Search for a journal, ISSN, publisher…',
    searchAriaLabel: 'Search',
    emptyLabel: 'No journals match the selected filters.',
    resultsLabel: (count, total) =>
      `${count} journal${count !== 1 ? 's' : ''} out of ${total}`,
    levelLabel: number => `Level ${number}`,
    formatTitle: 'Publication format',
    diamondTitle: 'Label: Diamond journal',
    ddhTitle: 'View journal in the Diamond Discovery Hub',
    mirabelTitle: 'View journal on Mir@bel',
    websiteTitle: 'Journal website',
    websiteLabel: 'Website',
    loadError: 'Unable to load data',
    configError: 'Explorer configuration not found.',
    facets: [
      {key: 'proximity', label: 'Level of proximity'},
      {key: 'access', label: 'Access'},
      {key: 'format', label: 'Publication format'},
      {key: 'periodicity', label: 'Publication frequency'},
      {key: 'themes', label: 'Topics'},
      {key: 'languages', label: 'Languages'},
      {key: 'publishers', label: 'Publisher'}
    ],
    languages: {
      fre:'French', fra:'French', eng:'English',
      deu:'German', ger:'German', ita:'Italian',
      spa:'Spanish', por:'Portuguese', dut:'Dutch',
      nld:'Dutch', cat:'Catalan', pol:'Polish',
      rus:'Russian', ara:'Arabic', gre:'Modern Greek',
      ell:'Modern Greek', lat:'Latin', tur:'Turkish',
      rum:'Romanian', ron:'Romanian', hun:'Hungarian',
      cze:'Czech', ces:'Czech', slo:'Slovak',
      slk:'Slovak', hrv:'Croatian', srp:'Serbian',
      slv:'Slovenian', bul:'Bulgarian', ukr:'Ukrainian',
      heb:'Hebrew', jpn:'Japanese', chi:'Chinese',
      zho:'Chinese'
    }
  }
};

const explorerLanguage =
  document.getElementById('revues-explorer')?.getAttribute('lang') === 'en'
    ? 'en'
    : 'fr';

window.MOSAR_REVUES_CONFIG = {
  ...REVUES_TRANSLATIONS[explorerLanguage],
  facetScrollThreshold: 8
};