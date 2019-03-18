import designs from '@/store/modules/designs';

describe('designs Vuex store', () => {
  let state;

  beforeEach(() => {
    state = {
      activeReport: {},
      design: {
        related_table: {},
      },
      hasSQLError: false,
      sqlErrorMessage: [],
      currentModel: '',
      currentDesign: '',
      results: [],
      keys: [],
      columnHeaders: [],
      columnNames: [],
      resultAggregates: {},
      loadingQuery: false,
      currentDataTab: 'sql',
      currentSQL: '',
      filtersOpen: false,
      dataOpen: true,
      chartsOpen: false,
      saveReportSettings: { name: null },
      reports: [],
      chartType: 'BarChart',
      limit: 3,
      distincts: {},
      sortColumn: null,
      sortDesc: false,
      dialect: null,
    };
  });

  it('has the correct initial state', () => {
    expect(designs.state).toMatchObject(state);
  });
});
