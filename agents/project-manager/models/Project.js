class Project {
  constructor(data) {
    this.id = data.id;
    this.name = data.name;
    this.address = data.address;
    this.work_type = data.work_type;
    this.budget_total = data.budget_total;
    this.budget_spent = data.budget_spent || 0;
    this.start_date = data.start_date;
    this.end_date = data.end_date;
    this.actual_start_date = data.actual_start_date;
    this.actual_end_date = data.actual_end_date;
    this.status = data.status || 'planning';
    this.client_id = data.client_id;
    this.description = data.description;
    this.created_at = data.created_at;
    this.updated_at = data.updated_at;
  }

  get budget_remaining() {
    return this.budget_total - this.budget_spent;
  }

  get budget_usage_percent() {
    return (this.budget_spent / this.budget_total) * 100;
  }

  get is_over_budget() {
    return this.budget_spent > this.budget_total;
  }

  get is_delayed() {
    if (!this.end_date) return false;
    const today = new Date();
    const endDate = new Date(this.end_date);
    return today > endDate && this.status !== 'completed';
  }

  toJSON() {
    return {
      id: this.id,
      name: this.name,
      address: this.address,
      work_type: this.work_type,
      budget_total: this.budget_total,
      budget_spent: this.budget_spent,
      budget_remaining: this.budget_remaining,
      budget_usage_percent: Math.round(this.budget_usage_percent * 100) / 100,
      start_date: this.start_date,
      end_date: this.end_date,
      actual_start_date: this.actual_start_date,
      actual_end_date: this.actual_end_date,
      status: this.status,
      client_id: this.client_id,
      description: this.description,
      is_over_budget: this.is_over_budget,
      is_delayed: this.is_delayed,
      created_at: this.created_at,
      updated_at: this.updated_at
    };
  }
}

module.exports = Project;
