import axios from 'axios';
import utils from '@/utils/utils';

export default {
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
