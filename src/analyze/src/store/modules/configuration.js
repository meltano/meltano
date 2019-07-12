import Vue from 'vue';

import utils from '@/utils/utils';
import lodash from 'lodash';

import orchestrationsApi from '../../api/orchestrations';

const defaultState = {
  hasExtractorLoadingError: false,
  loaderInFocusConfiguration: {},
  extractorInFocusConfiguration: {},
  connectionInFocusConfiguration: {},
  extractorInFocusEntities: {},
  pipelines: [],
};

const getters = {
  getHasPipelines(state) {
    return state.pipelines.length > 0;
  },
  getHasValidConfigSettings(_, gettersRef) {
    return (configSettings) => {
      const isValid = setting => gettersRef.getIsConfigSettingValid(configSettings.config[setting.name]);
      return configSettings.settings && lodash.every(configSettings.settings, isValid);
    };
  },
  getIsConfigSettingValid() {
    return value => value !== null && value !== undefined && value !== '';
  },
};

const actions = {
  clearExtractorInFocusEntities: ({ commit }) => commit('reset', 'extractorInFocusEntities'),
  clearExtractorInFocusConfiguration: ({ commit }) => commit('reset', 'extractorInFocusConfiguration'),
  clearLoaderInFocusConfiguration: ({ commit }) => commit('reset', 'loaderInFocusConfiguration'),
  clearConnectionInFocusConfiguration: ({ commit }) => commit('reset', 'connectionInFocusConfiguration'),

  getAllPipelineSchedules({ commit }) {
    orchestrationsApi.getAllPipelineSchedules()
      .then((response) => {
        commit('setPipelines', response.data);
      });
  },

  getExtractorInFocusEntities({ commit }, extractorName) {
    commit('setHasExtractorLoadingError', false);

    orchestrationsApi.getExtractorInFocusEntities(extractorName)
      .then((response) => {
        commit('setAllExtractorInFocusEntities', response.data);
      })
      .catch(() => {
        commit('setHasExtractorLoadingError', true);
      });
  },

  getExtractorConfiguration({ commit, dispatch }, extractor) {
    dispatch('getPluginConfiguration', { name: extractor, type: 'extractors' })
      .then((response) => {
        commit('setExtractorInFocusConfiguration', response.data);
      });
  },

  getLoaderConfiguration({ commit, dispatch }, loader) {
    dispatch('getPluginConfiguration', { name: loader, type: 'loaders' })
      .then((response) => {
        commit('setLoaderInFocusConfiguration', response.data);
      });
  },

  getConnectionConfiguration({ commit, dispatch }, connection) {
    dispatch('getPluginConfiguration', { name: connection, type: 'connections' })
      .then((response) => {
        commit('setConnectionInFocusConfiguration', response.data);
      });
  },

  getPluginConfiguration(_, pluginPayload) {
    return orchestrationsApi.getPluginConfiguration(pluginPayload);
  },

  savePluginConfiguration(_, configPayload) {
    orchestrationsApi.savePluginConfiguration(configPayload);
    // TODO commit if values are properly saved, they are initially copied from
    // the extractor's config and we'd have to update this
  },

  savePipelineSchedule({ commit }, pipelineSchedulePayload) {
    orchestrationsApi.savePipelineSchedule(pipelineSchedulePayload)
      .then((response) => {
        commit('updatePipelines', response.data);
      });
  },

  selectEntities({ state }) {
    orchestrationsApi.selectEntities(state.extractorInFocusEntities)
      .then(() => {
        // TODO confirm success or handle error in UI
      });
  },

  toggleAllEntityGroupsOn({ dispatch, state }) {
    state.extractorInFocusEntities.entityGroups.forEach((group) => {
      if (!group.selected) {
        dispatch('toggleEntityGroup', group);
      }
    });
  },

  toggleAllEntityGroupsOff({ commit, dispatch, state }) {
    state.extractorInFocusEntities.entityGroups.forEach((entityGroup) => {
      if (entityGroup.selected) {
        dispatch('toggleEntityGroup', entityGroup);
      } else {
        const selectedAttributes = entityGroup.attributes.filter(attribute => attribute.selected);
        if (selectedAttributes.length > 0) {
          selectedAttributes.forEach(attribute => commit('toggleSelected', attribute));
        }
      }
    });
  },

  toggleEntityGroup({ commit }, entityGroup) {
    commit('toggleSelected', entityGroup);
    const selected = entityGroup.selected;
    entityGroup.attributes.forEach((attribute) => {
      if (attribute.selected !== selected) {
        commit('toggleSelected', attribute);
      }
    });
  },

  toggleEntityAttribute({ commit }, { entityGroup, attribute }) {
    commit('toggleSelected', attribute);
    const hasDeselectedAttribute = attribute.selected === false && entityGroup.selected;
    const hasAllSelectedAttributes = !entityGroup.attributes.find(attr => !attr.selected);
    if (hasDeselectedAttribute || hasAllSelectedAttributes) {
      commit('toggleSelected', entityGroup);
    }
  },
};

const mutations = {
  reset(state, attr) {
    if (defaultState.hasOwnProperty(attr)) {
      state[attr] = defaultState[attr];
    }
  },

  setAllExtractorInFocusEntities(state, entitiesData) {
    state.extractorInFocusEntities = entitiesData
      ? {
        extractorName: entitiesData.extractor_name,
        entityGroups: entitiesData.entity_groups,
      }
      : {};
  },

  setExtractorInFocusConfiguration(state, configuration) {
    state.extractorInFocusConfiguration = configuration;
  },

  setHasExtractorLoadingError(state, value) {
    state.hasExtractorLoadingError = value;
  },

  setLoaderInFocusConfiguration(state, configuration) {
    state.loaderInFocusConfiguration = configuration;
  },

  setConnectionInFocusConfiguration(state, configuration) {
    state.connectionInFocusConfiguration = configuration;
  },

  setPipelines(state, pipelines) {
    pipelines.forEach((pipeline) => {
      pipeline.startDate = utils.getDateStringAsIso8601OrNull(pipeline.startDate);
    });
    state.pipelines = pipelines;
  },

  toggleSelected(state, selectable) {
    Vue.set(selectable, 'selected', !selectable.selected);
  },

  updatePipelines(state, pipeline) {
    pipeline.startDate = utils.getDateStringAsIso8601OrNull(pipeline.start_date);
    state.pipelines.push(pipeline);
  },
};

export default {
  namespaced: true,
  state: lodash.cloneDeep(defaultState),
  getters,
  actions,
  mutations,
};
