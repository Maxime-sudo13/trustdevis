class ProjectStep {
  constructor(data) {
    this.id = data.id;
    this.project_id = data.project_id;
    this.name = data.name;
    this.description = data.description;
    this.status = data.status || 'pending';
    this.planned_start_date = data.planned_start_date;
    this.planned_end_date = data.planned_end_date;
    this.actual_start_date = data.actual_start_date;
    this.actual_end_date = data.actual_end_date;
    this.client_validated = data.client_validated || false;
    this.validated_at = data.validated_at;
    this.order_index = data.order_index || 0;
    this.created_at = data.created_at;
  }

  get is_delayed() {
    if (!this.planned_end_date || this.status === 'completed') return false;
    const today = new Date();
    const plannedEnd = new Date(this.planned_end_date);
    return today > plannedEnd && this.status !== 'completed';
  }

  get duration_days() {
    if (!this.planned_start_date || !this.planned_end_date) return null;
    const start = new Date(this.planned_start_date);
    const end = new Date(this.planned_end_date);
    return Math.ceil((end - start) / (1000 * 60 * 60 * 24));
  }

  toJSON() {
    return {
      id: this.id,
      project_id: this.project_id,
      name: this.name,
      description: this.description,
      status: this.status,
      planned_start_date: this.planned_start_date,
      planned_end_date: this.planned_end_date,
      actual_start_date: this.actual_start_date,
      actual_end_date: this.actual_end_date,
      client_validated: this.client_validated,
      validated_at: this.validated_at,
      order_index: this.order_index,
      is_delayed: this.is_delayed,
      duration_days: this.duration_days,
      created_at: this.created_at
    };
  }
}

module.exports = ProjectStep;
