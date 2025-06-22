from pathlib import Path
import requests, json, datetime as dt
import re
from typing import Dict, List, Optional
import urllib.parse

def fetch_papers(query: str, years: int = 2, max_n: int = 25) -> Path:
    """Fetch enriched paper data from Semantic Scholar API with abstracts and metadata."""
    y0 = dt.date.today().year - years
    
    # Enhanced fields for richer data extraction
    fields = "paperId,title,abstract,year,authors,venue,citationCount,fieldsOfStudy,url,openAccessPdf"
    url = (
        "https://api.semanticscholar.org/graph/v1/paper/search"
        f"?query={query}&year={y0}-{dt.date.today().year}&limit={max_n}"
        f"&fields={fields}"
    )
    
    response = requests.get(url, timeout=30)
    papers = response.json().get("data", [])
    
    # Enrich papers with extracted parameters and download PDFs
    enriched_papers = []
    for paper in papers:
        enriched = extract_metamaterial_params(paper)
        if enriched.get('relevance_score', 0) > 1.0:  # Only process relevant papers
            enriched = download_paper_pdf(enriched)
            enriched_papers.append(enriched)
    
    out = Path(__file__).parent / "data" / "papers.json"
    out.parent.mkdir(exist_ok=True)
    out.write_text(json.dumps(enriched_papers, indent=2))
    return out

def download_paper_pdf(paper: Dict) -> Dict:
    """Download PDF if available and save to papers folder."""
    enhanced_paper = paper.copy()
    
    # Try to get PDF URL
    pdf_url = None
    if paper.get('openAccessPdf') and paper['openAccessPdf'].get('url'):
        pdf_url = paper['openAccessPdf']['url']
    elif paper.get('url') and 'arxiv.org' in paper['url']:
        # Convert arXiv URL to PDF
        arxiv_id = paper['url'].split('/')[-1]
        pdf_url = f"https://arxiv.org/pdf/{arxiv_id}.pdf"
    
    if pdf_url:
        try:
            # Create papers folder
            papers_folder = Path(__file__).parent / "papers"
            papers_folder.mkdir(exist_ok=True)
            
            # Create filename from paper title
            title = paper.get('title', 'Unknown')
            safe_title = re.sub(r'[^\w\s-]', '', title)
            safe_title = re.sub(r'\s+', '_', safe_title)[:50]
            filename = f"{safe_title}.pdf"
            pdf_path = papers_folder / filename
            
            # Download PDF if it doesn't exist
            if not pdf_path.exists():
                print(f"📥 Downloading: {title[:50]}...")
                response = requests.get(pdf_url, timeout=30)
                if response.status_code == 200:
                    pdf_path.write_bytes(response.content)
                    enhanced_paper['pdf_path'] = str(pdf_path)
                    print(f"✅ Downloaded: {filename}")
                else:
                    print(f"❌ Failed to download: {filename}")
            else:
                enhanced_paper['pdf_path'] = str(pdf_path)
                print(f"📄 Already exists: {filename}")
                
        except Exception as e:
            print(f"⚠️  PDF download failed for {paper.get('title', 'Unknown')}: {e}")
    
    return enhanced_paper

def extract_metamaterial_params(paper: Dict) -> Dict:
    """Extract geometric and physical parameters from paper abstracts."""
    enhanced_paper = paper.copy()
    
    abstract = paper.get("abstract", "") or ""
    title = paper.get("title", "") or ""
    text = f"{title} {abstract}".lower()
    
    # Extract numerical parameters using regex
    params = {}
    
    # Frequency ranges (GHz, THz, etc.)
    freq_patterns = [
        r'(\d+(?:\.\d+)?)\s*-?\s*(\d+(?:\.\d+)?)\s*(ghz|thz)',
        r'(\d+(?:\.\d+)?)\s*(ghz|thz)',
        r'(infrared|ir|terahertz|thz|microwave)'
    ]
    
    for pattern in freq_patterns:
        matches = re.findall(pattern, text)
        if matches:
            params['frequency_info'] = matches
            break
    
    # Geometric dimensions - FOCUS ON MM SCALE FOR FDM PRINTING
    size_patterns = [
        r'(\d+(?:\.\d+)?)\s*(mm|cm)',  # Focus on mm/cm scale
        r'(\d+(?:\.\d+)?)\s*(millimeter|centimeter)',
        r'period.*?(\d+(?:\.\d+)?)\s*(mm|cm)',
        r'unit cell.*?(\d+(?:\.\d+)?)\s*(mm|cm)',
        r'feature size.*?(\d+(?:\.\d+)?)\s*(mm|cm)'
    ]
    
    dimensions = []
    for pattern in size_patterns:
        matches = re.findall(pattern, text)
        dimensions.extend(matches)
    
    if dimensions:
        params['dimensions'] = dimensions
    
    # Manufacturing methods - PRIORITIZE FDM
    manufacturing = []
    if any(term in text for term in ['fdm', 'fused deposition', 'filament', 'extrusion']):
        manufacturing.append('FDM_3D_printing')
        manufacturing.append('3D_printing')  # Also add general category
    elif any(term in text for term in ['3d print', 'additive', 'sla', 'stereolithography']):
        manufacturing.append('3D_printing')
    if any(term in text for term in ['lithography', 'photolithography', 'electron beam']):
        manufacturing.append('lithography')
    if any(term in text for term in ['etching', 'etch']):
        manufacturing.append('etching')
    
    if manufacturing:
        params['manufacturing_methods'] = manufacturing
    
    # Material properties - FOCUS ON FDM MATERIALS
    materials = []
    fdm_materials = ['pla', 'abs', 'petg', 'tpu', 'tpe', 'polycarbonate', 'nylon', 'pva', 'support']
    general_materials = ['metal', 'dielectric', 'polymer', 'silicon', 'gold', 'copper', 'silver', 'resin']
    
    # Check FDM materials first
    for term in fdm_materials:
        if term in text:
            materials.append(term)
    
    # Add general materials if no FDM-specific ones found
    if not materials:
        for term in general_materials:
            if term in text:
                materials.append(term)
    
    if materials:
        params['materials'] = materials
    
    # Functionality keywords
    functions = []
    function_terms = ['absorber', 'antenna', 'filter', 'lens', 'polarizer', 'cloaking', 'negative index', 'metamaterial', 'unit cell']
    for term in function_terms:
        if term in text:
            functions.append(term)
    
    if functions:
        params['functions'] = functions
    
    enhanced_paper['extracted_params'] = params
    enhanced_paper['relevance_score'] = calculate_relevance_score(params, text)
    
    return enhanced_paper

def calculate_relevance_score(params: Dict, text: str) -> float:
    """Calculate relevance score for automated prioritization - PRIORITIZE FDM PRINTABLE."""
    score = 0.0
    
    # MUCH higher score for FDM 3D printable designs
    if params.get('manufacturing_methods'):
        if 'FDM_3D_printing' in params['manufacturing_methods']:
            score += 5.0  # Highest priority for FDM
        elif '3D_printing' in params['manufacturing_methods']:
            score += 2.0  # Lower priority for other 3D printing
    
    # Higher score for MM scale (FDM printable)
    dimensions = params.get('dimensions', [])
    if dimensions:
        for value, unit in dimensions:
            try:
                val = float(value)
                if unit in ['mm', 'cm'] and 0.1 <= val <= 100:  # FDM printable range
                    score += 3.0
                    break
            except ValueError:
                continue
    
    # Penalize micro/nano scale (not FDM printable)
    if any('μm' in str(d) or 'um' in str(d) or 'nm' in str(d) for d in dimensions):
        score -= 2.0  # Penalty for micro/nano scale
    
    # Higher score for parametric/tunable designs
    if any(term in text for term in ['tunable', 'parametric', 'configurable', 'reconfigurable']):
        score += 1.0
    
    # Higher score for unit cell designs
    if any(term in text for term in ['unit cell', 'periodic', 'lattice', 'metamaterial']):
        score += 1.0
    
    # Bonus for recent high-citation papers
    return score