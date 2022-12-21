export default function FilterModel({
  filterType,
  attribute,
  expression = '',
  value = '',
  isActive = true,
}) {
  const filter = {
    filterType,
    attribute,
    expression,
    value,
    isActive,
  }
  return filter
}
