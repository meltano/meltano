import axios from 'axios';
import utils from './utils';

export default {
  index(model, design) {
    return axios.get(utils.buildUrl('repos/designs', `${model}/${design}`));
  },

  getTable(table) {
    return axios.get(utils.buildUrl('repos/tables', `${table}`));
  },

  loadReports() {
    return axios.get(utils.buildUrl('reports'));
  },

  loadReport(name) {
    return axios.get(utils.buildUrl('reports/load', `${name}`));
  },

  saveReport(data) {
    return axios.post(utils.buildUrl('reports', 'save'), data);
  },

  updateReport(data) {
    return axios.post(utils.buildUrl('reports', 'update'), data);
  },
};
