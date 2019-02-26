export default {
  capitalize: (value) => {
    if (!value) {
      return '';
    }
    const capMe = value.toString();
    return capMe.charAt(0).toUpperCase() + capMe.slice(1);
  },
  hyphenate: (value, prepend) => {
    if (!value) {
      return '';
    }
    let hyphenateMe = `${prepend}-` || '';
    hyphenateMe += value.toLowerCase().replace(/\s\s*/g, '-');
    return hyphenateMe;
  },
  pretty: (value) => {
    try {
      return JSON.stringify(JSON.parse(value), null, 2);
    } catch (e) {
      return value;
    }
  },
  singularize: (value) => {
    if (!value) {
      return '';
    }
    // A more robust implementation is encouraged (currently assumes English and 's' at tail)
    let singularizeMe = value.toString();
    const lastChar = singularizeMe[singularizeMe.length - 1];
    if (lastChar.toLowerCase() === 's') {
      singularizeMe = singularizeMe.slice(0, -1);
    }
    return singularizeMe;
  },
};
