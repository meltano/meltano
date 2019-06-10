import axios from 'axios';
import utils from '@/utils/utils';

export default {
  extract(extractor) {
    return axios.post(utils.apiUrl('orchestrations', `extract/${extractor}`));
  },

  getPluginConfiguration(pluginPayload) {
    return axios.post(utils.apiUrl('orchestrations', 'get/configuration'), pluginPayload);
  },

  savePluginConfiguration(configPayload) {
    return axios.post(utils.apiUrl('orchestrations', 'save/configuration'), configPayload);
  },

  selectEntities(extractorEntities) {
    return axios.post(utils.apiUrl('orchestrations', 'select-entities'), extractorEntities);
  },

  getExtractorInFocusEntities(extractor) {
    return axios.post(utils.apiUrl('orchestrations', `entities/${extractor}`));
  },

  load(extractor, loader) {
    return axios.post(utils.apiUrl('orchestrations', `load/${loader}`), {
      extractor,
    });
  },

  transform(model, connectionName) {
    return axios.post(utils.apiUrl('orchestrations', `transform/${model}`), {
      connection_name: connectionName,
    });
  },

  connectionNames() {
    return axios.get(utils.apiUrl('orchestrations', 'connection_names'));
  },

  run(payload) {
    return axios.post(utils.apiUrl('orchestrations', 'run'), payload);
  },
};
