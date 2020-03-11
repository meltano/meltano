import moment from 'moment'

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
  const targetValue = isRelative
    ? getRelativeToAbsoluteDateString(value)
    : value

  return utils.getDateFromYYYYMMDDString(targetValue)
}

export function getDateLabel(attributePair) {
  return this.getHasValidDateRange(attributePair.absoluteDateRange)
    ? `${utils.formatDateStringYYYYMMDD(
        attributePair.absoluteDateRange.start
      )} - ${utils.formatDateStringYYYYMMDD(
        attributePair.absoluteDateRange.end
      )}`
    : 'None'
}

export function getHasValidDateRange(dateRange) {
  return dateRange.start && dateRange.end
}

export function getIsRelativeDateRangeFormat(value) {
  return /[+-]\d*[dmy]/.test(value)
}

export function getIsRelativeLast(value) {
  return value === RELATIVE_DATE_RANGE_MODELS.SIGNS.LAST.NAME
}

export function getNullDateRange() {
  return { start: null, end: null }
}

export function getRelativeOffsetFromDateRange(dateRange) {
  const { start, end } = dateRange
  const startMatches = getRelativeSignNumberPeriod(start)
  const endMatches = getRelativeSignNumberPeriod(end)
  const absStartNumber = Math.abs(startMatches.number)
  const absEndNumber = Math.abs(endMatches.number)

  // If the numbers are equal it doesn't matter which key we pick, otherwise we want the key associated with the greater value
  const key = absStartNumber > absEndNumber ? 'start' : 'end'
  return dateRange[key]
}

export function getRelativeSignNumberPeriod(value) {
  const match = value.match(/([+-])(\d*)([dmy])/)
  const sign = match[1]
  const number = match[2]
  const period = match[3]
  return { sign, number, period }
}

function getRelativeToAbsoluteDateString(value) {
  const { sign, number, period } = getRelativeSignNumberPeriod(value)
  const method = getIsRelativeLast(sign) ? 'subtract' : 'add'
  const absoluteMoment = moment()[method](number, period)

  // TODO may or may not have to account and refactor for type time vs. type date

  return utils.formatDateStringYYYYMMDD(absoluteMoment.toDate())
}
