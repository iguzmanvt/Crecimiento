(function () {
'use strict';
var control = document.getElementById('search-control');
var input = document.getElementById('course-search');
var clear = document.getElementById('clear-search');
var status = document.getElementById('search-status');
var items = Array.prototype.slice.call(document.querySelectorAll('.searchable'));
function normalize(value) { return value.normalize('NFD').replace(/[\u0300-\u036f]/g, '').toLowerCase().replace(/\binnovation\b/g, 'innovacion').trim(); }
function update() {
  var query = normalize(input.value);
  var taskMatch = query.match(/\btarea\s*(\d+)(?:\s*,?\s*variante(?:\s+tematica)?)?/);
  var taskId = taskMatch ? 'T' + taskMatch[1] + (taskMatch[0].indexOf('variante') !== -1 ? '_variante' : '') : '';
  var rest = taskMatch ? query.replace(taskMatch[0], '') : query;
  var terms = rest.split(/\s+/).filter(Boolean);
  var counts = {tema: 0, tarea: 0};
  items.forEach(function (item) {
    var content = normalize(item.dataset.search || '');
    var taskIds = (item.dataset.taskIds || '').split(/\s+/);
    var matchesTask = !taskId || taskIds.some(function (id) { return id === taskId || id.indexOf(taskId + '_') === 0; });
    var matches = matchesTask && terms.every(function (term) { return content.indexOf(term) !== -1; });
    item.hidden = !matches;
    if (matches) counts[item.dataset.kind] += 1;
    var details = item.querySelector('details');
    if (details) details.open = Boolean(query) && matches;
    if (item.dataset.kind === 'tema') {
      var nav = document.querySelector('[data-topic-link="' + item.id.replace('tema-', '') + '"]');
      if (nav) nav.hidden = !matches;
    }
  });
  clear.hidden = !input.value;
  document.getElementById('no-topics').hidden = counts.tema > 0;
  document.getElementById('no-tasks').hidden = counts.tarea > 0;
  status.textContent = counts.tema + (counts.tema === 1 ? ' tema' : ' temas') + ' y ' + counts.tarea + (counts.tarea === 1 ? ' enunciado' : ' enunciados') + (query ? ' que coinciden.' : ' disponibles.');
}
control.hidden = false;
input.addEventListener('input', update);
clear.addEventListener('click', function () { input.value = ''; update(); input.focus(); });
update();
}());
