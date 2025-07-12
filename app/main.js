// app/main.js

import { DashboardView } from './views/dashboard.js';
import { PapersView } from './views/papers.js';
import { DesignsView } from './views/designs.js';
// Future: import { AboutView } from './views/about.js';

const appRoot = document.getElementById('app-root');

function render(view) {
  appRoot.innerHTML = '';
  appRoot.appendChild(view);
}

function showDashboard() {
  render(DashboardView());
}
function showPapers() {
  render(PapersView());
}
function showDesigns() {
  render(DesignsView());
}
function showAbout() {
  appRoot.innerHTML = '<h2>About MetaFlux</h2><p>Automated FDM 3D-Printable Metamaterial Design Pipeline.</p>';
}

document.getElementById('nav-dashboard').onclick = showDashboard;
document.getElementById('nav-papers').onclick = showPapers;
document.getElementById('nav-designs').onclick = showDesigns;
document.getElementById('nav-about').onclick = showAbout;

// Initial view
showDashboard(); 