'use strict';
(() => {
  const byId = id => document.getElementById(id);
  const announce = text => { const el = byId('app-message'); if (el) el.textContent = text; };
  const post = async (url, body) => {
    const response = await fetch(url, {method: 'POST', headers: {'Content-Type': 'application/json'}, body});
    if (!response.ok) {
      const error = await response.json().catch(() => ({}));
      throw new Error(typeof error.detail === 'string' ? error.detail : 'Check the form values and try again.');
    }
    return response;
  };
  const theme = byId('theme-toggle');
  try { const saved = localStorage.getItem('studio-theme'); if (['light', 'dark'].includes(saved)) document.documentElement.dataset.theme = saved; } catch { /* Storage can be disabled. */ }
  theme?.addEventListener('click', () => {
    const current = document.documentElement.dataset.theme || (matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light');
    const next = current === 'dark' ? 'light' : 'dark';
    document.documentElement.dataset.theme = next;
    try { localStorage.setItem('studio-theme', next); } catch { /* Optional preference. */ }
    announce(`${next === 'dark' ? 'Dark' : 'Light'} theme selected.`);
  });
  const personas = Object.fromEntries([...document.querySelectorAll('#partner-names option')]
    .map(option => [option.value.toLowerCase(), option.dataset.id]));
  byId('partner-form')?.addEventListener('submit', event => {
    event.preventDefault();
    const name = byId('partner').value.trim().replace(/\s+/g, ' ').toLowerCase();
    const id = personas[name];
    if (id) location.assign(`/examples/${id}/base`);
    else byId('partner-error').textContent = 'Choose a name from the five fictional partners in the list, or open the pipeline.';
  });
  byId('import-file')?.addEventListener('change', async event => {
    const file = event.target.files?.[0]; if (!file) return;
    if (file.size > 512000) { announce('Choose a JSON file smaller than 500 KB.'); event.target.value = ''; return; }
    try {
      const text = await file.text(); JSON.parse(text);
      await post('/studio/import', text); location.assign('/studio?view=overview');
    } catch (error) { announce(error instanceof SyntaxError ? 'The file is not valid JSON.' : error.message); event.target.value = ''; }
  });
  byId('clear-session')?.addEventListener('click', async () => {
    try { await post('/session/clear'); location.assign('/'); } catch (error) { announce(error.message); }
  });
  const copy = async text => {
    try { await navigator.clipboard.writeText(text); announce('Copied to clipboard.'); }
    catch { announce('Clipboard access is unavailable. Select the text and copy it manually.'); }
  };
  document.querySelectorAll('.copy-text').forEach(button => button.addEventListener('click', () => copy(byId(button.dataset.target).innerText)));
  document.querySelectorAll('.copy-section').forEach(button => button.addEventListener('click', () => {
    const clone = byId(button.dataset.section).cloneNode(true);
    clone.querySelectorAll('button').forEach(el => el.remove());
    clone.querySelectorAll('details').forEach(el => el.open = true);
    copy(clone.textContent.replace(/\n{3,}/g, '\n\n').trim());
  }));
  document.addEventListener('keydown', event => {
    if (event.key === 'Escape') document.querySelectorAll('.evidence-chip').forEach(el => el.classList.add('tooltip-dismissed'));
  });
  document.querySelectorAll('.evidence-chip').forEach(el => {
    ['mouseleave', 'blur'].forEach(name => el.addEventListener(name, () => el.classList.remove('tooltip-dismissed')));
  });
  const contextDialog = byId('context-dialog');
  byId('open-context')?.addEventListener('click', () => contextDialog.showModal());
  byId('close-context')?.addEventListener('click', () => contextDialog.close());
  const print = brief => {
    document.body.classList.toggle('print-brief', brief);
    if (!brief) document.querySelectorAll('.studio-content details').forEach(el => {
      el.dataset.wasOpen = String(el.open); el.open = true;
    });
    window.print();
  };
  window.addEventListener('afterprint', () => {
    document.body.classList.remove('print-brief');
    document.querySelectorAll('details[data-was-open]').forEach(el => {
      el.open = el.dataset.wasOpen === 'true'; delete el.dataset.wasOpen;
    });
  });
  byId('print-studio')?.addEventListener('click', () => print(false));
  byId('print-brief')?.addEventListener('click', () => print(true));
  byId('section-picker')?.addEventListener('change', event => location.assign(event.target.value));
  document.querySelectorAll('.task-check').forEach(input => input.addEventListener('change', async () => {
    input.disabled = true;
    try {
      await post(`/partners/${input.dataset.partner}/tasks/${input.dataset.task}`, JSON.stringify({done:input.checked}));
      location.reload();
    } catch (error) { input.checked = !input.checked; input.disabled = false; announce(error.message); }
  }));
  const trackingDialog = byId('tracking-dialog');
  byId('open-tracking')?.addEventListener('click', () => trackingDialog.showModal());
  byId('close-tracking')?.addEventListener('click', () => trackingDialog.close());
  byId('tracking-form')?.addEventListener('submit', async event => {
    event.preventDefault();
    const form = event.currentTarget;
    const values = Object.fromEntries(new FormData(form));
    ['confirmed','touchpoints_completed','pilots_completed','independent_uses'].forEach(key => values[key] = Number(values[key]));
    const button = form.querySelector('[type=submit]'); button.disabled = true;
    try { await post(`/partners/${form.dataset.partner}/tracking`, JSON.stringify(values)); location.reload(); }
    catch (error) { byId('tracking-error').textContent = error.message; button.disabled = false; }
  });
  if (document.querySelector('.dashboard, .partner-workspace, .print-content')) {
  let lastActivity = Date.now(); let lastHeartbeat = Date.now(); let sending = false;
  const touch = () => { lastActivity = Date.now(); };
  ['pointerdown', 'keydown', 'input', 'scroll'].forEach(name => document.addEventListener(name, touch, {passive:true}));
  setInterval(async () => {
    if (lastActivity <= lastHeartbeat || Date.now()-lastActivity > 30*60*1000 || Date.now()-lastHeartbeat < 60000 || sending) return;
    sending = true;
    try { await post('/session/heartbeat'); lastHeartbeat = Date.now(); }
    catch { announce('The server session expired. Export requires an active session; reopen an example or import a saved file.'); }
    finally { sending = false; }
  }, 30000);
  }
  const sliders = [...document.querySelectorAll('.weight-slider')];
  if (!sliders.length) return;
  const defaults = {goal_fit:25, audience_fit:20, values_fit:20, time_to_first_value:10, feasibility:10, differentiation:10, risk_safety:5};
  let cases = null;
  let previous = [...document.querySelectorAll('.use-case')].map(el => el.dataset.caseId);
  const rank = () => {
    const weights = Object.fromEntries(sliders.map(el => [el.dataset.dimension, Number(el.value)]));
    sliders.forEach(el => byId(`output-${el.dataset.dimension}`).value = el.value);
    const total = Object.values(weights).reduce((a,b) => a+b, 0);
    if (!total) { byId('ranking-explanation').textContent = 'At least one weight must be above zero. The previous ranking is retained.'; return; }
    if (!cases) return;
    document.querySelectorAll('a[href^="/studio/export/"]').forEach(link => {
      const url = new URL(link.href); url.searchParams.set('weights', JSON.stringify(weights));
      link.href = url.pathname + url.search;
    });
    const scored = cases.map(c => ({...c, weighted: Object.entries(weights).reduce((sum,[key,value]) => sum + value * c.scores[key].score / 5, 0) * 100 / total}));
    scored.sort((a,b) => b.weighted-a.weighted || b.scores.risk_safety.score-a.scores.risk_safety.score || a.time_to_first_value_days-b.time_to_first_value_days || a.id.localeCompare(b.id));
    scored.forEach((c, index) => {
      const row = document.querySelector(`[data-case-id="${c.id}"]`);
      if (!row) return;
      row.querySelector('.rank').textContent = index+1;
      row.querySelector('.score-value').textContent = c.weighted.toFixed(1);
      byId('ranked-cases').append(row);
    });
    const changed = scored.filter((c,index) => previous.indexOf(c.id) !== index);
    const strongest = Object.keys(weights).sort((a,b) => weights[b]-weights[a] || a.localeCompare(b))[0];
    byId('ranking-explanation').textContent = changed.length
      ? `${scored[0].title} ranks first. ${changed.length} positions changed; ${strongest.replaceAll('_',' ')} has the highest weight (${weights[strongest]} of ${total}). All scores reflect the current weights. The demo plan is unchanged.`
      : `Order unchanged. Scores reflect current weights; ${strongest.replaceAll('_',' ')} has the highest weight (${weights[strongest]} of ${total}). Ties favor lower risk, then fewer days.`;
    previous = scored.map(c => c.id);
  };
  sliders.forEach(el => el.addEventListener('input', rank));
  const saveWeights = async () => {
    const weights = Object.fromEntries(sliders.map(el => [el.dataset.dimension, Number(el.value)]));
    if (!Object.values(weights).some(v => v > 0)) return;
    try { await post('/studio/weights', JSON.stringify({weights})); }
    catch (error) { announce(`Weights are shown locally but could not be saved: ${error.message}`); }
  };
  sliders.forEach(el => el.addEventListener('change', saveWeights));
  byId('reset-weights')?.addEventListener('click', () => { sliders.forEach(el => el.value = defaults[el.dataset.dimension]); rank(); saveWeights(); });
  fetch('/studio/data').then(response => { if (!response.ok) throw new Error('Session expired. Reopen an example or import your JSON.'); return response.json(); })
    .then(data => { cases = data.use_cases; rank(); })
    .catch(error => { sliders.forEach(el => el.disabled = true); announce(error.message); });

})();
