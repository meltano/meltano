import utils from '@/utils/utils'

export const RELATIVE_DATE_RANGE_MODELS = Object.freeze({
  PERIODS: {
    DAYS: { NAME: 'days', LABEL: 'Days' },
    MONTHS: { NAME: 'months', LABEL: 'Months', IS_DISABLED: true },
    YEARS: { NAME: 'years', LABEL: 'Years', IS_DISABLED: true }
  },
  SIGNS: {
    LAST: { NAME: '-', LABEL: 'Last' },
    NEXT: { NAME: '+', LABEL: 'Next' }
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
