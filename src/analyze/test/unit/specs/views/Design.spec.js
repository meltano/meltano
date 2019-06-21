import { mount, createLocalVue, shallowMount } from '@vue/test-utils';
import Vuex from 'vuex';
import VueRouter from 'vue-router';
import Design from '@/components/analyze/Design';
import designs from '@/store/modules/designs';
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
    state.reports = [{ chartType: 'BarChart', createdAt: 1552937196.941, design: 'region', id: 'F5KXGZLSOMXWI23ON54C2Z3JORWGCYRPIRXWG5LNMVXHI4ZPKBZG62TFMN2HGL3DMFZGE33OF5WW6ZDFNQXXEZLQN5ZHILJRFV2GK43UFZZGK4DPOJ2C43JVN4======', model: 'carbon', name: 'Report 1 Test', path: '/Users/dknox-gitlab/Documents/Projects/carbon/model/report-1-test.report.m5o', queryPayload: { aggregates: ['count'], columns: [], filters: {}, joins: [{ aggregates: [], columns: [], name: 'entry', timeframes: [] }, { aggregates: [], columns: [], name: 'generationmix' }], limit: 3, order: null, table: 'region', timeframes: [] }, slug: 'report-1-test', version: '1.0.0' }];
    const wrapper = createWrapper();

    expect(wrapper.element).toMatchSnapshot();
  });

  it('a loaded report renders report name, selections, chart, SQL, and results where the Save, Load, and Run Query buttons are enabled', () => {
    // eslint-disable-next-line
    const report = { chartType: 'BarChart', createdAt: 1552937196.941, design: 'region', id: 'F5KXGZLSOMXWI23ON54C2Z3JORWGCYRPIRXWG5LNMVXHI4ZPKBZG62TFMN2HGL3DMFZGE33OF5WW6ZDFNQXXEZLQN5ZHILJRFV2GK43UFZZGK4DPOJ2C43JVN4======', model: 'carbon', name: 'Report 1 Test', path: '/Users/dknox-gitlab/Documents/Projects/carbon/model/report-1-test.report.m5o', queryPayload: { aggregates: ['count'], columns: [], filters: {}, joins: [{ aggregates: [], columns: [], name: 'entry', timeframes: [] }, { aggregates: [], columns: [], name: 'generationmix' }], limit: 3, order: null, table: 'region', timeframes: [] }, slug: 'report-1-test', version: '1.0.0' };
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
