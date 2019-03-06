import { mount, createLocalVue, shallowMount } from '@vue/test-utils';
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
    state = repos.state;
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

    expect(wrapper.html()).toBeTruthy();
    expect(actions.getRepo).toHaveBeenCalled();
    expect(actions.sync).toHaveBeenCalled();
  });

  it('renders no code or markdown by default', () => {
    const wrapper = mount(Repo, { store, localVue });
    expect(wrapper.contains('#code-container')).toBe(false);
    expect(wrapper.contains('#markdown-container')).toBe(false);
  });

  it('renders markdown in the preview pane for markdown files', () => {
    state.activeView = { is_markdown: true, file: '<h1>Title</h1>', populated: true };
    const wrapper = mount(Repo, { store, localVue });
    expect(wrapper.contains('#markdown-container')).toBe(true);
  });

  it('renders code in the preview pane for code files', () => {
    state.activeView = { is_markdown: false, file: '{ "title": "Title" }', populated: true };
    const wrapper = mount(Repo, { store, localVue });
    expect(wrapper.contains('#code-container')).toBe(true);
  });
});
