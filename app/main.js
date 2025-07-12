// app/main.js

import { DashboardView } from './views/dashboard.js';
// Future: import { PapersView } from './views/papers.js';
// Future: import { DesignsView } from './views/designs.js';
// Future: import { AboutView } from './views/about.js';

const appRoot = document.getElementById('app-root');

function render(view) {
  appRoot.innerHTML = '';
  appRoot.appendChild(view);
}

function showDashboard() {
  render(DashboardView());
}

// Placeholder for future navigation
function showPapers() {
  appRoot.innerHTML = '<h2>Papers</h2><p>Coming soon...</p>';
}
function showDesigns() {
  appRoot.innerHTML = '<h2>Designs</h2><p>Coming soon...</p>';
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