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
      limit: 50,
      distincts: {},
      sortColumn: null,
      sortDesc: false,
      dialect: null,
    };
  });

  it('has the correct initial state', () => {
    expect(designs.state).toMatchObject(state);
  });

  it('selection/deselection of aggregates properly validates/invalidates order value', () => {
    // eslint-disable-next-line
    state = { activeReport: {}, design: { description: 'Region Carbon Intensity Data', from: 'region', graph: { directed: true, graph: {}, links: [{ source: 'region', target: 'entry' }, { source: 'entry', target: 'generationmix' }], multigraph: false, nodes: [{ id: 'region' }, { id: 'entry' }, { id: 'generationmix' }] }, joins: [{ label: 'Entry', name: 'entry', related_table: { columns: [{ hidden: 'yes', label: 'ID', name: 'id', primary_key: 'yes', sql: '{{TABLE}}.id', type: 'string' }, { hidden: 'yes', label: 'Region ID', name: 'region_id', sql: '{{TABLE}}.region_id', type: 'string' }, { label: 'Forecast', name: 'forecast', sql: '{{TABLE}}.forecast', type: 'number' }], name: 'entry', sql_table_name: 'entry', timeframes: [{ description: 'Selected from range in carbon data', label: 'From', name: 'from', periods: [{ label: 'Quarter', name: 'quarter', part: 'QUARTER' }, { label: 'Week', name: 'week', part: 'WEEK' }, { label: 'Month', name: 'month', part: 'MONTH' }, { label: 'Year', name: 'year', part: 'YEAR' }], sql: '{{TABLE}}.from', type: 'time' }, { description: 'Selected to range in carbon data', label: 'To', name: 'to', periods: [{ label: 'Quarter', name: 'quarter', part: 'QUARTER' }, { label: 'Week', name: 'week', part: 'WEEK' }, { label: 'Month', name: 'month', part: 'MONTH' }, { label: 'Year', name: 'year', part: 'YEAR' }], sql: '{{TABLE}}.to', type: 'time' }], version: 1 }, relationship: 'many_to_one', sql_on: 'region.id = entry.region_id' }, { label: 'Generation Mix', name: 'generationmix', related_table: { aggregates: [{ description: 'Average Percent (%)', label: 'Average Percent (%)', name: 'avg_perc', sql: '{{table}}.perc', type: 'avg' }], columns: [{ label: 'ID', name: 'id', primary_key: 'yes', sql: '{{table}}.id', type: 'string' }, { label: 'Entry ID', name: 'entry_id', sql: '{{table}}.entry_id', type: 'string' }, { label: 'Fuel Type', name: 'fuel', sql: '{{table}}.fuel', type: 'string' }, { label: 'Percent (%)', name: 'perc', sql: '{{table}}.perc', type: 'number' }], name: 'generationmix', sql_table_name: 'generationmix', version: 1 }, relationship: 'many_to_one', sql_on: 'entry.id = generationmix.entry_id' }], label: 'Region', name: 'region', related_table: { aggregates: [{ description: 'Runner Count', label: 'Count', name: 'count', sql: '{{table}}.id', type: 'count', selected: true }], columns: [{ hidden: true, name: 'id', primary_key: true, sql: '{{table}}.id', type: 'string' }, { description: 'Carbon region long name', label: 'Name', name: 'name', sql: '{{table}}.dnoregion', type: 'string', selected: true }, { description: 'Carbon region short name', label: 'Short Name', name: 'short_name', sql: '{{table}}.shortname', type: 'string', selected: true }], name: 'region', sql_table_name: 'region', version: 1 } }, hasSQLError: false, sqlErrorMessage: [], currentModel: 'carbon', currentDesign: 'region', results: [{ 'region.count': 1, 'region.dnoregion': 'Electricity North West', 'region.shortname': 'North West England' }, { 'region.count': 1, 'region.dnoregion': 'England', 'region.shortname': 'England' }, { 'region.count': 1, 'region.dnoregion': 'NPG North East', 'region.shortname': 'North East England' }], keys: ['region.dnoregion', 'region.shortname', 'region.count'], columnHeaders: ['Name', 'Short Name', 'Count'], columnNames: ['name', 'short_name', 'count'], resultAggregates: ['region.count'], loadingQuery: true, currentDataTab: 'results', currentSQL: 'SELECT "region"."dnoregion" "region.dnoregion","region"."shortname" "region.shortname",COALESCE(COUNT("region"."id"),0) "region.count" FROM "region" "region" GROUP BY "region.dnoregion","region.shortname" ORDER BY "region.count" ASC LIMIT 3;', filtersOpen: false, dataOpen: true, chartsOpen: false, saveReportSettings: { name: null }, reports: [{ chartType: 'BarChart', createdAt: 1552937196.941, design: 'region', id: 'F5KXGZLSOMXWI23ON54C2Z3JORWGCYRPIRXWG5LNMVXHI4ZPKBZG62TFMN2HGL3DMFZGE33OF5WW6ZDFNQXXEZLQN5ZHILJRFV2GK43UFZZGK4DPOJ2C43JVN4======', model: 'carbon', name: 'Report 1 Test', path: '/Users/dknox-gitlab/Documents/Projects/carbon/model/report-1-test.report.m5o', queryPayload: { aggregates: ['count'], columns: [], filters: {}, joins: [{ aggregates: [], columns: [], name: 'entry', timeframes: [] }, { aggregates: [], columns: [], name: 'generationmix' }], limit: 3, order: null, table: 'region', timeframes: [] }, slug: 'report-1-test', version: '1.0.0' }], chartType: 'BarChart', limit: 3, distincts: {}, sortColumn: 'count', sortDesc: false, dialect: 'sqlite' };
    designs.state.design = state.design;
    designs.state.sortColumn = state.sortColumn;
    const queryPayloadAggregateSelected = designs.helpers.getQueryPayloadFromDesign();

    expect(queryPayloadAggregateSelected.order).toEqual({ column: 'count', direction: 'asc' });

    designs.state.design.related_table.aggregates[0].selected = false;
    const queryPayloadAggregateDeselected = designs.helpers.getQueryPayloadFromDesign();

    expect(queryPayloadAggregateDeselected.order).toBeNull();
  });
});
