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
    state = Object.assign(Design.data(), designs.state);
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

  it('no selections, chart, SQL, or results where the Save, Load, and Run Query buttons are disabled by default', () => {
    const wrapper = mount(Design, { store, localVue, router });

    expect(wrapper.element).toMatchSnapshot();
  });

  it('Run Query button enabled and SQL tab focused and displayed if selection(s) are made', () => {
    state.currentSQL = 'SELECT COALESCE(COUNT("region"."id"),0) "region.count" FROM "region" "region" LIMIT 3;';
    const wrapper = mount(Design, { store, localVue, router });

    expect(wrapper.element).toMatchSnapshot();
  });

  it('Save report button enabled if query has ran', () => {
    state.currentSQL = 'SELECT COALESCE(COUNT("region"."id"),0) "region.count" FROM "region" "region" LIMIT 3;';
    state.resultAggregates = ['region.count'];
    state.results = [{ 'region.count': 17 }];
    const wrapper = mount(Design, { store, localVue, router });

    expect(wrapper.element).toMatchSnapshot();
  });
});
