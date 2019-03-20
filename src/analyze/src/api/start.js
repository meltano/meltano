import axios from 'axios';
import utils from '@/utils/utils';

export default {
  hasProject() {
    return axios.get(utils.apiUrl('start', 'has_project'));
  },

  getCwd() {
    return axios.get(utils.apiUrl('start', 'cwd'));
  },

  getExists(project) {
    return axios.get(utils.apiUrl('start', `exists/${project}`));
  },

  createProject(project) {
    return axios.post(utils.apiUrl('start', 'create'), { project });
  },
};
