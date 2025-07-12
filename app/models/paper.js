// app/models/paper.js

export class Paper {
  constructor(data) {
    this.id = data.paperId || data.id || '';
    this.title = data.title || '';
    this.year = data.year || '';
    this.authors = data.authors || [];
    this.venue = data.venue || '';
    this.citationCount = data.citationCount || 0;
    this.url = data.url || '';
    this.pdf = data.pdf_path || (data.openAccessPdf && data.openAccessPdf.url) || '';
    this.extracted = data.extracted_params || {};
    this.score = data.relevance_score || 0;
  }

  get displayAuthors() {
    if (!this.authors || this.authors.length === 0) return '';
    return this.authors.map(a => a.name).join(', ');
  }

  get displayYear() {
    return this.year ? `(${this.year})` : '';
  }

  get displayScore() {
    return this.score ? `[${this.score.toFixed(1)}]` : '';
  }

  get pdfLink() {
    return this.pdf || '';
  }
} 