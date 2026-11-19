class ProjectFinance {
  constructor(data) {
    this.id = data.id;
    this.project_id = data.project_id;
    this.type = data.type;
    this.amount = data.amount;
    this.description = data.description;
    this.date = data.date;
    this.artisan_id = data.artisan_id;
    this.document_id = data.document_id;
    this.created_at = data.created_at;
  }

  static TYPES = {
    ESTIMATE: 'estimate',
    DEPOSIT: 'deposit',
    PROGRESS_PAYMENT: 'progress_payment',
    FINAL_PAYMENT: 'final_payment',
    EXPENSE: 'expense',
    REFUND: 'refund'
  };

  get is_income() {
    return [ProjectFinance.TYPES.DEPOSIT, ProjectFinance.TYPES.PROGRESS_PAYMENT, ProjectFinance.TYPES.FINAL_PAYMENT].includes(this.type);
  }

  get is_expense() {
    return [ProjectFinance.TYPES.EXPENSE].includes(this.type);
  }

  toJSON() {
    return {
      id: this.id,
      project_id: this.project_id,
      type: this.type,
      amount: this.amount,
      description: this.description,
      date: this.date,
      artisan_id: this.artisan_id,
      document_id: this.document_id,
      is_income: this.is_income,
      is_expense: this.is_expense,
      created_at: this.created_at
    };
  }
}

module.exports = ProjectFinance;
