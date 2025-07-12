// app/views/papers.js
import { Paper } from '../models/paper.js';

export function PapersView() {
  const el = document.createElement('section');
  el.innerHTML = `<h2>Papers</h2><div id="papers-list">Loading...</div>`;
  const list = el.querySelector('#papers-list');

  fetch('data/papers.json')
    .then(r => r.json())
    .then(data => {
      if (!Array.isArray(data) || data.length === 0) {
        list.innerHTML = '<p>No papers found.</p>';
        return;
      }
      list.innerHTML = '';
      data.forEach(d => {
        const paper = new Paper(d);
        const item = document.createElement('div');
        item.className = 'paper-item';
        item.innerHTML = `
          <b>${paper.title}</b> ${paper.displayYear} ${paper.displayScore}<br>
          <span style="color:#666;">${paper.displayAuthors}</span>
          ${paper.pdfLink ? `<a href="${paper.pdfLink}" target="_blank" style="margin-left:1em;">[PDF]</a>` : ''}
        `;
        item.onclick = () => showPaperDetail(paper);
        list.appendChild(item);
      });
    })
    .catch(() => {
      list.innerHTML = '<p style="color:red;">Failed to load papers.json</p>';
    });

  function showPaperDetail(paper) {
    list.innerHTML = `
      <button id="back-to-list">&larr; Back</button>
      <h3>${paper.title}</h3>
      <div><b>Authors:</b> ${paper.displayAuthors}</div>
      <div><b>Year:</b> ${paper.year}</div>
      <div><b>Venue:</b> ${paper.venue}</div>
      <div><b>Score:</b> ${paper.displayScore}</div>
      <div><b>PDF:</b> ${paper.pdfLink ? `<a href="${paper.pdfLink}" target="_blank">Download/View</a>` : 'N/A'}</div>
      <div><b>Extracted Params:</b><pre style="background:#f4f4f4; padding:0.5em;">${JSON.stringify(paper.extracted, null, 2)}</pre></div>
    `;
    list.querySelector('#back-to-list').onclick = () => {
      el.replaceWith(PapersView());
    };
  }

  return el;
} 