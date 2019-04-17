import Vue from 'vue';
import orchestrationsApi from '../../api/orchestrations';

const state = {
  extractors: [],
  loaders: [],
  hasExtractorLoadingError: false,
  extractorEntities: {},
  currentView: 'intro',
  currentExtractor: '',
  currentConnectionName: '',
  connectionNames: [],
  currentLoader: '',
  installedPlugins: {},
  log: 'Job log will appear when run.',
};

const getters = {
  isIntroView() {
    return state.currentView === 'intro';
  },

  isExtractorView() {
    return state.currentView === 'extractor';
  },

  isLoaderView() {
    return state.currentView === 'loader';
  },

  isTransformView() {
    return state.currentView === 'transform';
  },

  isRunView() {
    return state.currentView === 'run';
  },

  canRun() {
    return !!state.currentExtractor && !!state.currentLoader;
  },

  remainingExtractors() {
    if (state.installedPlugins) {
      const installedExtractors = state.installedPlugins.extractors || [];

      if (installedExtractors && installedExtractors.length > 0) {
        return state.extractors.filter((extractor) => {
          let matchFound = false;

          for (let i = 0; i < installedExtractors.length; i += 1) {
            if (extractor === installedExtractors[i].name) {
              matchFound = true;
            }
          }

          return !matchFound;
        });
      }
    }

    return state.extractors;
  },

  remainingLoaders() {
    if (state.installedPlugins) {
      const installedLoaders = state.installedPlugins.loaders;

      if (installedLoaders && installedLoaders.length > 0) {
        return state.loaders.filter((loader) => {
          let matchFound = false;

          for (let i = 0; i < installedLoaders.length; i += 1) {
            if (loader === installedLoaders[i].name) {
              matchFound = true;
            }
          }

          return !matchFound;
        });
      }
    }

    return state.loaders;
  },
};

const actions = {
  clearExtractorEntities({ commit }) {
    commit('setAllExtractorEntities', null);
  },

  getAll({ commit }) {
    orchestrationsApi.index()
      .then((response) => {
        commit('setAll', response.data);
      });
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

  getInstalledPlugins({ commit }) {
    orchestrationsApi.installedPlugins()
      .then((response) => {
        commit('setInstalledPlugins', response.data);
      });
  },

  getConnectionNames({ commit }) {
    orchestrationsApi.connectionNames()
      .then((response) => {
        commit('setConnectionNames', response.data);
      });
  },

  currentViewClicked({ commit }, selectedCurrentView) {
    commit('setCurrentView', selectedCurrentView);
  },

  currentExtractorClicked({ commit }, e) {
    const selectedExtractor = e.target.value;
    commit('setCurrentExtractor', selectedExtractor);
  },

  currentLoaderClicked({ commit }, e) {
    const selectedLoader = e.target.value;
    commit('setCurrentLoader', selectedLoader);
  },

  currentConnectionNameClicked({ commit }, e) {
    const selectedConnectionName = e.target.value;
    commit('setCurrentConnectionName', selectedConnectionName);
  },

  selectEntities() {
    orchestrationsApi.selectEntities(state.extractorEntities)
      .then(() => {
        // TODO confirm success or handle error in UI
      });
  },

  runExtractor() {
    state.log = 'Running...';
    orchestrationsApi.extract(state.currentExtractor)
      .then((response) => {
        state.log = `Output saved to \n${response.data.output_file_paths.join(',\n')}`;
      });
  },

  runLoader() {
    state.log = 'Running...';
    orchestrationsApi.load(state.currentExtractor, state.currentLoader)
      .then((response) => {
        state.log = `CSV's Loaded \n${response.data.inserted_files.join(',\n')}`;
      });
  },

  runTransform() {
    state.log = 'Running...';
    orchestrationsApi.transform(state.currentExtractor, state.currentConnectionName)
      .then((response) => {
        state.log = `${response.data.command}\n${response.data.output}`;
      });
  },

  runJobs() {
    const payload = {
      extractor: state.currentExtractor,
      loader: state.currentLoader,
      connection_name: state.currentConnectionName,
    };
    state.log = 'Running...';
    orchestrationsApi.run(payload)
      .then((response) => {
        state.log = response.data.append;
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

  setConnectionNames(_, connectionNames) {
    state.connectionNames = connectionNames;
  },

  setCurrentView(_, selectedCurrentView) {
    state.currentView = selectedCurrentView;
  },

  setCurrentExtractor(_, selectedExtractor) {
    state.currentExtractor = selectedExtractor;
  },

  setCurrentLoader(_, selectedLoader) {
    state.currentLoader = selectedLoader;
  },

  setCurrentConnectionName(_, selectedConnectionName) {
    state.currentConnectionName = selectedConnectionName;
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
