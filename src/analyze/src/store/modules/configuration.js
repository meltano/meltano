import Vue from 'vue';

import orchestrationsApi from '../../api/orchestrations';

const state = {
  hasExtractorLoadingError: false,
  loaderInFocusConfiguration: {},
  extractorInFocusConfiguration: {},
  extractorInFocusEntities: {},
  pipelines: [],
};

const getters = {
  getExtractorImageUrl(_, gettersRef) {
    return extractor => (
      `/static/logos/${gettersRef.getExtractorNameWithoutPrefixedTapDash(extractor)}-logo.png`
    );
  },
  getExtractorNameWithoutPrefixedTapDash() {
    return extractor => extractor.replace('tap-', '');
  },
  getLoaderImageUrl(_, gettersRef) {
    return loader => (
      `/static/logos/${gettersRef.getLoaderNameWithoutPrefixedTargetDash(loader)}-logo.png`
    );
  },
  getLoaderNameWithoutPrefixedTargetDash() {
    return loader => loader.replace('target-', '');
  },
};

const actions = {
  clearExtractorInFocusEntities({ commit }) {
    commit('setAllExtractorInFocusEntities', null);
  },

  clearExtractorInFocusConfiguration({ commit }) {
    commit('setExtractorInFocusConfiguration', {});
  },

  clearLoaderInFocusConfiguration({ commit }) {
    commit('setLoaderInFocusConfiguration', {});
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

  getPluginConfiguration(_, pluginPayload) {
    return orchestrationsApi.getPluginConfiguration(pluginPayload);
  },

  saveExtractorConfiguration(_, configPayload) {
    orchestrationsApi.savePluginConfiguration(configPayload);
    // TODO commit if values are properly saved, they are initially copied from
    // the extractor's config and we'd have to update this
  },

  saveLoaderConfiguration(_, configPayload) {
    orchestrationsApi.savePluginConfiguration(configPayload);
    // TODO commit if values are properly saved, they are initially copied from
    // the loader's config and we'd have to update this
  },

  selectEntities() {
    orchestrationsApi.selectEntities(state.extractorInFocusEntities)
      .then(() => {
        // TODO confirm success or handle error in UI
      });
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
  setAllExtractorInFocusEntities(_, entitiesData) {
    state.extractorInFocusEntities = entitiesData
      ? {
        extractorName: entitiesData.extractor_name,
        entityGroups: entitiesData.entity_groups,
      }
      : {};
  },

  setExtractorInFocusConfiguration(_, configuration) {
    state.extractorInFocusConfiguration = configuration;
  },

  setHasExtractorLoadingError(_, value) {
    state.hasExtractorLoadingError = value;
  },

  setLoaderInFocusConfiguration(_, configuration) {
    state.loaderInFocusConfiguration = configuration;
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
