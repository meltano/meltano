import axios from 'axios';
import utils from '@/utils/utils';

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

  getSql(model, design, data) {
    return axios.post(utils.buildUrl('sql/get', `${model}/${design}`), data);
  },

  getDialect(model) {
    return axios.get(utils.buildUrl('sql/get', `${model}/dialect`));
  },

  getDistinct(model, design, field) {
    return axios.post(utils.buildUrl('sql/distinct', `${model}/${design}`), { field });
  },
};
