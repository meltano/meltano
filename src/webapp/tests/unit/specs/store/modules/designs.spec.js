import designs from '@/store/modules/designs'

describe('designs Vuex store', () => {
  let state

  beforeEach(() => {
    state = {
      activeReport: {},
      design: {
        relatedTable: {}
      },
      hasSQLError: false,
      sqlErrorMessage: [],
      currentModel: '',
      currentDesign: '',
      results: [],
      queryAttributes: [],
      resultAggregates: [],
      loadingQuery: false,
      currentSQL: '',
      saveReportSettings: { name: null },
      reports: [],
      chartType: 'BarChart',
      limit: 50,
      loader: null,
      filterOptions: [],
      filters: {
        columns: [],
        aggregates: []
      },
      order: {
        assigned: [],
        unassigned: []
      }
    }
  })

  it('has the correct initial state', () => {
    expect(designs.state).toMatchObject(state)
  })
})
