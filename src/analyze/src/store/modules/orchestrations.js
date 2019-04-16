import orchestrationsApi from '../../api/orchestrations';

const state = {
  extractors: [],
  loaders: [],
  currentView: 'intro',
  currentExtractor: '',
  currentConnectionName: '',
  connectionNames: [],
  currentLoader: '',
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
};

const actions = {
  getAll({ commit }) {
    orchestrationsApi.index()
      .then((response) => {
        commit('setAll', response.data);
      })
      .catch(() => {});
  },

  getConnectionNames({ commit }) {
    orchestrationsApi.connectionNames()
      .then((response) => {
        commit('setConnectionNames', response.data);
      })
      .catch(() => {});
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
      })
      .catch(() => {});
  },

  runLoader() {
    state.log = 'Running...';
    orchestrationsApi.load(state.currentExtractor, state.currentLoader)
      .then((response) => {
        state.log = `CSV's Loaded \n${response.data.inserted_files.join(',\n')}`;
      })
      .catch(() => {});
  },

  runTransform() {
    state.log = 'Running...';
    orchestrationsApi.transform(state.currentExtractor, state.currentConnectionName)
      .then((response) => {
        state.log = `${response.data.command}\n${response.data.output}`;
      })
      .catch(() => {});
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
      })
      .catch(() => { });
  },
};

const mutations = {
  setAll(_, orchestrationData) {
    state.extractors = orchestrationData.extractors;
    state.loaders = orchestrationData.loaders;
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
};

export default {
  namespaced: true,
  state,
  getters,
  actions,
  mutations,
};
