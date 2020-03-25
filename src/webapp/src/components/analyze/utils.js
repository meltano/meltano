import { QUERY_ATTRIBUTE_DATA_TYPES } from '@/api/design'

export function isDateAttribute(attribute) {
  return (
    attribute.type === QUERY_ATTRIBUTE_DATA_TYPES.DATE ||
    attribute.type === QUERY_ATTRIBUTE_DATA_TYPES.TIME
  )
}
