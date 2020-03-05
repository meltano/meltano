import utils from '@/utils/utils'

export const RELATIVE_DATE_RANGE_MODELS = Object.freeze({
  PERIODS: {
    DAYS: { name: 'days', label: 'Days' },
    MONTHS: { name: 'months', label: 'Months' },
    YEARS: { name: 'years', label: 'Years' }
  },
  SIGNS: {
    LAST: { name: '-', label: 'Last' },
    NEXT: { name: '+', label: 'Next' }
  }
})

export function getDateLabel(attributePair) {
  return this.getHasValidDateRange(attributePair.dateRange)
    ? `${utils.formatDateStringYYYYMMDD(
        attributePair.dateRange.start
      )} - ${utils.formatDateStringYYYYMMDD(attributePair.dateRange.end)}`
    : 'None'
}

export function getHasValidDateRange(dateRange) {
  return dateRange.start && dateRange.end
}
