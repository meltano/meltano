import designs from '@/store/modules/designs'

describe('designs Vuex store', () => {
  let state

  beforeEach(() => {
    state = {
      activeReport: {},
      chartType: 'BarChart',
      currentDesign: '',
      currentModel: '',
      currentNamespace: '',
      currentSQL: '',
      design: {
        relatedTable: {},
      },
      loader: null,
      filterOptions: [],
      filters: {
        aggregates: [],
        columns: [],
      },
      hasSQLError: false,
      isLoadingQuery: false,
      limit: 50,
      order: {
        assigned: [],
        unassigned: [],
      },
      queryAttributes: [],
      reports: [],
      resultAggregates: [],
      results: [],
      saveReportSettings: { name: null },
      sqlErrorMessage: [],
    }
  })

  it('has the correct initial state', () => {
    expect(designs.state).toMatchObject(state)
  })
})
