export default function capitalize(value) {
  if (!value) {
    return '';
  }
  const capMe = value.toString();
  return capMe.charAt(0).toUpperCase() + capMe.slice(1);
}
