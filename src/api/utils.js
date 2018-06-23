export default {
  root() {
    return 'http://localhost:5000';
  },
  buildUrl(blueprint, location = '') {
    return [this.root(), blueprint, location].join('/');
  },

  titleCase(value) {
    return value
      .replace(
        /\w\S*/g, txt => txt
          .charAt(0)
          .toUpperCase() + txt.substr(1)
          .toLowerCase());
  },
};
