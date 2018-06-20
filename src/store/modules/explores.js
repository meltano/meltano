import exploreApi from '../../api/explore';

const state = {
  explore: {
    settings: {
      label: 'loading...',
    },
  },
};

const getters = {};

const actions = {
  getExplore({ commit }, { model, explore }) {
    exploreApi.index(model, explore)
      .then((data) => {
        commit('setExplore', data.data);
      });
  },
};

const mutations = {
  setExplore(_, exploreData) {
    state.explore = exploreData;
  },
};

export default {
  namespaced: true,
  state,
  getters,
  actions,
  mutations,
};
