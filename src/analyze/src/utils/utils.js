export default {

  // Color Utils
  colors: {
    backgroundColor: [
      'rgba(255, 99, 132, 0.2)',
      'rgba(54, 162, 235, 0.2)',
      'rgba(255, 206, 86, 0.2)',
      'rgba(75, 192, 192, 0.2)',
      'rgba(153, 102, 255, 0.2)',
      'rgba(255, 159, 64, 0.2)',
    ],
    borderColor: [
      'rgba(255,99,132,1)',
      'rgba(54, 162, 235, 1)',
      'rgba(255, 206, 86, 1)',
      'rgba(75, 192, 192, 1)',
      'rgba(153, 102, 255, 1)',
      'rgba(255, 159, 64, 1)',
    ],
  },

  root() {
    return 'http://localhost:5000';
  },

  apiUrl(blueprint, location = '') {
    return [this.root(), 'api/v1', blueprint, location].join('/');
  },

  getColor(i) {
    // assume they are the same length;
    const colorLength = this.colors.backgroundColor.length;
    return {
      backgroundColor: this.colors.backgroundColor[i % colorLength],
      borderColor: this.colors.borderColor[i % colorLength],
    };
  },

  // Collection Utils
  difference(arr1, arr2) {
    return arr1.filter(x => !arr2.includes(x))
      .concat(arr2.filter(x => !arr1.includes(x)));
  },

  // String Utils
  capitalize(value) {
    if (!value) {
      return '';
    }
    const capMe = value.toString();
    return capMe.charAt(0).toUpperCase() + capMe.slice(1);
  },
  hyphenate(value, prepend) {
    if (!value) {
      return '';
    }
    let hyphenateMe = `${prepend}-` || '';
    hyphenateMe += value.toLowerCase().replace(/\s\s*/g, '-');
    return hyphenateMe;
  },
  jsDashify(type, name) {
    if (!type || !name) {
      return '';
    }
    return this.hyphenate(name, `js-${type.toLowerCase()}`);
  },
  pretty(value) {
    try {
      return JSON.stringify(JSON.parse(value), null, 2);
    } catch (e) {
      return value;
    }
  },
  singularize(value) {
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
  titleCase(value) {
    return value
      .replace(
        /\w\S*/g, txt => txt
          .charAt(0)
          .toUpperCase() + txt.substr(1)
          .toLowerCase());
  },
  truncate(string, max = 50) {
    if (string.length > max) {
      return `${string.substring(0, max)}...`;
    }
    return string;
  },
};
