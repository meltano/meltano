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
      .then((data) => {
        commit('setAll', data.data);
      });
  },

  getConnectionNames({ commit }) {
    orchestrationsApi.connectionNames()
      .then((data) => {
        commit('setConnectionNames', data.data);
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
      .then((data) => {
        state.log = `Output saved to \n${data.data.output_file_paths.join(',\n')}`;
      });
  },

  runLoader() {
    state.log = 'Running...';
    orchestrationsApi.load(state.currentExtractor, state.currentLoader)
      .then((data) => {
        state.log = `CSV's Loaded \n${data.data.inserted_files.join(',\n')}`;
      });
  },

  runTransform() {
    state.log = 'Running...';
    orchestrationsApi.transform(state.currentExtractor, state.currentConnectionName)
      .then((data) => {
        state.log = `${data.data.command}\n${data.data.output}`;
      });
  },

  runJobs() {
    const payload = {
      extractor: state.currentExtractor,
      loader: state.currentLoader,
    };
    state.log = 'Running...';
    orchestrationsApi.run(payload)
      .then((data) => {
        state.log = data.data.append;
      });
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
  }
};

export default {
  namespaced: true,
  state,
  getters,
  actions,
  mutations,
};
