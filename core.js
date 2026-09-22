(function (root) {
  'use strict';
  const normalize = value => String(value || '').normalize('NFD').replace(/[\u0300-\u036f]/g, '').toLocaleLowerCase('pt-BR');
  function query(records, filters = {}) {
    const terms = normalize(filters.q).split(/\s+/).filter(Boolean);
    const result = records.filter(r =>
      (!filters.ano || r.date.slice(0, 4) === filters.ano) &&
      (!filters.mes || r.date.slice(5, 7) === filters.mes) &&
      (!filters.preletor || r.preacher === filters.preletor) &&
      (!filters.serie || normalize(r.series) === normalize(filters.serie)) &&
      (!filters.estacao || r.season === filters.estacao) &&
      terms.every(t => normalize([r.title, r.series, r.preacher, r.celebration, r.season, r.originalText].join(' ')).includes(t))
    );
    result.sort((a, b) => {
      if (filters.ordem === 'oldest') return a.date.localeCompare(b.date) || a.id.localeCompare(b.id);
      if (filters.ordem === 'published') {
        const publication = (b.publishedAt || '').localeCompare(a.publishedAt || '');
        if (publication) return publication;
      }
      return b.date.localeCompare(a.date) || a.id.localeCompare(b.id);
    });
    return result;
  }
  const api = { normalize, query };
  if (typeof module !== 'undefined' && module.exports) module.exports = api;
  else root.SermonsCore = api;
})(typeof globalThis !== 'undefined' ? globalThis : this);
