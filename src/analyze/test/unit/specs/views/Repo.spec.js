import { shallowMount, createLocalVue } from '@vue/test-utils';
import Vuex from 'vuex';
import Repo from '@/views/Repo';

const localVue = createLocalVue();
localVue.use(Vuex);

describe('Repo.vue', () => {
  let actions;
  let store;

  beforeEach(() => {
    actions = {
      'repos/getRepo': jest.fn(),
      'repos/sync': jest.fn(),
    };
    store = new Vuex.Store({
      state: {},
      modules: {
        repos: actions,
      },
    });
  });

  test('is a Vue instance', () => {
    const wrapper = shallowMount(Repo, { store, localVue });
    expect(wrapper.isVueInstance()).toBeTruthy();
  });
});
