export default {
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
    // eslint-disable-next-line no-undef
    return 'http://localhost:5000';
  },
  buildUrl(blueprint, location = '') {
    return [this.root(), blueprint, location].join('/');
  },

  getColor(i) {
    // assume they are the same length;
    const colorLength = this.colors.backgroundColor.length;
    return {
      backgroundColor: this.colors.backgroundColor[i % colorLength],
      borderColor: this.colors.borderColor[i % colorLength],
    };
  },

  truncate(string, max = 50) {
    if (string.length > max) {
      return `${string.substring(0, max)}...`;
    }
    return string;
  },

  titleCase(value) {
    return value
      .replace(
        /\w\S*/g, txt => txt
          .charAt(0)
          .toUpperCase() + txt.substr(1)
          .toLowerCase());
  },
  difference(arr1, arr2) {
    return arr1.filter(x => !arr2.includes(x))
      .concat(arr2.filter(x => !arr1.includes(x)));
  },
};
