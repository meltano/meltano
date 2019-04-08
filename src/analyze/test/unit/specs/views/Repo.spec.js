import { mount, createLocalVue, shallowMount } from '@vue/test-utils';
import Vuex from 'vuex';
import VueRouter from 'vue-router';
import Repo from '@/views/Repo';
import repos from '@/store/modules/repos';

const localVue = createLocalVue();
localVue.use(Vuex);
localVue.use(VueRouter);

describe('Repo.vue', () => {
  let actions;
  let state;
  let router;
  let store;

  beforeEach(() => {
    state = repos.state;
    actions = {
      getRepo: jest.fn(),
      getFile: jest.fn(),
      sync: jest.fn(),
    };
    router = new VueRouter();
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
    const wrapper = shallowMount(Repo, { store, localVue, router });

    expect(wrapper.html()).toBeTruthy();
    expect(actions.getRepo).toHaveBeenCalled();
    expect(actions.sync).toHaveBeenCalled();
  });

  it('renders no code or markdown by default', () => {
    const wrapper = mount(Repo, { store, localVue, router });

    expect(wrapper.element).toMatchSnapshot();
  });

  it('renders markdown in the preview pane for markdown files', () => {
    state.activeView = { is_markdown: true, file: '<h1>Title</h1>', populated: true };
    const wrapper = mount(Repo, { store, localVue, router });

    expect(wrapper.element).toMatchSnapshot();
  });

  it('renders code in the preview pane for code files', () => {
    state.activeView = { is_markdown: false, file: '{ "title": "Title" }', populated: true };
    const wrapper = mount(Repo, { store, localVue, router });

    expect(wrapper.element).toMatchSnapshot();
  });

  it('renders the dashboard list when dashboards exist and calls getFile() when a dashboard is clicked', () => {
    state.files = {
      dashboards: {
        label: 'Dashboards',
        items: [{
          createdAt: 1551459531.431577,
          description: '',
          id: 'F5KXGZLSOMXWI23ON54C2Z3JORWGCYRPIRXWG5LNMVXHI4ZPKBZG62TFMN2HGL3DMFZGE33OFVTWS5DGNRUXQL3NN5SGK3BPMIXGIYLTNBRG6YLSMQXG2NLP',
          name: 'Some',
          path: 'some.dashboard.m5o',
          reportIds: [],
          slug: 'some',
          version: '1.0.0',
        }],
      },
    };
    const wrapper = mount(Repo, { store, localVue, router });

    expect(wrapper.element).toMatchSnapshot();

    wrapper.find('.js-dashboards-some').trigger('click');

    expect(actions.getFile).toHaveBeenCalled();
  });

  it('renders the document list when documents exist and calls getFile() when a document is clicked', () => {
    state.files = {
      documents: {
        label: 'Documents',
        items: [{
          createdAt: 1551990614.693281,
          id: 'F5KXGZLSOMXWI23ON54C2Z3JORWGCYRPIRXWG5LNMVXHI4ZPKBZG62TFMN2HGL3DMFZGE33OFVTWS5DGNRUXQL2SIVAUITKFFZWWI===',
          name: 'README',
          path: 'README.md',
          slug: 'readme-md',
        }],
      },
    };
    const wrapper = mount(Repo, { store, localVue, router });

    expect(wrapper.element).toMatchSnapshot();

    wrapper.find('.js-documents-readme').trigger('click');

    expect(actions.getFile).toHaveBeenCalled();
  });

  it('renders the report list when reports exist and calls getFile() when a report is clicked', () => {
    state.files = {
      reports: {
        label: 'Reports',
        items: [{
          chartType: 'BarChart',
          createdAt: 1551461064.508327,
          design: 'region',
          id: 'F5KXGZLSOMXWI23ON54C2Z3JORWGCYRPIRXWG5LNMVXHI4ZPKBZG62TFMN2HGL3DMFZGE33OFVTWS5DGNRUXQL3NN5SGK3BPMMZC44TFOBXXE5BONU2W6===',
          model: 'carbon',
          name: 'Some',
          path: 'some.report.m5o',
          queryPayload: {},
          slug: 'some',
          version: '1.0.0',
        }],
      },
    };
    const wrapper = mount(Repo, { store, localVue, router });

    expect(wrapper.element).toMatchSnapshot();

    wrapper.find('.js-reports-some').trigger('click');

    expect(actions.getFile).toHaveBeenCalled();
  });

  it('renders the table list when tables exist and calls getFile() when a table is clicked', () => {
    state.files = {
      tables: {
        label: 'Tables',
        items: [{
          createdAt: 1551989728.153954,
          id: 'MVYGS43PMRSXGLTUMFRGYZJONU2W6===',
          name: 'episodes',
          path: 'episodes.table.m5o',
          slug: 'episodes',
        }],
      },
    };
    const wrapper = mount(Repo, { store, localVue, router });

    expect(wrapper.element).toMatchSnapshot();

    wrapper.find('.js-tables-episodes').trigger('click');

    expect(actions.getFile).toHaveBeenCalled();
  });

  it('renders the topic list when topics exist and calls getFile() when a topic is clicked', () => {
    state.files = {
      topics: {
        label: 'Topics',
        items: [{
          version: 1,
          name: 'carbon',
          connection: 'runners_db',
          label: 'carbon intensity',
          designs: {},
        }],
      },
    };
    const wrapper = mount(Repo, { store, localVue, router });

    expect(wrapper.element).toMatchSnapshot();

    wrapper.find('.js-topics-carbon').trigger('click');

    expect(actions.getFile).toHaveBeenCalled();
  });
});
