import exploreApi from '../../api/explore';

const state = {
  explore: {
    settings: {
      label: 'loading...',
    },
  },
  selected: [],
};

const getters = {};

const actions = {
  getExplore({ commit }, { model, explore }) {
    exploreApi.index(model, explore)
      .then((data) => {
        commit('setExplore', data.data);
      });
  },

  expandRow({ commit }, index) {
    commit('toggleCollapsed', index);
  },
};

const mutations = {
  setExplore(_, exploreData) {
    state.explore = exploreData;
  },

  toggleCollapsed(_, index) {
    state.explore.views[index].collapsed = !state.explore.views[index].collapsed;
  },
};

export default {
  namespaced: true,
  state,
  getters,
  actions,
  mutations,
};
