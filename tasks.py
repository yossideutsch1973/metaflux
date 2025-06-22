from invoke import task
import sys
from pathlib import Path
from lit_scan import fetch_papers
from param_cad import generate_unit_cell
from auto_cad import batch_generate_from_papers, analyze_papers_for_cad

@task
def lit(c, q="3D-printed tunable IR metamaterial"):
    """Fetch and analyze recent metamaterial papers."""
    papers_file = fetch_papers(q)
    print(f"Enhanced literature analysis complete: {papers_file}")
    
    # Show top candidates
    candidates = analyze_papers_for_cad(papers_file)
    print(f"\nFound {len(candidates)} 3D-printable candidates:")
    for i, paper in enumerate(candidates[:3], 1):
        title = paper.get('title', 'Unknown')[:60]
        score = paper.get('relevance_score', 0)
        print(f"  {i}. [{score:.1f}] {title}...")

@task  
def cad(c, p=80e-6, h=150e-6):
    """Generate single parametric unit cell."""
    print(generate_unit_cell(float(p), float(h)))

@task
def auto(c):
    """Automated paper-to-CAD pipeline."""
    papers_file = Path("data/papers.json")
    
    if not papers_file.exists():
        print("No papers found. Running 'invoke lit' first...")
        fetch_papers("3D-printed tunable IR metamaterial")
    
    print("🤖 Running automated paper-to-CAD pipeline...")
    generated_files = batch_generate_from_papers(papers_file)
    
    print(f"\n✅ Generated {len(generated_files)} STL files:")
    for f in generated_files:
        print(f"  📄 {f.name}")
    
    return generated_files

@task 
def analyze(c):
    """Analyze current paper database."""
    papers_file = Path("data/papers.json")
    
    if not papers_file.exists():
        print("No papers database found. Run 'invoke lit' first.")
        return
    
    candidates = analyze_papers_for_cad(papers_file)
    
    print(f"📊 Analysis Results:")
    print(f"  • Total 3D-printable candidates: {len(candidates)}")
    
    if candidates:
        print(f"\n🏆 Top candidate:")
        top = candidates[0]
        print(f"  Title: {top.get('title', 'Unknown')}")
        print(f"  Score: {top.get('relevance_score', 0):.1f}")
        
        params = top.get('extracted_params', {})
        if params.get('dimensions'):
            print(f"  Dimensions: {params['dimensions']}")
        if params.get('materials'):
            print(f"  Materials: {params['materials']}")
        if params.get('functions'):
            print(f"  Functions: {params['functions']}")

@task
def pipeline(c, query="3D-printed tunable IR metamaterial"):
    """Complete end-to-end pipeline: literature → analysis → CAD generation."""
    print("🚀 Starting complete MetaFlux pipeline...")
    
    # Step 1: Literature scan
    print("\n📚 Step 1: Literature Analysis")
    papers_file = fetch_papers(query)
    
    # Step 2: Analysis  
    print("\n🔍 Step 2: Parameter Extraction")
    candidates = analyze_papers_for_cad(papers_file)
    print(f"Found {len(candidates)} viable candidates")
    
    # Step 3: CAD Generation
    print("\n🔧 Step 3: Automated CAD Generation")
    generated_files = batch_generate_from_papers(papers_file)
    
    print(f"\n🎉 Pipeline complete!")
    print(f"  📖 Papers analyzed: {len(candidates)}")
    print(f"  🏗️  STL files generated: {len(generated_files)}")
    print(f"  📁 Output directory: ./designs/")
    
    return generated_files