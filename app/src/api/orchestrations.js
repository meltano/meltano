import axios from 'axios';
import utils from './utils';

export default {
  index() {
    return axios.get(utils.buildUrl('orchestrations'));
  },

  extract(extractor) {
    return axios.post(utils.buildUrl('orchestrations', `extract/${extractor}`));
  },

  load(extractor, loader) {
    return axios.post(utils.buildUrl('orchestrations', `load/${loader}`), {
      extractor,
    });
  },

  run(payload) {
    return axios.post(utils.buildUrl('orchestrations', 'run'), payload);
  },
};
