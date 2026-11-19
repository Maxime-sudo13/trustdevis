class ProjectDocument {
  constructor(data) {
    this.id = data.id;
    this.project_id = data.project_id;
    this.type = data.type;
    this.filename = data.filename;
    this.original_name = data.original_name;
    this.path = data.path;
    this.artisan_id = data.artisan_id;
    this.uploaded_at = data.uploaded_at;
  }

  static TYPES = {
    CONTRACT: 'contract',
    ESTIMATE: 'estimate',
    INVOICE: 'invoice',
    INSURANCE: 'insurance',
    PHOTO: 'photo',
    PLAN: 'plan',
    PERMIT: 'permit',
    FINAL_DOSSIER: 'final_dossier',
    OTHER: 'other'
  };

  get is_contract() {
    return this.type === ProjectDocument.TYPES.CONTRACT;
  }

  get is_invoice() {
    return this.type === ProjectDocument.TYPES.INVOICE;
  }

  toJSON() {
    return {
      id: this.id,
      project_id: this.project_id,
      type: this.type,
      filename: this.filename,
      original_name: this.original_name,
      path: this.path,
      artisan_id: this.artisan_id,
      uploaded_at: this.uploaded_at
    };
  }
}

module.exports = ProjectDocument;
