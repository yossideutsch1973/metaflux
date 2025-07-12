// app/main.js

import { DashboardView } from './views/dashboard.js';
import { PapersView } from './views/papers.js';
import { DesignsView } from './views/designs.js';
// Future: import { AboutView } from './views/about.js';

const appRoot = document.getElementById('app-root');
const consoleDiv = document.getElementById('console');

export function log(msg) {
  if (!consoleDiv) return;
  const line = document.createElement('div');
  line.textContent = `[${new Date().toLocaleTimeString()}] ${msg}`;
  consoleDiv.appendChild(line);
  // Keep only last 10 messages
  while (consoleDiv.children.length > 10) consoleDiv.removeChild(consoleDiv.firstChild);
}

function render(view) {
  appRoot.innerHTML = '';
  appRoot.appendChild(view);
}

function showDashboard() {
  log('Navigating to Dashboard');
  render(DashboardView());
}
function showPapers() {
  log('Navigating to Papers');
  render(PapersView());
}
function showDesigns() {
  log('Navigating to Designs');
  render(DesignsView());
}
function showAbout() {
  log('Navigating to About');
  appRoot.innerHTML = '<h2>About MetaFlux</h2><p>Automated FDM 3D-Printable Metamaterial Design Pipeline.</p>';
}

document.getElementById('nav-dashboard').onclick = showDashboard;
document.getElementById('nav-papers').onclick = showPapers;
document.getElementById('nav-designs').onclick = showDesigns;
document.getElementById('nav-about').onclick = showAbout;

// Initial view
log('App loaded');
showDashboard(); 