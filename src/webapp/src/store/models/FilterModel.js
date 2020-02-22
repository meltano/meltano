export default function FilterModel({
  attribute,
  filterType,
  expression = '',
  value = '',
  isActive = true
}) {
  const filter = {
    sourceName: attribute.sourceName,
    name: attribute.name,
    expression,
    value,
    attribute,
    filterType,
    isActive
  }
  return filter
}
