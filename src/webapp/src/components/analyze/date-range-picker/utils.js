import utils from '@/utils/utils'

export const RELATIVE_DATE_RANGE_MODELS = Object.freeze({
  PERIODS: {
    DAYS: { NAME: 'd', LABEL: 'Days' },
    MONTHS: { NAME: 'm', LABEL: 'Months', IS_DISABLED: true },
    YEARS: { NAME: 'y', LABEL: 'Years', IS_DISABLED: true }
  },
  SIGNS: {
    LAST: { NAME: '-', LABEL: 'Last' },
    NEXT: { NAME: '+', LABEL: 'Next' }
  }
})

export function getAbsoluteDate(value) {
  const isRelative = getIsRelativeDateRangeFormat(value)
  const targetValue = isRelative ? getRelativeToAbsoluteDate(value) : value
  return utils.getDateFromYYYYMMDDString(targetValue)
}

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

export function getIsRelativeDateRangeFormat(value) {
  return /[+-]\d*[dmy]/.test(value)
}

function getRelativeToAbsoluteDate(value) {
  // TODO conversion
  return value
}
