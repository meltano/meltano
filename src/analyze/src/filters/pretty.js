export default function pretty(value) {
  try {
    return JSON.stringify(JSON.parse(value), null, 2);
  } catch (e) {
    return value;
  }
}
