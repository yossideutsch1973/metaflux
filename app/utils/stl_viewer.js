// app/utils/stl_viewer.js
// Usage: STLViewer.render(div, stlUrl)

export const STLViewer = {
  render: function(container, stlUrl) {
    // Clear previous content
    container.innerHTML = '';
    // Set up scene
    const width = container.offsetWidth || 400;
    const height = container.offsetHeight || 300;
    const scene = new THREE.Scene();
    const camera = new THREE.PerspectiveCamera(45, width/height, 0.1, 1000);
    camera.position.set(0, 0, 80);
    const renderer = new THREE.WebGLRenderer({antialias:true, alpha:true});
    renderer.setClearColor(0xf7f7fa, 1);
    renderer.setSize(width, height);
    container.appendChild(renderer.domElement);

    // Add light
    const light = new THREE.DirectionalLight(0xffffff, 1);
    light.position.set(0, 0, 100);
    scene.add(light);
    scene.add(new THREE.AmbientLight(0xffffff, 0.7));

    // Controls
    let controls;
    if (THREE.OrbitControls) {
      controls = new THREE.OrbitControls(camera, renderer.domElement);
    }

    // Load STL
    const loader = new THREE.STLLoader();
    loader.load(stlUrl, function(geometry) {
      const material = new THREE.MeshPhongMaterial({ color: 0x6699cc, specular: 0x111111, shininess: 100 });
      const mesh = new THREE.Mesh(geometry, material);
      geometry.computeBoundingBox();
      const center = geometry.boundingBox.getCenter(new THREE.Vector3());
      mesh.position.sub(center); // Center the mesh
      scene.add(mesh);
      animate();
    }, undefined, function(err) {
      container.innerHTML = '<div style="color:red;">Failed to load STL</div>';
    });

    function animate() {
      requestAnimationFrame(animate);
      renderer.render(scene, camera);
      if (controls) controls.update();
    }
  }
}; 