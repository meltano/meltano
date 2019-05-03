import Vue from 'vue';

import lodash from 'lodash';

import orchestrationsApi from '../../api/orchestrations';

const state = {
  extractors: [],
  loaders: [],
  hasExtractorLoadingError: false,
  extractorInFocusEntities: {},
  installedPlugins: {},
  installingExtractors: [],
  installingLoaders: [],
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
  getIsExtractorPluginInstalled(stateRef) {
    return extractor => (stateRef.installedPlugins.extractors
      ? Boolean(stateRef.installedPlugins.extractors.find(item => item.name === extractor))
      : false);
  },
  getIsInstallingExtractorPlugin(stateRef) {
    return extractor => stateRef.installingExtractors.includes(extractor);
  },
  getLoaderImageUrl(_, gettersRef) {
    return loader => (
      `/static/logos/${gettersRef.getLoaderNameWithoutPrefixedTargetDash(loader)}-logo.png`
    );
  },
  getLoaderNameWithoutPrefixedTargetDash() {
    return loader => loader.replace('target-', '');
  },
  getIsLoaderPluginInstalled(stateRef) {
    return loader => (stateRef.installedPlugins.loaders
      ? Boolean(stateRef.installedPlugins.loaders.find(item => item.name === loader))
      : false);
  },
  getIsInstallingLoaderPlugin(stateRef) {
    return loader => stateRef.installingLoaders.includes(loader);
  },
};

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

  installExtractor({ commit, dispatch }, extractor) {
    commit('installExtractorStart', extractor);

    orchestrationsApi.addExtractors({ name: extractor })
      .then(() => {
        dispatch('getInstalledPlugins')
          .then(() => {
            commit('installExtractorComplete', extractor);
          });
      });
  },

  installLoader({ commit, dispatch }, loader) {
    commit('installLoaderStart', loader);

    orchestrationsApi.addLoaders({ name: loader })
      .then(() => {
        dispatch('getInstalledPlugins')
          .then(() => {
            commit('installLoaderComplete', loader);
          });
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
  installExtractorStart(_, extractor) {
    state.installingExtractors.push(extractor);
  },

  installExtractorComplete(_, extractor) {
    lodash.pull(state.installingExtractors, extractor);
  },

  installLoaderStart(_, loader) {
    state.installingLoaders.push(loader);
  },

  installLoaderComplete(_, loader) {
    lodash.pull(state.installingExtractors, loader);
  },

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

  setHasExtractorLoadingError(_, value) {
    state.hasExtractorLoadingError = value;
  },

  setInstalledPlugins(_, projectConfig) {
    if (projectConfig.plugins) {
      state.installedPlugins = projectConfig.plugins;
    }
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
