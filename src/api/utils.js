export default {
  root() {
    return 'http://localhost:5000';
  },
  buildUrl(blueprint, location = '') {
    return [this.root(), blueprint, location].join('/');
  },
};
