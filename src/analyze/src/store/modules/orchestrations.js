import Vue from 'vue';
import orchestrationsApi from '../../api/orchestrations';

const state = {
  extractors: [],
  loaders: [],
  hasExtractorLoadingError: false,
  extractorInFocusEntities: {},
  extractorInFocus: null,
  loaderInFocus: null,
  installedPlugins: {},
};

const getters = {};

const actions = {
  clearExtractorInFocusEntities({ commit }) {
    commit('setAllExtractorInFocusEntities', null);
  },

  getAll({ commit }) {
    orchestrationsApi.index()
      .then((response) => {
        commit('setAll', response.data);
      })
      .catch(() => {});
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
    orchestrationsApi.selectEntities(state.extractorInFocusEntities)
      .then(() => {
        // TODO confirm success or handle error in UI
      });
  },

  setExtractorInFocus({ commit }, extractor) {
    commit('setExtractorInFocus', extractor);
  },

  setLoaderInFocus({ commit }, loader) {
    commit('setLoaderInFocus', loader);
  },

  toggleAllEntityGroupsOn({ dispatch }) {
    state.extractorInFocusEntities.entityGroups.forEach((group) => {
      if (!group.selected) {
        dispatch('toggleEntityGroup', group);
      }
    });
  },

  toggleAllEntityGroupsOff({ commit, dispatch }) {
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
  setAll(_, orchestrationData) {
    state.extractors = orchestrationData.extractors;
    state.loaders = orchestrationData.loaders;
  },

  setAllExtractorInFocusEntities(_, entitiesData) {
    state.extractorInFocusEntities = entitiesData
      ? {
        extractorName: entitiesData.extractor_name,
        entityGroups: entitiesData.entity_groups,
      }
      : {};
  },

  setExtractorInFocus(_, selectedExtractor) {
    state.extractorInFocus = selectedExtractor;
  },

  setLoaderInFocus(_, selectedLoader) {
    state.loaderInFocus = selectedLoader;
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
