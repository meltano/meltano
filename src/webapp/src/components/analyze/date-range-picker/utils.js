import utils from '@/utils/utils'

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
