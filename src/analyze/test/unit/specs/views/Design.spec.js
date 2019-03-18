import { mount, createLocalVue, shallowMount } from '@vue/test-utils';
import Vuex from 'vuex';
import VueRouter from 'vue-router';
import Design from '@/views/Design';
import designs from '@/store/modules/designs';

const localVue = createLocalVue();
localVue.use(Vuex);
localVue.use(VueRouter);

describe('Design.vue', () => {
  let actions;
  let state;
  let router;
  let store;

  beforeEach(() => {
    state = designs.state;
    actions = {
      getDesign: jest.fn(),
      loadReport: jest.fn(),
      saveReport: jest.fn(),
    };
    router = new VueRouter();
    store = new Vuex.Store({
      modules: {
        designs: {
          namespaced: true,
          state,
          actions,
          getters: designs.getters,
        },
      },
    });
  });

  it('calls getDesign() via created() lifecycle hook', () => {
    const wrapper = shallowMount(Design, { store, localVue, router });

    expect(wrapper.html()).toBeTruthy();
    expect(actions.getDesign).toHaveBeenCalled();
  });

  it('Renders no selections, chart, SQL, or results by default', () => {
    const wrapper = mount(Design, { store, localVue, router });

    expect(wrapper.element).toMatchSnapshot();
  });
});
