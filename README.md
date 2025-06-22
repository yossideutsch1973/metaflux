# MetaFlux: Automated FDM 3D-Printable Metamaterial Design Pipeline

A comprehensive automated pipeline for researching, analyzing, and generating FDM 3D-printable metamaterial designs from scientific literature.

## 🎯 Overview

MetaFlux is an intelligent system that:
- **Researches** recent metamaterial papers from Semantic Scholar
- **Downloads** PDF copies of relevant papers
- **Analyzes** papers for FDM-printable parameters (mm scale)
- **Generates** paper-specific CAD geometries (STL files)
- **Creates** multiple design variants with metadata

## ✨ Key Features

### 🔬 **Smart Literature Analysis**
- Fetches papers from Semantic Scholar API
- Downloads PDF copies automatically
- Extracts geometric parameters (mm scale)
- Identifies FDM manufacturing methods
- Scores papers for FDM printability

### 🏗️ **Paper-Specific CAD Generation**
- **6 Different Geometry Types**:
  - `gradient_index_lens` - Lens designs with concentric rings
  - `patch_antenna` - Antenna designs with feed lines
  - `metamaterial_absorber` - Jerusalem cross absorbers
  - `frequency_selective_surface` - FSS with cross slots
  - `wire_grid_polarizer` - Parallel wire grids
  - `split_ring_resonator` - Classic SRR designs

### 🖨️ **FDM-Optimized Design**
- **Millimeter scale** (not micro/nano)
- **FDM material detection** (PLA, ABS, PETG, TPU)
- **Print-friendly geometries** with proper wall thickness
- **Multiple variants** (0.8x, 1.0x, 1.2x scaling)

### 📊 **Comprehensive Metadata**
- Paper references and citations
- Geometric parameters in mm
- Manufacturing specifications
- Performance metrics

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- pip
- Virtual environment (recommended)

### Installation

```bash
# Clone the repository
git clone <repository-url>
cd metaflux

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### Basic Usage

```bash
# 1. Literature research and PDF download
invoke lit

# 2. Analyze papers for FDM printability
invoke analyze

# 3. Generate CAD designs
invoke auto

# 4. Complete pipeline (all steps)
invoke pipeline

# 5. Generate single unit cell
invoke cad -p 20e-3 -h 30e-3  # 20mm period, 30mm height
```

## 📁 Project Structure

```
metaflux/
├── README.md                 # This file
├── requirements.txt          # Python dependencies
├── tasks.py                  # Invoke task definitions
├── lit_scan.py              # Literature research & PDF download
├── auto_cad.py              # CAD generation & geometry types
├── param_cad.py             # Basic unit cell generation
├── data/
│   └── papers.json          # Analyzed paper database
├── papers/                  # Downloaded PDF papers
├── designs/                 # Generated STL files & metadata
└── venv/                    # Virtual environment
```

## 🔧 Architecture

### Core Components

#### 1. **Literature Scanner** (`lit_scan.py`)
```python
# Pure functional approach for parameter extraction
def extract_metamaterial_params(paper: Dict) -> Dict:
    """Extract FDM-printable parameters from paper abstracts."""
    # Mathematical representation: P = {d, m, f} where:
    # d = dimensions (mm scale)
    # m = manufacturing methods (FDM)
    # f = functions (antenna, lens, absorber, etc.)
```

#### 2. **CAD Generator** (`auto_cad.py`)
```python
# Geometry type determination based on paper content
def determine_geometry_type(paper: Dict) -> str:
    """Map paper content to appropriate geometry type."""
    # Pure function: paper → geometry_type
    # No side effects, deterministic output
```

#### 3. **Parameter Extractor**
```python
# FDM-scale parameter extraction
def extract_geometric_params(paper: Dict) -> Optional[Dict[str, float]]:
    """Extract mm-scale parameters for FDM printing."""
    # Mathematical representation: G = {p, h, t} where:
    # p = period (1-50 mm)
    # h = height (5-100 mm) 
    # t = thickness (0.1-5 mm)
```

### Design Philosophy

- **Pure Functional Programming**: All mathematical functions are pure with no side effects
- **Concise Code**: Optimized for readability while maintaining functionality
- **Mathematical Rigor**: Symbolic math representations in comments
- **FDM-First**: Prioritizes FDM-printable designs over micro/nano scale

## 📊 Generated Designs

### Example Output
```
✅ Generated 9 STL files:
  📄 patch_antenna_16348728_v1_28mm_28mm.stl
  📄 patch_antenna_16348728_v2_35mm_35mm.stl
  📄 patch_antenna_16348728_v3_42mm_42mm.stl
  📄 metamaterial_absorber_0a16f0a3_v1_16mm_24mm.stl
  📄 metamaterial_absorber_0a16f0a3_v2_20mm_30mm.stl
  📄 metamaterial_absorber_0a16f0a3_v3_24mm_36mm.stl
  📄 split_ring_resonator_39b4dc7b_v1_16mm_24mm.stl
  📄 split_ring_resonator_39b4dc7b_v2_20mm_30mm.stl
  📄 split_ring_resonator_39b4dc7b_v3_24mm_36mm.stl
```

### Design Variants
Each paper generates 3 variants:
- **v1**: 0.8x scale (smaller)
- **v2**: 1.0x scale (nominal)
- **v3**: 1.2x scale (larger)

## 🎛️ Configuration

### Literature Search
```python
# Default query in tasks.py
query = "3D-printed tunable IR metamaterial"

# Customize search parameters
years = 2  # Search last 2 years
max_n = 25  # Maximum papers to fetch
```

### FDM Parameters
```python
# Default FDM-scale parameters
default_period = 25e-3    # 25 mm
default_height = 35e-3    # 35 mm
default_thickness = 2e-3  # 2 mm
```

## 🔍 Analysis Results

### Paper Scoring
Papers are scored based on:
- **FDM manufacturing** (+5.0 points)
- **mm-scale dimensions** (+3.0 points)
- **Parametric/tunable** (+1.0 points)
- **Unit cell designs** (+1.0 points)
- **Micro/nano scale penalty** (-2.0 points)

### Example Analysis
```
📊 Analysis Results:
  • Total FDM-printable candidates: 3

🏆 Top candidate:
  Title: A 3D-Printed, Metallic-Free, Water-Based Metamaterial for Tunable S-Band Applications
  Score: 7.0
  Dimensions: [['35', 'mm']]
  Materials: ['pla', 'abs']
  Functions: ['metamaterial']
```

## 🛠️ Development

### Adding New Geometry Types
1. Add geometry detection in `determine_geometry_type()`
2. Create generation function `generate_new_geometry()`
3. Add to `generate_paper_specific_geometry()`

### Extending Parameter Extraction
1. Add new patterns to `extract_metamaterial_params()`
2. Update relevance scoring in `calculate_relevance_score()`
3. Test with `invoke analyze`

## 📋 Dependencies

```
cadquery>=2.5.0          # CAD generation
requests>=2.25.0         # API calls
invoke>=2.0.0            # Task automation
numpy>=1.20.0            # Numerical operations
pathlib                  # File path handling
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Follow functional programming principles
4. Add mathematical documentation
5. Test with `invoke pipeline`
6. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- Semantic Scholar API for paper data
- CadQuery for CAD generation
- Research community for metamaterial papers

## 📞 Support

For questions or issues:
1. Check the documentation
2. Review existing issues
3. Create a new issue with details

---

**MetaFlux**: Transforming research into printable reality 🚀 