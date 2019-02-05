export default function hyphenate(value, prepend) {
  if (!value) {
    return '';
  }
  let hyphenateMe = `${prepend}-` || '';
  hyphenateMe += value.toLowerCase().replace(/\s\s*/g, '-');
  return hyphenateMe;
}
