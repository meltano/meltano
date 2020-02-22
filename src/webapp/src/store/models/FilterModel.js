export default function FilterModel({
  sourceName,
  attribute,
  filterType,
  expression = '',
  value = '',
  isActive = true
}) {
  const filter = {
    sourceName,
    name: attribute.name,
    expression,
    value,
    attribute,
    filterType,
    isActive
  }
  return filter
}
