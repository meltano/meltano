import Vue from 'vue';
import orchestrationsApi from '../../api/orchestrations';

const state = {
  extractors: [],
  loaders: [],
  hasExtractorLoadingError: false,
  extractorEntities: {},
  currentExtractor: '',
  currentLoader: '',
  installedPlugins: {},
};

const getters = {};

const actions = {
  clearExtractorEntities({ commit }) {
    commit('setAllExtractorEntities', null);
  },

  getAll({ commit }) {
    orchestrationsApi.index()
      .then((response) => {
        commit('setAll', response.data);
      })
      .catch(() => {});
  },

  getExtractorEntities({ commit }, extractorName) {
    commit('setHasExtractorLoadingError', false);

    orchestrationsApi.getExtractorEntities(extractorName)
      .then((response) => {
        commit('setAllExtractorEntities', response.data);
      })
      .catch(() => {
        commit('setHasExtractorLoadingError', true);
      });
  },

  saveExtractorConfiguration(_, configPayload) {
    orchestrationsApi.saveExtractorConfiguration(configPayload);
    // TODO commit if values are properly saved, they are initially copied from
    // the extractor's config and we'd have to update this
  },

  getInstalledPlugins({ commit }) {
    orchestrationsApi.installedPlugins()
      .then((response) => {
        commit('setInstalledPlugins', response.data);
      });
  },

  selectEntities() {
    orchestrationsApi.selectEntities(state.extractorEntities)
      .then(() => {
        // TODO confirm success or handle error in UI
      });
  },

  toggleAllEntityGroupsOn({ dispatch }) {
    state.extractorEntities.entityGroups.forEach((group) => {
      if (!group.selected) {
        dispatch('toggleEntityGroup', group);
      }
    });
  },

  toggleAllEntityGroupsOff({ commit, dispatch }) {
    state.extractorEntities.entityGroups.forEach((entityGroup) => {
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
  setAll(_, orchestrationData) {
    state.extractors = orchestrationData.extractors;
    state.loaders = orchestrationData.loaders;
  },

  setAllExtractorEntities(_, entitiesData) {
    state.extractorEntities = entitiesData
      ? {
        extractorName: entitiesData.extractor_name,
        entityGroups: entitiesData.entity_groups,
      }
      : {};
  },

  setCurrentExtractor(_, selectedExtractor) {
    state.currentExtractor = selectedExtractor;
  },

  setCurrentLoader(_, selectedLoader) {
    state.currentLoader = selectedLoader;
  },

  setHasExtractorLoadingError(_, value) {
    state.hasExtractorLoadingError = value;
  },

  setInstalledPlugins(_, projectConfig) {
    state.installedPlugins = projectConfig.plugins;
  },

  toggleSelected(_, selectable) {
    Vue.set(selectable, 'selected', !selectable.selected);
  },
};

export default {
  namespaced: true,
  state,
  getters,
  actions,
  mutations,
};
