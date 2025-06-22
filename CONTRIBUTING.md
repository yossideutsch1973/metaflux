# Contributing to MetaFlux

Thank you for your interest in contributing to MetaFlux! This document provides guidelines for contributing to the project.

## 🎯 Project Philosophy

MetaFlux follows these core principles:

- **Pure Functional Programming**: All mathematical functions should be pure with no side effects
- **Concise Code**: Optimize for readability while maintaining functionality
- **Mathematical Rigor**: Include symbolic math representations in comments
- **FDM-First**: Prioritize FDM-printable designs over micro/nano scale

## 🚀 Getting Started

### Prerequisites
- Python 3.8+
- Git
- Basic understanding of metamaterials and 3D printing

### Development Setup
```bash
# Fork and clone the repository
git clone https://github.com/your-username/metaflux.git
cd metaflux

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Install development dependencies
pip install -r requirements-dev.txt  # If available
```

## 📝 Code Style

### Python Style Guide
- Follow PEP 8 for code formatting
- Use type hints for all function parameters and return values
- Keep functions small and focused (max 50 lines)
- Use descriptive variable names

### Functional Programming Guidelines
```python
# ✅ Good: Pure function with no side effects
def calculate_relevance_score(params: Dict, text: str) -> float:
    """Calculate relevance score for paper prioritization."""
    # Mathematical representation: S = f(P, T) where:
    # S = score, P = parameters, T = text
    score = 0.0
    # ... calculation logic
    return score

# ❌ Bad: Function with side effects
def process_paper(paper: Dict) -> None:
    """Process paper and save to file."""
    # Side effect: file I/O
    with open('output.txt', 'w') as f:
        f.write(str(paper))
```

### Mathematical Documentation
```python
def extract_geometric_params(paper: Dict) -> Optional[Dict[str, float]]:
    """Extract mm-scale parameters for FDM printing.
    
    Mathematical representation: G = {p, h, t} where:
    - p = period (1-50 mm)
    - h = height (5-100 mm) 
    - t = thickness (0.1-5 mm)
    
    Returns None if no valid parameters found.
    """
```

## 🔧 Development Workflow

### 1. Create a Feature Branch
```bash
git checkout -b feature/your-feature-name
```

### 2. Make Changes
- Follow the functional programming principles
- Add comprehensive type hints
- Include mathematical documentation
- Write tests for new functionality

### 3. Test Your Changes
```bash
# Run the complete pipeline
invoke pipeline

# Test specific components
invoke lit
invoke analyze
invoke auto

# Run unit tests (if available)
pytest tests/
```

### 4. Commit Your Changes
```bash
# Use conventional commit format
git commit -m "feat: add new geometry type for frequency selective surfaces"
git commit -m "fix: correct parameter extraction for mm-scale dimensions"
git commit -m "docs: update README with new features"
```

### 5. Push and Create Pull Request
```bash
git push origin feature/your-feature-name
```

## 🏗️ Adding New Features

### Adding New Geometry Types

1. **Update geometry detection** in `auto_cad.py`:
```python
def determine_geometry_type(paper: Dict) -> str:
    # Add detection logic for your geometry
    if 'your_keyword' in text:
        return 'your_geometry_type'
```

2. **Create generation function**:
```python
def generate_your_geometry(period: float, height: float, thickness: float) -> cq.Workplane:
    """Generate your specific geometry type.
    
    Mathematical representation: G = f(p, h, t) where:
    - G = geometry, p = period, h = height, t = thickness
    """
    # Pure function implementation
    return geometry
```

3. **Add to geometry selector**:
```python
def generate_paper_specific_geometry(geometry_type: str, ...):
    if geometry_type == 'your_geometry_type':
        return generate_your_geometry(period, height, thickness)
```

### Extending Parameter Extraction

1. **Add extraction patterns** in `lit_scan.py`:
```python
def extract_metamaterial_params(paper: Dict) -> Dict:
    # Add new regex patterns for your parameters
    new_patterns = [
        r'your_pattern',
        r'another_pattern'
    ]
```

2. **Update relevance scoring**:
```python
def calculate_relevance_score(params: Dict, text: str) -> float:
    # Add scoring logic for your parameters
    if your_condition:
        score += your_points
```

## 🧪 Testing

### Running Tests
```bash
# Run all tests
pytest

# Run specific test file
pytest tests/test_lit_scan.py

# Run with coverage
pytest --cov=metaflux
```

### Writing Tests
```python
# tests/test_lit_scan.py
import pytest
from lit_scan import extract_metamaterial_params

def test_extract_metamaterial_params_fdm_paper():
    """Test parameter extraction for FDM paper."""
    paper = {
        'title': '3D Printed FDM Metamaterial',
        'abstract': '35mm period, PLA material'
    }
    
    result = extract_metamaterial_params(paper)
    
    assert result['relevance_score'] > 5.0
    assert 'FDM_3D_printing' in result['extracted_params']['manufacturing_methods']
```

## 📋 Pull Request Guidelines

### Before Submitting
- [ ] Code follows functional programming principles
- [ ] All functions have type hints
- [ ] Mathematical documentation is included
- [ ] Tests pass and coverage is maintained
- [ ] Documentation is updated
- [ ] No large files are committed (STL, PDF)

### Pull Request Template
```markdown
## Description
Brief description of changes

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Documentation update
- [ ] Code refactoring

## Testing
- [ ] Ran `invoke pipeline` successfully
- [ ] Added/updated tests
- [ ] All tests pass

## Mathematical Documentation
- [ ] Added symbolic representations
- [ ] Updated function documentation

## Checklist
- [ ] Code follows functional programming principles
- [ ] Type hints are comprehensive
- [ ] No side effects in pure functions
- [ ] FDM-printable scale maintained
```

## 🐛 Reporting Bugs

### Bug Report Template
```markdown
## Bug Description
Clear description of the bug

## Steps to Reproduce
1. Run `invoke lit`
2. Run `invoke auto`
3. Observe error

## Expected Behavior
What should happen

## Actual Behavior
What actually happens

## Environment
- Python version:
- OS:
- MetaFlux version:

## Additional Context
Any other relevant information
```

## 📚 Documentation

### Updating Documentation
- Keep README.md current with new features
- Update CHANGELOG.md for all changes
- Add mathematical documentation to functions
- Include examples in docstrings

### Documentation Standards
```python
def your_function(param1: float, param2: str) -> Dict[str, Any]:
    """Brief description of function.
    
    Mathematical representation: R = f(p1, p2) where:
    - R = result, p1 = param1, p2 = param2
    
    Args:
        param1: Description with units
        param2: Description
        
    Returns:
        Dictionary with result data
        
    Raises:
        ValueError: When parameters are invalid
        
    Example:
        >>> result = your_function(1.0, "test")
        >>> print(result['key'])
        'value'
    """
```

## 🤝 Community Guidelines

### Code of Conduct
- Be respectful and inclusive
- Focus on constructive feedback
- Help others learn and grow
- Follow the project's functional programming philosophy

### Communication
- Use clear, concise language
- Provide context for suggestions
- Ask questions when unsure
- Share knowledge and insights

## 📞 Getting Help

- **Issues**: Create an issue for bugs or feature requests
- **Discussions**: Use GitHub Discussions for questions
- **Documentation**: Check README.md and inline docs first

Thank you for contributing to MetaFlux! 🚀 