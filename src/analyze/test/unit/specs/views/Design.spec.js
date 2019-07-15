import { mount, createLocalVue, shallowMount } from '@vue/test-utils';
import Vuex from 'vuex';
import VueRouter from 'vue-router';
import Design from '@/components/analyze/Design';
import designs from '@/store/modules/designs';
import plugins from '@/store/modules/plugins';
import router from '@/router';

const localVue = createLocalVue();
localVue.use(Vuex);
localVue.use(VueRouter);

describe('Design.vue', () => {
  let actions;
  let state;
  let store;

  const createShallowWrapper = use =>
    shallowMount(Design, {
      store,
      localVue,
      router,
      ...use,
    });

  const createWrapper = use =>
    mount(Design, {
      stubs: ['font-awesome-icon'],
      store,
      localVue,
      router,
      ...use,
      $route: { params: 'test' },
    });

  beforeEach(() => {
    state = Object.assign(Design.data(), designs.state);
    actions = {
      getDesign: jest.fn(),
      getSQL: jest.fn(),
      loadReport: jest.fn(),
      saveReport: jest.fn(),
    };
    store = new Vuex.Store({
      modules: {
        designs: {
          namespaced: true,
          state,
          actions,
          getters: designs.getters,
        },
        plugins,
      },
    });
  });

  it('calls getDesign() via beforeRouteEnter() router lifecycle hook', () => {
    const params = {
      model: 'model',
      design: 'design',
    };
    const wrapper = createShallowWrapper();

    router.push({ name: 'analyze_design', params });

    wrapper.vm.$nextTick(() => {
      expect(wrapper.html()).toBeTruthy();
      expect(wrapper.vm.$route.params).toEqual(params);
      expect(actions.getDesign).toHaveBeenCalled();
    });
  });

  it('no selections, chart, SQL, or results where the Save, Load, and Run Query buttons are disabled by default', () => {
    const wrapper = createWrapper();

    expect(wrapper.element).toMatchSnapshot();
  });

  it('Run Query button enabled and SQL tab focused and displayed if selection(s) are made', () => {
    state.currentSQL = 'SELECT COALESCE(COUNT("region"."id"),0) "region.count" FROM "region" "region" LIMIT 3;';
    const wrapper = createWrapper();

    expect(wrapper.element).toMatchSnapshot();
  });

  it('Save report button enabled if query has ran', () => {
    state.currentSQL = 'SELECT COALESCE(COUNT("region"."id"),0) "region.count" FROM "region" "region" LIMIT 3;';
    state.resultAggregates = ['region.count'];
    state.results = [{ 'region.count': 17 }];
    const wrapper = createWrapper();

    expect(wrapper.element).toMatchSnapshot();
  });

  it('Load report button enabled if reports exist', () => {
    // eslint-disable-next-line
    state.reports = [{name: "test", model: "carbon", design: "region", chartType: "BarChart", queryPayload: {table: "region", columns: ["name"], aggregates: ["count"], timeframes: [], joins: [{name: "entry", columns: [], aggregates: [], timeframes: []}, {name: "generationmix", columns: [], aggregates: []}], order: null, limit: "3", filters: {columns: [], aggregates: []}}, path: "/Users/dknox-gitlab/Documents/Projects/gitlab/model/test.report.m5o", id: "F5KXGZLSOMXWI23ON54C2Z3JORWGCYRPIRXWG5LNMVXHI4ZPKBZG62TFMN2HGL3HNF2GYYLCF5WW6ZDFNQXWGLTSMVYG64TUFZWTK3Y=", slug: "test", createdAt: 1563204808.6965702, version: "1.0.0"}];
    const wrapper = createWrapper();

    expect(wrapper.element).toMatchSnapshot();
  });

  it('a loaded report renders report name, selections, chart, SQL, and results where the Save, Load, and Run Query buttons are enabled', () => {
    // eslint-disable-next-line
    const report = {name: "test", model: "carbon", design: "region", chartType: "BarChart", queryPayload: {table: "region", columns: ["name"], aggregates: ["count"], timeframes: [], joins: [{name: "entry", columns: [], aggregates: [], timeframes: []}, {name: "generationmix", columns: [], aggregates: []}], order: null, limit: "3", filters: {columns: [], aggregates: []}}, path: "/Users/dknox-gitlab/Documents/Projects/gitlab/model/test.report.m5o", id: "F5KXGZLSOMXWI23ON54C2Z3JORWGCYRPIRXWG5LNMVXHI4ZPKBZG62TFMN2HGL3HNF2GYYLCF5WW6ZDFNQXWGLTSMVYG64TUFZWTK3Y=", slug: "test", createdAt: 1563204808.6965702, version: "1.0.0"};
    state.activeReport = report;
    state.chartType = 'BarChart';
    state.currentSQL = 'SELECT COALESCE(COUNT("region"."id"),0) "region.count" FROM "region" "region" LIMIT 3;';
    state.keys = ['region.count'];
    state.reports = [report];
    state.results = [{ 'region.count': 17 }];
    state.resultAggregates = ['region.count'];
    const wrapper = createShallowWrapper();

    expect(wrapper.element).toMatchSnapshot();
  });
});
