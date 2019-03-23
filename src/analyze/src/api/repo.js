import axios from 'axios';
import utils from '@/utils/utils';

export default {
  project_by_slug(slug) {
    return axios.get(utils.apiUrl('repos', `projects/${slug}`));
  },

  file(slug, id) {
    return axios.get(utils.apiUrl('repos', `projects/${slug}/file/${id}`));
  },

  lint(slug) {
    return axios.get(utils.apiUrl('repos', `projects/${slug}/lint`));
  },

  sync(slug) {
    return axios.get(utils.apiUrl('repos', `projects/${slug}/sync`));
  },

  models(slug) {
    return axios.get(utils.apiUrl('repos', `projects/${slug}/models`));
  },
};
