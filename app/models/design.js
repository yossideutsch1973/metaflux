// app/models/design.js

export class Design {
  constructor(data, filePath = '') {
    this.paperId = data.paper_id || '';
    this.title = data.paper_title || '';
    this.geometryType = data.geometry_type || '';
    this.parameters = data.parameters || {};
    this.filePath = filePath || data.file_path || '';
    this.generatedAt = data.generated_at || '';
    this.manufacturing = data.manufacturing_method || '';
    this.scale = data.scale || '';
  }

  get displayTitle() {
    return this.title || this.paperId;
  }

  get displayGeometry() {
    return this.geometryType.replace(/_/g, ' ');
  }
} 