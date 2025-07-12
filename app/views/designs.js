// app/views/designs.js
import { Design } from '../models/design.js';
import { log } from '../main.js';
import { STLViewer } from '../utils/stl_viewer.js';

export function DesignsView() {
  const el = document.createElement('section');
  el.innerHTML = `<h2>Designs</h2><div id="designs-list">Loading...</div>`;
  const list = el.querySelector('#designs-list');

  async function loadDesigns() {
    log('Loading design metadata from known folders...');
    const folders = [
      'A_3D-Printed_Metallic-Free_Water-Based_Metamateria',
      'Tunable_3D_printed_composite_metamaterials_with_ne',
      'Additively_Manufactured_Mechanical_MetamaterialBas'
    ];
    let files = [];
    for (const folder of folders) {
      for (let v = 1; v <= 3; ++v) {
        const types = ['patch_antenna', 'metamaterial_absorber', 'split_ring_resonator'];
        for (const type of types) {
          for (let p of [16, 20, 24, 28, 35, 42]) {
            for (let h of [24, 30, 36, 28, 35, 42]) {
              const f = `designs/${folder}/${type}_${folder.slice(0,8)}_v${v}_${p}mm_${h}mm.json`;
              try {
                log('Trying to fetch: ' + f);
                // eslint-disable-next-line no-await-in-loop
                const resp = await fetch(f);
                if (resp.ok) {
                  const data = await resp.json();
                  files.push(new Design(data, f));
                  log('Loaded design: ' + f);
                }
              } catch (e) {
                log('Error fetching ' + f + ': ' + e);
              }
            }
          }
        }
      }
    }
    log(`Total designs loaded: ${files.length}`);
    return files;
  }

  loadDesigns().then(designs => {
    if (!designs.length) {
      log('No designs found.');
      list.innerHTML = '<p>No designs found.</p>';
      return;
    }
    log(`Rendering ${designs.length} designs.`);
    list.innerHTML = '';
    designs.forEach(design => {
      const item = document.createElement('div');
      item.className = 'design-item';
      item.innerHTML = `
        <b>${design.displayTitle}</b> <span style="color:#888;">(${design.displayGeometry})</span><br>
        <span style="color:#666;">${design.filePath}</span>
      `;
      item.onclick = () => showDesignDetail(design);
      list.appendChild(item);
    });
  });

  function showDesignDetail(design) {
    log('Showing details for design: ' + design.displayTitle);
    const stlPath = design.filePath.replace(/\.json$/, '.stl');
    list.innerHTML = `
      <button id="back-to-list">&larr; Back</button>
      <h3>${design.displayTitle}</h3>
      <div><b>Geometry:</b> ${design.displayGeometry}</div>
      <div><b>File:</b> ${design.filePath}</div>
      <div><b>Parameters:</b><pre style="background:#f4f4f4; padding:0.5em;">${JSON.stringify(design.parameters, null, 2)}</pre></div>
      <button id="view-stl-btn">View STL</button>
      <div id="stl-viewer" style="width:400px; height:300px; margin-top:1em;"></div>
    `;
    list.querySelector('#back-to-list').onclick = () => {
      el.replaceWith(DesignsView());
    };
    list.querySelector('#view-stl-btn').onclick = () => {
      log('Loading STL: ' + stlPath);
      STLViewer.render(list.querySelector('#stl-viewer'), stlPath);
    };
  }

  return el;
} 