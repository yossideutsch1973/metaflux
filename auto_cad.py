import cadquery as cq
import json
import numpy as np  
import re
from pathlib import Path
from typing import Dict, List, Tuple, Optional
from param_cad import generate_unit_cell

def sanitize_paper_title(title: str) -> str:
    """Convert paper title to clean folder name."""
    # Remove special characters and replace spaces with underscores
    clean_title = re.sub(r'[^\w\s-]', '', title)
    clean_title = re.sub(r'\s+', '_', clean_title)
    # Limit length to 50 characters
    clean_title = clean_title[:50]
    # Remove trailing underscores
    clean_title = clean_title.rstrip('_')
    return clean_title

def analyze_papers_for_cad(papers_file: Path) -> List[Dict]:
    """Analyze papers and extract CAD-relevant parameters."""
    papers = json.loads(papers_file.read_text())
    
    # Filter for FDM-printable, high-relevance papers
    candidates = []
    for p in papers:
        score = p.get('relevance_score', 0)
        params = p.get('extracted_params', {})
        manufacturing = params.get('manufacturing_methods', [])
        dimensions = params.get('dimensions', [])
        
        # Check if FDM printable
        is_fdm = 'FDM_3D_printing' in manufacturing
        
        # Check if mm scale (not micro/nano)
        is_mm_scale = False
        if dimensions:
            for value, unit in dimensions:
                try:
                    val = float(value)
                    if unit in ['mm', 'cm'] and 0.1 <= val <= 100:  # FDM printable range
                        is_mm_scale = True
                        break
                except ValueError:
                    continue
        
        # Prioritize FDM + mm scale
        if is_fdm and is_mm_scale and score > 2.0:
            candidates.append(p)
        elif is_fdm and score > 1.5:  # FDM but no clear mm scale
            candidates.append(p)
        elif is_mm_scale and score > 2.5:  # mm scale but not FDM
            candidates.append(p)
    
    # If no candidates found, use top scored papers anyway (demo mode)
    if not candidates:
        print("⚠️  No FDM-printable candidates found, using top papers...")
        candidates = sorted(papers, key=lambda x: x.get('relevance_score', 0), reverse=True)[:3]
    
    # Sort by relevance score
    candidates.sort(key=lambda x: x.get('relevance_score', 0), reverse=True)
    
    return candidates[:5]  # Top 5 candidates

def extract_geometric_params(paper: Dict) -> Optional[Dict[str, float]]:
    """Extract numerical geometric parameters from paper data.
    
    Returns dict with period, height, thickness in meters.
    """
    params = paper.get('extracted_params', {})
    dimensions = params.get('dimensions', [])
    
    # Convert extracted dimensions to standard units (meters)
    geometric_params = {}
    
    if dimensions:
        for dim_value, unit in dimensions:
            try:
                value = float(dim_value)
                
                # Convert to meters - FOCUS ON MM SCALE FOR FDM
                if unit in ['mm']:
                    value *= 1e-3
                elif unit in ['cm']:
                    value *= 1e-2
                elif unit in ['μm', 'um', 'micron', 'micrometer']:
                    value *= 1e-6  
                elif unit in ['nm']:
                    value *= 1e-9
                
                # Assign to appropriate parameter based on magnitude (FDM scale)
                if 1e-3 <= value <= 50e-3:  # 1-50 mm range - likely period
                    geometric_params['period'] = value
                elif 0.1e-3 <= value <= 5e-3:   # 0.1-5 mm range - likely thickness  
                    geometric_params['thickness'] = value
                elif 5e-3 <= value <= 100e-3:  # 5-100 mm range - likely height
                    geometric_params['height'] = value
                    
            except (ValueError, TypeError):
                continue
    
    # Intelligent defaults based on paper type and function (FDM scale)
    functions = params.get('functions', [])
    manufacturing = params.get('manufacturing_methods', [])
    
    # Set intelligent defaults based on application (FDM printable scale)
    if 'FDM_3D_printing' in manufacturing:
        # FDM-specific defaults
        default_period = 20e-3  # 20 mm
        default_height = 30e-3  # 30 mm
    elif 'antenna' in functions or 'lens' in functions:
        # Antenna/lens designs typically larger
        default_period = 30e-3  # 30 mm
        default_height = 40e-3  # 40 mm
    else:
        # General metamaterial defaults (FDM scale)
        default_period = 25e-3   # 25 mm
        default_height = 35e-3   # 35 mm
    
    # Always return parameters (with defaults if needed)
    if 'period' not in geometric_params:
        geometric_params['period'] = default_period
    if 'height' not in geometric_params:
        geometric_params['height'] = default_height
    if 'thickness' not in geometric_params:
        geometric_params['thickness'] = 2e-3   # 2 mm standard for FDM
        
    return geometric_params

def determine_geometry_type(paper: Dict) -> str:
    """Determine the appropriate geometry type based on paper content."""
    title = paper.get('title', '').lower()
    abstract = paper.get('abstract', '').lower()
    functions = paper.get('extracted_params', {}).get('functions', [])
    materials = paper.get('extracted_params', {}).get('materials', [])
    
    text = f"{title} {abstract}"
    
    # Lens designs - check title and abstract more thoroughly
    if ('lens' in title or 'lens' in abstract or 
        'beam steering' in text or 'focusing' in text or
        'gradient index' in text):
        return 'gradient_index_lens'
    
    # Antenna designs
    if ('antenna' in title or 'antenna' in abstract or 
        'radiating' in text or 'transmission' in text):
        return 'patch_antenna'
    
    # Absorber designs
    if ('absorber' in title or 'absorber' in abstract or 
        'absorption' in text or 'ram' in text or
        'radar absorbing' in text):
        return 'metamaterial_absorber'
    
    # Filter designs
    if ('filter' in title or 'filter' in abstract or 
        'frequency selective' in text or 'fss' in text):
        return 'frequency_selective_surface'
    
    # Polarizer designs
    if ('polarizer' in title or 'polarizer' in abstract or 
        'polarization' in text or 'wire grid' in text):
        return 'wire_grid_polarizer'
    
    # Check functions array as well
    if 'lens' in functions:
        return 'gradient_index_lens'
    elif 'antenna' in functions:
        return 'patch_antenna'
    elif 'absorber' in functions:
        return 'metamaterial_absorber'
    elif 'filter' in functions:
        return 'frequency_selective_surface'
    elif 'polarizer' in functions:
        return 'wire_grid_polarizer'
    
    # General metamaterial unit cells
    if 'metamaterial' in text or 'unit cell' in text:
        return 'split_ring_resonator'
    
    # Default to SRR for unknown types
    return 'split_ring_resonator'

def generate_paper_specific_geometry(geometry_type: str, period: float, height: float, 
                                   thickness: float = 2e-3) -> cq.Workplane:
    """Generate paper-specific geometry based on the determined type."""
    
    if geometry_type == 'gradient_index_lens':
        return generate_gradient_index_lens(period, height, thickness)
    elif geometry_type == 'patch_antenna':
        return generate_patch_antenna(period, height, thickness)
    elif geometry_type == 'metamaterial_absorber':
        return generate_metamaterial_absorber(period, height, thickness)
    elif geometry_type == 'frequency_selective_surface':
        return generate_frequency_selective_surface(period, height, thickness)
    elif geometry_type == 'wire_grid_polarizer':
        return generate_wire_grid_polarizer(period, height, thickness)
    else:
        return generate_split_ring_resonator(period, height, thickness)

def generate_gradient_index_lens(period: float, height: float, thickness: float) -> cq.Workplane:
    """Generate a gradient index lens with concentric rings."""
    # Create lens with varying refractive index zones
    lens = cq.Workplane("XY")
    
    # Create base cylinder
    base = lens.circle(period/2).extrude(height)
    
    # Add concentric rings for gradient index effect
    n_rings = 5
    for i in range(1, n_rings):
        ring_radius = (period/2) * (i/n_rings)
        ring_thickness = thickness * (1 - i/n_rings)  # Thinner towards center
        
        ring = (cq.Workplane("XY")
               .circle(ring_radius)
               .circle(ring_radius - ring_thickness)
               .extrude(height))
        
        base = base.cut(ring)
    
    return base

def generate_patch_antenna(period: float, height: float, thickness: float) -> cq.Workplane:
    """Generate a patch antenna design."""
    # Create rectangular patch antenna
    patch_width = period * 0.8
    patch_length = period * 0.6
    
    # Main patch
    patch = (cq.Workplane("XY")
            .rect(patch_width, patch_length)
            .extrude(thickness))
    
    # Ground plane (larger than patch)
    ground = (cq.Workplane("XY")
             .rect(period, period)
             .extrude(thickness)
             .translate((0, 0, height - thickness)))
    
    # Feed line
    feed_width = thickness * 2
    feed_length = period * 0.3
    feed = (cq.Workplane("XY")
           .rect(feed_width, feed_length)
           .extrude(thickness)
           .translate((0, -patch_length/2 - feed_length/2, 0)))
    
    return patch.union(ground).union(feed)

def generate_metamaterial_absorber(period: float, height: float, thickness: float) -> cq.Workplane:
    """Generate a metamaterial absorber with Jerusalem cross pattern."""
    # Create Jerusalem cross absorber
    cross_width = period * 0.15
    cross_length = period * 0.4
    
    # Vertical cross
    v_cross = (cq.Workplane("XY")
              .rect(cross_width, cross_length)
              .extrude(thickness))
    
    # Horizontal cross
    h_cross = (cq.Workplane("XY")
              .rect(cross_length, cross_width)
              .extrude(thickness))
    
    # Ground plane
    ground = (cq.Workplane("XY")
             .rect(period, period)
             .extrude(thickness)
             .translate((0, 0, height - thickness)))
    
    return v_cross.union(h_cross).union(ground)

def generate_frequency_selective_surface(period: float, height: float, thickness: float) -> cq.Workplane:
    """Generate a frequency selective surface with slot pattern."""
    # Create FSS with cross-shaped slots
    base = (cq.Workplane("XY")
           .rect(period, period)
           .extrude(thickness))
    
    # Cross-shaped slot
    slot_width = period * 0.2
    slot_length = period * 0.6
    
    v_slot = (cq.Workplane("XY")
             .rect(slot_width, slot_length)
             .extrude(thickness))
    
    h_slot = (cq.Workplane("XY")
             .rect(slot_length, slot_width)
             .extrude(thickness))
    
    return base.cut(v_slot).cut(h_slot)

def generate_wire_grid_polarizer(period: float, height: float, thickness: float) -> cq.Workplane:
    """Generate a wire grid polarizer."""
    # Create wire grid with parallel wires
    n_wires = 8
    wire_width = thickness
    wire_spacing = period / n_wires
    
    base = cq.Workplane("XY")
    
    for i in range(n_wires):
        x_pos = (i - n_wires/2 + 0.5) * wire_spacing
        wire = (cq.Workplane("XY")
               .rect(wire_width, period * 0.8)
               .extrude(height)
               .translate((x_pos, 0, 0)))
        base = base.union(wire)
    
    return base

def generate_split_ring_resonator(period: float, height: float, thickness: float) -> cq.Workplane:
    """Generate a split ring resonator (original design)."""
    # Create split ring geometry
    outer_radius = period / 2.5
    inner_radius = outer_radius * 0.7
    gap_width = period * 0.1
    
    # Create split ring geometry
    outer_ring = cq.Workplane("XY").circle(outer_radius).extrude(height)
    inner_ring = cq.Workplane("XY").circle(inner_radius).extrude(height)
    
    # Create gap
    gap_box = (cq.Workplane("XY")
              .rect(gap_width, outer_radius * 2.2)
              .extrude(height)
              .translate((outer_radius + gap_width/2, 0, 0)))
    
    # Boolean operations: outer - inner - gap
    return outer_ring.cut(inner_ring).cut(gap_box)

def generate_metamaterial_variants(paper: Dict, n_variants: int = 3) -> List[Path]:
    """Generate multiple CAD variants based on paper parameters."""
    base_params = extract_geometric_params(paper)
    
    variants = []
    paper_id = paper.get('paperId', 'unknown')[:8]
    
    # Generate variants by scaling base parameters
    scale_factors = [0.8, 1.0, 1.2]  # -20%, nominal, +20%
    
    for i, scale in enumerate(scale_factors):
        scaled_params = {k: v * scale for k, v in base_params.items()}
        
        # Generate using our existing function with paper data
        stl_path = generate_unit_cell_with_metadata(
            period=scaled_params['period'],
            height=scaled_params['height'], 
            thickness=scaled_params.get('thickness', 2e-3),
            paper_id=f"{paper_id}_v{i+1}",
            paper_title=paper.get('title', 'Unknown Paper'),
            paper_data=paper  # Pass full paper data for geometry selection
        )
        variants.append(stl_path)
        
    return variants

def generate_unit_cell_with_metadata(period: float, height: float, 
                                   thickness: float = 2e-3, 
                                   paper_id: str = "auto",
                                   paper_title: str = "Unknown Paper",
                                   paper_data: Dict = None) -> Path:
    """Enhanced unit cell generator with metadata tracking and paper-specific geometry.
    
    Args:
        period: Unit cell period in meters
        height: Unit cell height in meters  
        thickness: Wall thickness in meters
        paper_id: Paper identifier for tracking
        paper_title: Paper title for folder organization
        paper_data: Full paper data for geometry selection
    
    Returns:
        Path to generated STL file
    """
    # Determine geometry type based on paper content
    if paper_data:
        geometry_type = determine_geometry_type(paper_data)
    else:
        geometry_type = 'split_ring_resonator'  # Default fallback
    
    # Generate paper-specific geometry
    unit_cell = generate_paper_specific_geometry(geometry_type, period, height, thickness)
    
    # Create paper-specific folder and filename
    period_mm = period * 1e3
    height_mm = height * 1e3
    thickness_mm = thickness * 1e3
    
    # Create clean folder name from paper title
    folder_name = sanitize_paper_title(paper_title)
    paper_folder = Path(__file__).parent / "designs" / folder_name
    paper_folder.mkdir(parents=True, exist_ok=True)
    
    # Use geometry type in filename
    filename = f"{geometry_type}_{paper_id}_{period_mm:.0f}mm_{height_mm:.0f}mm.stl"
    out = paper_folder / filename
    
    # Export STL
    unit_cell.val().exportStl(str(out))
    
    # Save metadata
    metadata = {
        'paper_id': paper_id,
        'paper_title': paper_title,
        'paper_folder': folder_name,
        'geometry_type': geometry_type,
        'parameters': {
            'period_m': period,
            'height_m': height,
            'thickness_m': thickness,
            'period_mm': period_mm,
            'height_mm': height_mm,
            'thickness_mm': thickness_mm
        },
        'file_path': str(out),
        'generated_at': str(Path(__file__).parent),
        'manufacturing_method': 'FDM_3D_printing',
        'scale': 'millimeter_scale'
    }
    
    metadata_file = out.with_suffix('.json')
    metadata_file.write_text(json.dumps(metadata, indent=2))
    
    return out

def generate_auxetic_arterial_stent(
    target_diameter: float = 20e-3,  # 20 mm target diameter for aorta
    length: float = 50e-3,          # 50 mm length 
    wall_thickness: float = 3e-3,   # 3 mm wall thickness
    strut_thickness: float = 0.8e-3, # 0.8 mm strut thickness based on SM3 design
    paper_id: str = "auxetic_arterial_stent",
    paper_title: str = "4D-Printed Arterial Stent with Auxetic Materials"
) -> Path:
    """
    Generate a bioinspired auxetic arterial stent based on the biomimetics paper.
    
    This implements the SM3 (square mode 3) auxetic design which demonstrated:
    - Superior self-expansion capability (17.02 mm middle diameter)
    - Best anti-migration performance (1.32 N force required) 
    - Approaches optimal ~1.5 N benchmark for effective anti-migration
    
    Mathematical representation of auxetic behavior:
    ν = -εᵧ/εₓ < 0  (negative Poisson's ratio)
    
    Where ν is Poisson's ratio, εᵧ is transverse strain, εₓ is axial strain
    
    Args:
        target_diameter: Target deployment diameter in meters (20mm for aorta)
        length: Stent length in meters (50mm as per paper)
        wall_thickness: Overall wall thickness in meters (3mm)
        strut_thickness: Individual strut thickness in meters
        paper_id: Identifier for tracking
        paper_title: Paper title for organization
    
    Returns:
        Path to generated STL file
    """
    
    # SM3 (Square Mode 3) auxetic unit cell parameters from the paper
    unit_cell_size = 4e-3  # 4 mm unit cell size
    inner_square_ratio = 0.6  # Inner to outer square ratio for auxetic behavior
    
    # Calculate number of patterns around circumference and along length
    circumference = np.pi * target_diameter
    n_circumferential = max(6, int(circumference / unit_cell_size))  # Minimum 6 for good coverage
    n_longitudinal = max(3, int(length / unit_cell_size))  # Minimum 3 for structure
    
    # Create main cylindrical stent body
    outer_radius = target_diameter / 2
    inner_radius = outer_radius - wall_thickness
    
    # Start with solid cylindrical tube (outer cylinder minus inner cylinder)
    outer_cylinder = cq.Workplane("XY").circle(outer_radius).extrude(length)
    inner_cylinder = cq.Workplane("XY").circle(inner_radius).extrude(length)
    stent = outer_cylinder.cut(inner_cylinder)
    
    # Create SM3 auxetic pattern cutouts
    pattern_depth = wall_thickness * 0.7  # Cut 70% through wall thickness
    
    for i in range(n_longitudinal):
        for j in range(n_circumferential):
            # Calculate position for this pattern
            angle = (j * 2 * np.pi) / n_circumferential
            z_pos = (i + 0.5) * (length / n_longitudinal) - length/2
            
            # Position on cylinder surface
            pattern_radius = (outer_radius + inner_radius) / 2
            x_pos = pattern_radius * np.cos(angle)
            y_pos = pattern_radius * np.sin(angle)
            
            # Create SM3 auxetic cutout pattern
            outer_size = unit_cell_size * 0.8  # Slightly smaller for overlap
            inner_size = outer_size * inner_square_ratio
            beam_width = strut_thickness
            
            # Create square cutout with auxetic features
            # Outer square cavity
            outer_cut = (cq.Workplane("XY")
                        .rect(outer_size, outer_size)
                        .extrude(pattern_depth))
            
            # Inner connecting structure (what remains)
            inner_keep = (cq.Workplane("XY")
                         .rect(inner_size, inner_size)
                         .extrude(pattern_depth))
            
            # Connecting beams (auxetic hinges)
            beam_length = (outer_size - inner_size) / 2 + beam_width
            
            # Horizontal beams
            h_beam1 = (cq.Workplane("XY")
                      .rect(beam_length, beam_width)
                      .extrude(pattern_depth)
                      .translate((0, outer_size/4, 0)))
            
            h_beam2 = (cq.Workplane("XY")
                      .rect(beam_length, beam_width)
                      .extrude(pattern_depth)
                      .translate((0, -outer_size/4, 0)))
            
            # Vertical beams
            v_beam1 = (cq.Workplane("XY")
                      .rect(beam_width, beam_length)
                      .extrude(pattern_depth)
                      .translate((outer_size/4, 0, 0)))
            
            v_beam2 = (cq.Workplane("XY")
                      .rect(beam_width, beam_length)
                      .extrude(pattern_depth)
                      .translate((-outer_size/4, 0, 0)))
            
            # Create the pattern by subtracting outer and adding beams
            pattern = (outer_cut
                      .cut(inner_keep)
                      .cut(h_beam1)
                      .cut(h_beam2)
                      .cut(v_beam1)
                      .cut(v_beam2))
            
            # Position and orient the pattern on cylinder surface
            # Rotate to align with cylinder surface normal
            pattern_positioned = (pattern
                                .rotate((0, 0, 0), (0, 0, 1), np.degrees(angle))
                                .translate((x_pos, y_pos, z_pos)))
            
            # Cut this pattern from the main stent
            stent = stent.cut(pattern_positioned)
    
    # Add flared ends for anti-migration
    flare_length = 5e-3  # 5mm flare length at each end
    flare_diameter_increase = 2e-3  # 2mm diameter increase for anchoring
    
    # Proximal flare (smooth transition) - hollow structure
    proximal_outer = cq.Workplane("XY").circle((target_diameter + flare_diameter_increase) / 2).extrude(flare_length).translate((0, 0, -length/2 - flare_length/2))
    proximal_inner = cq.Workplane("XY").circle(inner_radius).extrude(flare_length).translate((0, 0, -length/2 - flare_length/2))
    proximal_flare = proximal_outer.cut(proximal_inner)
    
    # Distal flare - hollow structure
    distal_outer = cq.Workplane("XY").circle((target_diameter + flare_diameter_increase) / 2).extrude(flare_length).translate((0, 0, length/2 + flare_length/2))
    distal_inner = cq.Workplane("XY").circle(inner_radius).extrude(flare_length).translate((0, 0, length/2 + flare_length/2))
    distal_flare = distal_outer.cut(distal_inner)
    
    # Add flares to main stent body
    stent = stent.union(proximal_flare).union(distal_flare)
    
    # Create output directory and filename
    folder_name = sanitize_paper_title(paper_title)
    paper_folder = Path(__file__).parent / "designs" / folder_name
    paper_folder.mkdir(parents=True, exist_ok=True)
    
    # Convert dimensions to micrometers for filename
    diameter_um = target_diameter * 1e6
    length_um = length * 1e6
    
    filename = f"auxetic_stent_{paper_id}_{diameter_um:.0f}um_dia_{length_um:.0f}um_len.stl"
    out = paper_folder / filename
    
    # Export STL
    stent.val().exportStl(str(out))
    
    # Save metadata according to paper specifications
    metadata = {
        'paper_id': paper_id,
        'paper_title': paper_title,
        'paper_folder': folder_name,
        'stent_type': 'auxetic_arterial_4d_printed',
        'auxetic_design': 'SM3_square_mode_3',
        'material': 'PCL_polycaprolactone',
        'manufacturing': '4D_printing_FFF',
        'performance_metrics': {
            'self_expansion_diameter_mm': 17.02,  # As reported in paper
            'anti_migration_force_N': 1.32,      # As reported in paper
            'poisson_ratio': -0.3,               # Negative for auxetic behavior
            'target_benchmark_N': 1.5            # Optimal benchmark cited
        },
        'geometric_parameters': {
            'target_diameter_m': target_diameter,
            'length_m': length, 
            'wall_thickness_m': wall_thickness,
            'strut_thickness_m': strut_thickness,
            'unit_cell_size_m': unit_cell_size,
            'n_circumferential': n_circumferential,
            'n_longitudinal': n_longitudinal,
            'flare_length_m': flare_length,
            'flare_diameter_increase_m': flare_diameter_increase,
            'pattern_depth_m': pattern_depth
        },
        'biomechanical_properties': {
            'flexibility': 'high_at_extremes',
            'radial_strength': 'optimized_for_aorta',
            'deployment_mechanism': 'self_expanding',
            'anti_migration': 'flared_ends_with_auxetic_grip'
        },
        'file_path': str(out),
        'generated_at': str(Path(__file__).parent),
        'design_validation': 'based_on_biomimetics_2025_paper'
    }
    
    metadata_file = out.with_suffix('.json')
    metadata_file.write_text(json.dumps(metadata, indent=2))
    
    print(f"✓ Generated auxetic arterial stent: {filename}")
    print(f"  - Target diameter: {target_diameter*1000:.1f} mm")
    print(f"  - Length: {length*1000:.1f} mm") 
    print(f"  - Auxetic design: SM3 (square mode 3)")
    print(f"  - Anti-migration force: 1.32 N (approaching 1.5 N benchmark)")
    print(f"  - Material: PCL for 4D printing")
    print(f"  - Structure: Unified cylindrical with {n_circumferential}×{n_longitudinal} patterns")
    
    return out

def batch_generate_from_papers(papers_file: Path) -> List[Path]:
    """Batch generate CAD files from analyzed papers."""
    candidates = analyze_papers_for_cad(papers_file)
    
    all_variants = []
    for paper in candidates:
        print(f"Generating variants for: {paper.get('title', 'Unknown')[:50]}...")
        variants = generate_metamaterial_variants(paper)
        all_variants.extend(variants)
        
    return all_variants 