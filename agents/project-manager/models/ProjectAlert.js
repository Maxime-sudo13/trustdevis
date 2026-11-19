class ProjectAlert {
  constructor(data) {
    this.id = data.id;
    this.project_id = data.project_id;
    this.type = data.type;
    this.severity = data.severity || 'info';
    this.message = data.message;
    this.is_read = data.is_read || false;
    this.created_at = data.created_at;
    this.resolved_at = data.resolved_at;
  }

  static TYPES = {
    BUDGET_WARNING: 'budget_warning',
    BUDGET_EXCEEDED: 'budget_exceeded',
    DELAY_WARNING: 'delay_warning',
    DELAY_EXCEEDED: 'delay_exceeded',
    STEP_VALIDATION: 'step_validation',
    DOCUMENT_MISSING: 'document_missing',
    PAYMENT_DUE: 'payment_due'
  };

  static SEVERITIES = {
    INFO: 'info',
    WARNING: 'warning',
    CRITICAL: 'critical'
  };

  get is_resolved() {
    return !!this.resolved_at;
  }

  toJSON() {
    return {
      id: this.id,
      project_id: this.project_id,
      type: this.type,
      severity: this.severity,
      message: this.message,
      is_read: this.is_read,
      is_resolved: this.is_resolved,
      created_at: this.created_at,
      resolved_at: this.resolved_at
    };
  }
}

module.exports = ProjectAlert;
