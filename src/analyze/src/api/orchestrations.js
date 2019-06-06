import axios from 'axios';
import utils from '@/utils/utils';

export default {
  index() {
    return axios.get(utils.apiUrl('orchestrations'));
  },

  installPlugin(installConfig) {
    return axios.post(utils.apiUrl('orchestrations', 'install-plugin'), installConfig);
  },

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

  installedPlugins() {
    return axios.get(utils.apiUrl('orchestrations', 'installed-plugins'));
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
