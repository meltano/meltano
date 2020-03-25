import {
  getDateRangesForFilters,
  getDateLabel,
  getHasValidDateRange
} from '@/components/analyze/date-range-picker/utils'
import { isDateAttribute } from '@/components/analyze/utils'

const reportDateRangeMixin = {
  computed: {
    getIsDateAttribute() {
      return isDateAttribute
    },
    getHasValidDateRange() {
      return getHasValidDateRange
    },
    dateAttributes() {
      const attributes = []
      const design = this.report.fullDesign
      const tables = [design, ...design.joins].map(t => t.relatedTable)
      tables.forEach(({ name: sourceName, columns }) => {
        columns.forEach(column => {
          if (this.getIsDateAttribute(column)) {
            attributes.push({ sourceName, ...column })
          }
        })
      })
      return attributes
    },
    getFilters() {
      return attribute => {
        const filters = this.report.queryPayload.filters || {}
        const columns = filters.columns || []
        return columns.filter(queryFilter => {
          return queryFilter.key
            ? queryFilter.key === attribute.key
            : queryFilter.sourceName === attribute.sourceName &&
                queryFilter.name === attribute.name
        })
      }
    },
    dateRanges() {
      return this.dateAttributes.map(attribute => {
        const filters = this.getFilters(attribute)
        const startFilter = filters.find(
          filter => filter.expression === 'greater_or_equal_than'
        )
        const endFilter = filters.find(
          filter => filter.expression === 'less_or_equal_than'
        )

        return getDateRangesForFilters(startFilter, endFilter).absoluteDateRange
      })
    },
    dateRange() {
      return this.dateRanges.find(dateRange =>
        this.getHasValidDateRange(dateRange)
      )
    },
    hasDateRange() {
      return this.dateRange && getHasValidDateRange(this.dateRange)
    },
    dateRangeLabel() {
      return getDateLabel(this.dateRange)
    }
  }
}

export default reportDateRangeMixin
