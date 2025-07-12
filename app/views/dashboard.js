// app/views/dashboard.js

export function DashboardView() {
  const el = document.createElement('section');
  el.innerHTML = `
    <h2>Welcome to MetaFlux</h2>
    <p>
      <b>MetaFlux</b> is an all-in-one web app for exploring, analyzing, and visualizing FDM 3D-printable metamaterial designs.<br>
      <ul>
        <li>Browse and search research papers</li>
        <li>View and download analyzed paper metadata</li>
        <li>Visualize 3D printable designs (STL) in-browser</li>
        <li>All logic and models are encapsulated in modern JavaScript</li>
        <li>No backend required – works on GitHub Pages!</li>
      </ul>
    </p>
    <p style="color:#888; font-size:0.9em;">(Dashboard features coming soon: paper list, design browser, 3D viewer, and more.)</p>
  `;
  return el;
} 