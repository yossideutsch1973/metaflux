import cadquery as cq
from pathlib import Path

def generate_unit_cell(period: float = 80e-6, height: float = 150e-6, paper_title: str = "Manual_Generation") -> Path:
    """Generate basic unit cell with folder organization."""
    import re
    
    # Create clean folder name
    clean_title = re.sub(r'[^\w\s-]', '', paper_title)
    clean_title = re.sub(r'\s+', '_', clean_title)
    clean_title = clean_title[:50].rstrip('_')
    
    # Create paper-specific folder
    paper_folder = Path(__file__).parent / "designs" / clean_title
    paper_folder.mkdir(parents=True, exist_ok=True)
    
    # Create unit cell geometry
    unit_cell = cq.Workplane("XY").box(period, period, height, centered=(True, True, False))
    
    # Ensure we have a valid solid before exporting
    if unit_cell.val() is not None:
        out = paper_folder / f"cell_{period*1e6:.0f}um.stl"
        unit_cell.val().exportStl(str(out))
        return out
    else:
        raise ValueError("Failed to create valid unit cell geometry")