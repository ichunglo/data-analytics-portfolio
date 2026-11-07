(() => {
  const data = window.LANDSCAPE_DATA;
  const $ = (id) => document.getElementById(id);
  const number = (n) => n.toLocaleString('en-US');
  $('target-total').textContent = number(data.manifest.target_count);
  $('drug-total').textContent = number(data.manifest.drug_count);
  $('link-total').textContent = number(data.manifest.relationship_count);
  $('top-total').textContent = number(data.targets.length);
  const category = $('category');
  [...new Set(data.targets.map((r) => r.target_category || 'Unclear'))].sort().forEach((name) => {
    const option = document.createElement('option'); option.value = name; option.textContent = name; category.appendChild(option);
  });
  const cell = (row, text, className = '') => { const td = document.createElement('td'); td.textContent = text; td.className = className; row.appendChild(td); return td; };
  function render() {
    const query = $('search').value.trim().toLowerCase();
    const filtered = data.targets.filter((r) => (!category.value || (r.target_category || 'Unclear') === category.value) && [r.gene_symbol, r.target_name].some((s) => s.toLowerCase().includes(query)));
    const label = (r) => r.gene_symbol || r.target_name;
    const mode = $('sort').value;
    filtered.sort((a, b) => (mode === 'name' ? label(a).localeCompare(label(b)) : mode === 'approved' ? b.reported_approved - a.reported_approved || b.linked_drugs - a.linked_drugs : b.linked_drugs - a.linked_drugs) || label(a).localeCompare(label(b)));
    $('rows').replaceChildren();
    const max = Math.max(1, ...filtered.map((r) => r.linked_drugs));
    filtered.forEach((r) => {
      const row = document.createElement('tr'); const target = cell(row, label(r)); target.title = r.target_name;
      cell(row, r.target_category || 'Unclear'); const barCell = cell(row, '');
      const bar = document.createElement('div'); bar.className = 'bar'; bar.setAttribute('aria-label', `${r.linked_drugs} linked drugs, ${r.reported_approved} with approval reported`);
      const total = document.createElement('div'); total.className = 'bar-total'; total.style.width = `${100 * r.linked_drugs / max}%`;
      const approved = document.createElement('div'); approved.className = 'bar-approved'; approved.style.width = `${100 * r.reported_approved / max}%`;
      bar.append(total, approved); barCell.appendChild(bar); cell(row, number(r.linked_drugs), 'num'); cell(row, number(r.reported_approved), 'num'); $('rows').appendChild(row);
    });
    $('result-count').textContent = `Showing ${filtered.length} of ${data.targets.length} top-ranked targets`;
    $('empty').hidden = filtered.length > 0;
  }
  ['search', 'category', 'sort'].forEach((id) => $(id).addEventListener(id === 'search' ? 'input' : 'change', render));
  render();
})();
