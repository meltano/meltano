const regExpConnectorLogo = /(?:tap-|target-)?(.*)/;
const regExpPrivateInput = /(password|private|token)/;

export default {

  // Path Utils
  root(path = '/') {
    // window.FLASK should be injected in the template
    // either by Webpack (dev) or Flask (prod)
    return `${FLASK.appUrl}${path}`;
  },

  apiRoot(path = '/') {
    return this.root(`/api/v1${path}`);
  },

  apiUrl(blueprint, location = '') {
    const path = [blueprint, location].join('/');
    return this.apiRoot().concat(path);
  },

  docsUrl(path = '/', fragment) {
    fragment = fragment ? `#${fragment}` : '';

    return `https://meltano.com/docs${path}.html${fragment}`;
  },

  getConnectorLogoUrl(connectorName) {
    connectorName = connectorName === "postgresql" ? "postgres" : connectorName;
    const name = regExpConnectorLogo.exec(connectorName)[1];

    return `/static/logos/${name}-logo.png`;
  },

  getIsSubRouteOf(parentPath, currentPath) {
    return currentPath.includes(parentPath);
  },

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
  inferInputType(value, defaultType = 'text') {
    let type = defaultType;
    if (regExpPrivateInput.test(value)) {
      type = 'password';
    }
    return type;
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
  underscoreToSpace(value) {
    return value.replace(/_/g, ' ');
  },

  // Date Utils
  getDateStringAsIso8601OrNull(dateString) {
    return dateString ? new Date(dateString).toISOString() : null;
  },

  getInputDateMeta() {
    return {
      min: '2000-01-01',
      pattern: '[0-9]{4}-[0-9]{2}-[0-9]{2}',
      today: this.formatDateStringYYYYMMDD(new Date()),
    };
  },

  getIsDateStringInFormatYYYYMMDD(dateString) {
    const result = /[0-9]{4}-[0-9]{2}-[0-9]{2}/.test(dateString);
    return result;
  },

  formatDateStringYYYYMMDD(date) {
    return new Date(date).toISOString().split('T')[0];
  },
};
