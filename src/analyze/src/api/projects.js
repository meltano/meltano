import axios from 'axios';
import utils from '@/utils/utils';

export default {
  getProjects() {
    return axios.get(utils.apiUrl('projects'));
  },

  hasProject() {
    return axios.get(utils.apiUrl('projects', 'has_project'));
  },

  getCwd() {
    return axios.get(utils.apiUrl('projects', 'cwd'));
  },

  getExists(project) {
    return axios.get(utils.apiUrl('projects', `exists/${project}`));
  },

  createProject(project) {
    return axios.post(utils.apiUrl('projects', 'create'), { project });
  },
};
