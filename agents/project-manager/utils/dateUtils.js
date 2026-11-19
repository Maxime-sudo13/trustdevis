const { format, parseISO, differenceInDays, isPast, isFuture } = require('date-fns');
const { fr } = require('date-fns/locale');

const DateUtils = {
  // Formater une date
  formatDate: (date, formatStr = 'dd/MM/yyyy') => {
    if (!date) return null;
    const d = typeof date === 'string' ? parseISO(date) : date;
    return format(d, formatStr, { locale: fr });
  },

  // Formater une date avec heure
  formatDateTime: (date) => {
    if (!date) return null;
    const d = typeof date === 'string' ? parseISO(date) : date;
    return format(d, 'dd/MM/yyyy HH:mm', { locale: fr });
  },

  // Calculer la différence en jours
  daysBetween: (date1, date2) => {
    if (!date1 || !date2) return null;
    const d1 = typeof date1 === 'string' ? parseISO(date1) : date1;
    const d2 = typeof date2 === 'string' ? parseISO(date2) : date2;
    return differenceInDays(d2, d1);
  },

  // Vérifier si une date est passée
  isPast: (date) => {
    if (!date) return false;
    const d = typeof date === 'string' ? parseISO(date) : date;
    return isPast(d);
  },

  // Vérifier si une date est future
  isFuture: (date) => {
    if (!date) return false;
    const d = typeof date === 'string' ? parseISO(date) : date;
    return isFuture(d);
  },

  // Obtenir le début de la semaine
  getStartOfWeek: (date = new Date()) => {
    const d = typeof date === 'string' ? parseISO(date) : date;
    const day = d.getDay();
    const diff = d.getDate() - day + (day === 0 ? -6 : 1);
    return new Date(d.setDate(diff));
  },

  // Obtenir la fin de la semaine
  getEndOfWeek: (date = new Date()) => {
    const start = DateUtils.getStartOfWeek(date);
    return new Date(start.setDate(start.getDate() + 6));
  }
};

module.exports = DateUtils;
