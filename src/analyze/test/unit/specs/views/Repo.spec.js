import { shallowMount, createLocalVue } from '@vue/test-utils';
import Vuex from 'vuex';
import Repo from '@/views/Repo';
import repos from '@/store/modules/repos';

const localVue = createLocalVue();
localVue.use(Vuex);

describe('Repo.vue', () => {
  let actions;
  let state;
  let store;

  beforeEach(() => {
    state = {
      activeView: {},
    };
    actions = {
      getRepo: jest.fn(),
      sync: jest.fn(),
    };
    store = new Vuex.Store({
      modules: {
        repos: {
          namespaced: true,
          state,
          actions,
          getters: repos.getters,
        },
      },
    });
  });

  it('calls getRepo() and sync() via created() lifecycle hook', () => {
    const wrapper = shallowMount(Repo, { store, localVue });

    expect(wrapper).toBeTruthy();
    expect(actions.getRepo).toHaveBeenCalled();
    expect(actions.sync).toHaveBeenCalled();
  });
});
