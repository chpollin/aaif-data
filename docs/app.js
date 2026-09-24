// Renders docs/data/profiles.json, written by 04_export.py, as one stacked bar per corpus.
// The state lives in the URL hash (#category/scope), so every view can be linked.

const PALETTE = ['#0072B2', '#E69F00', '#009E73', '#CC79A7', '#56B4E9', '#D55E00', '#F0E442', '#882255', '#999933'];
// A yes/no category reads as one quantity, so its "no" side stays pale.
const BINARY = ['#0072B2', '#b7d0e1'];
const SPECIAL = {
  _unmapped: { label: 'Code without meaning in the manual', color: '#6b6b6b' },
  _none: { label: 'Not annotated', color: '#d9d9d9' },
};
const SCOPES = {
  all: 'all adverbs',
  outside: 'adverbs outside a prepositional phrase',
  inside: 'adverbs inside a prepositional phrase',
};

const numberFormat = new Intl.NumberFormat('en');
let data;

function percent(count, total) {
  const value = (100 * count) / total;
  if (value < 0.1) return '<0.1%';
  return (value < 10 ? value.toFixed(1) : value.toFixed(0)) + '%';
}

function textColor(hex) {
  const [r, g, b] = [1, 3, 5].map((i) => parseInt(hex.slice(i, i + 2), 16) / 255);
  return 0.2126 * r + 0.7152 * g + 0.0722 * b > 0.5 ? '#1a1a1a' : '#ffffff';
}

function element(tag, attributes = {}, text) {
  const node = document.createElement(tag);
  for (const [key, value] of Object.entries(attributes)) node.setAttribute(key, value);
  if (text !== undefined) node.textContent = text;
  return node;
}

function readState() {
  const [category, scope] = location.hash.slice(1).split('/');
  return {
    category: data.categories.some((c) => c.key === category) ? category : 'target',
    scope: scope in SCOPES ? scope : 'all',
  };
}

function valuesOf(category) {
  const colors = category.values.length === 2 ? BINARY : PALETTE;
  const values = category.values.map((v, i) => ({ key: v.key, label: v.label, color: colors[i] }));
  for (const [key, special] of Object.entries(SPECIAL)) values.push({ key, ...special });
  return values;
}

function isUndeclared(corpus, categoryKey, valueKey) {
  const declared = corpus.declared && corpus.declared[categoryKey];
  return Array.isArray(declared) && !valueKey.startsWith('_') && !declared.includes(valueKey);
}

// The declaration is shown only where it explains a gap, naming the excluded values that
// corpora of at least two languages show in the same view. Language-specific values such
// as the Romanian suffixes would otherwise be listed for every other corpus.
function declarationNote(corpus, category, shared) {
  if (!corpus.declared) return 'The header declares no annotated categories.';
  const declared = corpus.declared[category.key];
  if (!declared) return 'The header does not declare this category.';
  const excluded = category.values.filter((v) => shared.has(v.key) && !declared.includes(v.key));
  if (!excluded.length) return null;
  return 'Not declared in the header: ' + excluded.map((v) => v.label).join(', ') + '.';
}

function showTooltip(event, text) {
  const tooltip = document.getElementById('tooltip');
  tooltip.textContent = text;
  tooltip.hidden = false;
  const rect = event.target.getBoundingClientRect();
  const left = Math.min(rect.left, window.innerWidth - tooltip.offsetWidth - 8);
  tooltip.style.left = Math.max(8, left) + 'px';
  tooltip.style.top = rect.bottom + 6 + 'px';
}

function hideTooltip() {
  document.getElementById('tooltip').hidden = true;
}

function renderRow(corpus, category, scope, values, shared) {
  const counts = corpus.counts[category.key][scope];
  const total = Object.values(counts).reduce((a, b) => a + b, 0);
  const row = element('li', { class: 'row' });

  const label = element('div', { class: 'corpus' });
  const link = element('a', { href: corpus.url, title: corpus.title }, corpus.abbreviation);
  label.append(link, element('span', { class: 'language' }, corpus.language));
  row.append(label);

  const bar = element('div', { class: 'bar' });
  if (total === 0) {
    const ppUnknown = scope !== 'all' && corpus.counts.pp.all._none;
    bar.append(element('span', { class: 'empty' }, ppUnknown ? 'Prepositional phrase not annotated' : 'No adverbs in this selection'));
  }
  for (const value of values) {
    const count = counts[value.key];
    if (!count) continue;
    const undeclared = isUndeclared(corpus, category.key, value.key);
    const share = percent(count, total);
    const description = `${corpus.abbreviation}, ${value.label}: ${numberFormat.format(count)} of ${numberFormat.format(total)} (${share})` +
      (undeclared ? ', not declared in the header' : '');
    const segment = element('span', {
      class: 'segment' + (undeclared ? ' undeclared' : ''),
      tabindex: '0',
      'aria-label': description,
    });
    segment.style.width = (100 * count) / total + '%';
    segment.style.backgroundColor = value.color;
    segment.style.color = textColor(value.color);
    if (value.key === '_none' && count === total) segment.textContent = value.label;
    else if (count / total >= 0.07) segment.textContent = share;
    segment.addEventListener('mouseenter', (e) => showTooltip(e, description));
    segment.addEventListener('focus', (e) => showTooltip(e, description));
    segment.addEventListener('mouseleave', hideTooltip);
    segment.addEventListener('blur', hideTooltip);
    bar.append(segment);
  }
  row.append(bar, element('span', { class: 'n' }, total ? 'n = ' + numberFormat.format(total) : ''));

  const note = declarationNote(corpus, category, shared);
  if (note && total) row.append(element('p', { class: 'note' }, note));
  return row;
}

function renderTable(category, scope, values) {
  const table = document.getElementById('counts');
  table.replaceChildren();
  const head = element('thead');
  const headRow = element('tr');
  headRow.append(element('th', { scope: 'col' }, 'Corpus'));
  for (const value of values) headRow.append(element('th', { scope: 'col' }, value.label));
  headRow.append(element('th', { scope: 'col' }, 'Total'));
  head.append(headRow);

  const body = element('tbody');
  for (const corpus of data.corpora) {
    const counts = corpus.counts[category.key][scope];
    const total = Object.values(counts).reduce((a, b) => a + b, 0);
    const row = element('tr');
    row.append(element('th', { scope: 'row' }, `${corpus.abbreviation} (${corpus.language})`));
    for (const value of values) {
      const count = counts[value.key] || 0;
      const cell = element('td', isUndeclared(corpus, category.key, value.key) && count ? { class: 'undeclared' } : {});
      cell.textContent = numberFormat.format(count);
      if (count) cell.append(' ', element('span', { class: 'pct' }, percent(count, total)));
      row.append(cell);
    }
    row.append(element('td', {}, numberFormat.format(total)));
    body.append(row);
  }
  table.append(head, body);
}

function render() {
  const { category: categoryKey, scope } = readState();
  const category = data.categories.find((c) => c.key === categoryKey);
  for (const input of document.querySelectorAll('#controls input')) {
    input.checked = input.value === (input.name === 'scope' ? scope : categoryKey);
  }

  const attested = new Set();
  const languages = new Map();
  let anyUndeclared = false;
  for (const corpus of data.corpora) {
    for (const [key, count] of Object.entries(corpus.counts[categoryKey][scope])) {
      if (!count) continue;
      attested.add(key);
      languages.set(key, (languages.get(key) || new Set()).add(corpus.language));
      if (isUndeclared(corpus, categoryKey, key)) anyUndeclared = true;
    }
  }
  const values = valuesOf(category).filter((v) => attested.has(v.key));
  const shared = new Set([...languages].filter(([, set]) => set.size > 1).map(([key]) => key));

  document.getElementById('profile-title').textContent = `${category.label}, ${SCOPES[scope]}`;
  document.getElementById('table-title').textContent = `Counts: ${category.label}, ${SCOPES[scope]}`;

  const legend = document.getElementById('legend');
  legend.replaceChildren();
  for (const value of values) {
    const item = element('li');
    const swatch = element('span', { class: 'swatch', 'aria-hidden': 'true' });
    swatch.style.backgroundColor = value.color;
    item.append(swatch, value.label);
    legend.append(item);
  }
  if (anyUndeclared) {
    const item = element('li');
    const swatch = element('span', { class: 'swatch segment undeclared', 'aria-hidden': 'true' });
    swatch.style.backgroundColor = '#ffffff';
    item.append(swatch, 'Value not declared in the corpus header');
    legend.append(item);
  }

  const rows = document.getElementById('rows');
  rows.replaceChildren(...data.corpora.map((c) => renderRow(c, category, scope, values, shared)));
  renderTable(category, scope, values);
}

function buildControls() {
  const options = document.getElementById('category-options');
  for (const category of data.categories) {
    const label = element('label');
    label.append(element('input', { type: 'radio', name: 'category', value: category.key }), element('span', {}, category.label));
    options.append(label);
  }
  for (const label of document.querySelectorAll('#controls label')) {
    const input = label.querySelector('input');
    if (!label.querySelector('span')) {
      const text = label.textContent.trim();
      label.textContent = '';
      label.append(input, element('span', {}, text));
    }
  }
  document.getElementById('controls').addEventListener('change', () => {
    const form = new FormData(document.getElementById('controls'));
    location.hash = `${form.get('category')}/${form.get('scope')}`;
  });
  window.addEventListener('hashchange', render);
}

async function init() {
  try {
    const response = await fetch('data/profiles.json');
    if (!response.ok) throw new Error(`HTTP ${response.status}`);
    data = await response.json();
  } catch (error) {
    document.getElementById('rows').replaceChildren(element('li', { class: 'note' }, `The counts could not be loaded (${error.message}).`));
    return;
  }
  document.getElementById('retrieved').textContent = data.retrieved;
  buildControls();
  render();
}

init();
