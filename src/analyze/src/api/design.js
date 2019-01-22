import axios from 'axios';
import utils from './utils';

export default {
  index(model, design) {
    return axios.get(utils.buildUrl('repos/designs', `${model}/${design}`));
  },

  getSql(model, design, data) {
    return axios.post(utils.buildUrl('sql/get', `${model}/${design}`), data);
  },

  saveReport(model, design, data) {
    console.log('api SaveReport', model, design, data);
  },

  getDialect(model) {
    return axios.get(utils.buildUrl('sql/get', `${model}/dialect`));
  },

  getDistinct(model, design, field) {
    return axios.post(utils.buildUrl('sql/distinct', `${model}/${design}`), { field });
  },

  getTable(table) {
    return axios.get(utils.buildUrl('repos/tables', `${table}`));
  },
};
