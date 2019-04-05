import orchestrationsApi from '../../api/orchestrations';

const state = {
  extractors: [],
  loaders: [],
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
    const installedExtractors = state.installedPlugins.extractors;

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

    return state.extractors;
  },

  remainingLoaders() {
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

    return state.extractors;
  },
};

const actions = {
  getAll({ commit }) {
    orchestrationsApi.index()
      .then((response) => {
        commit('setAll', response.data);
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

  updateExtractors({ commit }, itemIndex) {
    commit('removeExtractor', itemIndex);
  },
};

const mutations = {
  removeExtractor(_, itemIndex) {
    state.extractors.splice(itemIndex, 1);
  },

  setAll(_, orchestrationData) {
    state.extractors = orchestrationData.extractors.split('\n');
    state.loaders = orchestrationData.loaders.split('\n');
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

  setInstalledPlugins(_, projectConfig) {
    state.installedPlugins = projectConfig.plugins;
  },
};

export default {
  namespaced: true,
  state,
  getters,
  actions,
  mutations,
};
