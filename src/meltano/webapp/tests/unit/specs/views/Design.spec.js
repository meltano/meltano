import { createLocalVue, mount, shallowMount } from '@vue/test-utils'
import Vuex from 'vuex'
import VueRouter from 'vue-router'
import Design from '@/components/analyze/Design'
import designs from '@/store/modules/designs'
import plugins from '@/store/modules/plugins'
import router from '@/router'

const localVue = createLocalVue()
localVue.use(Vuex)
localVue.use(VueRouter)

describe('Design.vue', () => {
  let actions
  let state
  let store

  const createShallowWrapper = (use) =>
    shallowMount(Design, {
      store,
      localVue,
      router,
      ...use,
    })

  const createWrapper = (use) =>
    mount(Design, {
      stubs: ['font-awesome-icon'],
      store,
      localVue,
      router,
      ...use,
      $route: { params: 'test' },
    })

  beforeEach(() => {
    state = Object.assign(Design.data(), designs.state)
    actions = {
      getDesign: jest.fn(),
      getSQL: jest.fn(),
      loadReport: jest.fn(),
      saveReport: jest.fn(),
    }
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
    })
  })

  it('calls getDesign() via beforeRouteEnter() router lifecycle hook', () => {
    const params = {
      model: 'model',
      design: 'design',
    }
    const wrapper = createShallowWrapper()

    router.push({ name: 'analyze_design', params })

    wrapper.vm.$nextTick(() => {
      expect(wrapper.html()).toBeTruthy()
      expect(wrapper.vm.$route.params).toEqual(params)
      expect(actions.getDesign).toHaveBeenCalled()
    })
  })

  it('no selections, chart, SQL, or results where the Save, Load, and Run Query buttons are disabled by default', () => {
    const wrapper = createWrapper()

    expect(wrapper.element).toMatchSnapshot()
  })

  it('Run Query button enabled and SQL tab focused and displayed if selection(s) are made', () => {
    state.currentSQL =
      'SELECT COALESCE(COUNT("region"."id"),0) "region.count" FROM "region" "region" LIMIT 3;'
    const wrapper = createWrapper()

    expect(wrapper.element).toMatchSnapshot()
  })

  it('Save report button enabled if query has ran', () => {
    state.currentSQL =
      'SELECT COALESCE(COUNT("region"."id"),0) "region.count" FROM "region" "region" LIMIT 3;'
    state.resultAggregates = ['region.count']
    state.results = [{ 'region.count': 17 }]
    const wrapper = createShallowWrapper()

    expect(wrapper.element).toMatchSnapshot()
  })

  it('Load report button enabled if reports exist', () => {
    // eslint-disable-next-line
    const report = { "activeReport": { "chartType": "BarChart", "createdAt": 1563207377.535716, "design": "region", "id": "F5KXGZLSOMXWI23ON54C2Z3JORWGCYRPIRXWG5LNMVXHI4ZPKBZG62TFMN2HGL3HNF2GYYLCF5WW6ZDFNQXXIZLTOQXHEZLQN5ZHILTNGVXQ====", "model": "carbon", "name": "test", "path": "/Users/dknox-gitlab/Documents/Projects/gitlab/model/test.report.m5o", "queryPayload": { "aggregates": ["count"], "columns": ["name"], "filters": { "aggregates": [], "columns": [] }, "joins": [{ "aggregates": [], "columns": [], "name": "entry", "timeframes": [] }, { "aggregates": [], "columns": [], "name": "generationmix" }], "limit": "3", "order": null, "table": "region", "timeframes": [] }, "slug": "test", "version": "1.0.0" }, "design": { "description": "Region Carbon Intensity Data", "from": "region", "graph": { "directed": true, "graph": {}, "links": [{ "source": "region", "target": "entry" }, { "source": "entry", "target": "generationmix" }], "multigraph": false, "nodes": [{ "id": "region" }, { "id": "entry" }, { "id": "generationmix" }] }, "joins": [{ "label": "Entry", "name": "entry", "relatedTable": { "columns": [{ "hidden": "yes", "label": "ID", "name": "id", "primaryKey": "yes", "sql": "{{TABLE}}.id", "type": "string", "selected": false }, { "hidden": "yes", "label": "Region ID", "name": "region_id", "sql": "{{TABLE}}.region_id", "type": "string", "selected": false }, { "label": "Forecast", "name": "forecast", "sql": "{{TABLE}}.forecast", "type": "number", "selected": false }], "name": "entry", "sqlTableName": "entry", "timeframes": [{ "description": "Selected from range in carbon data", "label": "From", "name": "from", "periods": [{ "label": "Quarter", "name": "quarter", "part": "QUARTER" }, { "label": "Week", "name": "week", "part": "WEEK" }, { "label": "Month", "name": "month", "part": "MONTH" }, { "label": "Year", "name": "year", "part": "YEAR" }], "sql": "{{TABLE}}.from", "type": "time", "selected": false }, { "description": "Selected to range in carbon data", "label": "To", "name": "to", "periods": [{ "label": "Quarter", "name": "quarter", "part": "QUARTER" }, { "label": "Week", "name": "week", "part": "WEEK" }, { "label": "Month", "name": "month", "part": "MONTH" }, { "label": "Year", "name": "year", "part": "YEAR" }], "sql": "{{TABLE}}.to", "type": "time", "selected": false }], "version": 1 }, "relationship": "many_to_one", "sql_on": "region.id = entry.region_id", "collapsed": true }, { "label": "Generation Mix", "name": "generationmix", "relatedTable": { "aggregates": [{ "description": "Average Percent (%)", "label": "Average Percent (%)", "name": "avg_perc", "sql": "{{table}}.perc", "type": "avg", "selected": false }], "columns": [{ "label": "ID", "name": "id", "primaryKey": "yes", "sql": "{{table}}.id", "type": "string", "selected": false }, { "label": "Entry ID", "name": "entry_id", "sql": "{{table}}.entry_id", "type": "string", "selected": false }, { "label": "Fuel Type", "name": "fuel", "sql": "{{table}}.fuel", "type": "string", "selected": false }, { "label": "Percent (%)", "name": "perc", "sql": "{{table}}.perc", "type": "number", "selected": false }], "name": "generationmix", "sqlTableName": "generationmix", "version": 1 }, "relationship": "many_to_one", "sql_on": "entry.id = generationmix.entry_id" }], "label": "Region", "name": "region", "relatedTable": { "aggregates": [{ "description": "Runner Count", "label": "Count", "name": "count", "sql": "{{table}}.id", "type": "count", "selected": true }], "columns": [{ "hidden": true, "name": "id", "primaryKey": true, "sql": "{{table}}.id", "type": "string", "selected": false }, { "description": "Carbon region long name", "label": "Name", "name": "name", "sql": "{{table}}.dnoregion", "type": "string", "selected": true }, { "description": "Carbon region short name", "label": "Short Name", "name": "short_name", "sql": "{{table}}.shortname", "type": "string", "selected": false }], "name": "region", "sqlTableName": "region", "version": 1 } }, "hasSQLError": false, "sqlErrorMessage": [], "currentModel": "carbon", "currentDesign": "region", "results": [{ "region.count": 1, "region.dnoregion": "Electricity North West" }, { "region.count": 1, "region.dnoregion": "England" }, { "region.count": 1, "region.dnoregion": "NPG North East" }], "keys": ["region.dnoregion", "region.count"], "columnHeaders": ["Name", "Count"], "columnNames": ["name", "count"], "resultAggregates": ["region.count"], "loadingQuery": false, "currentSQL": "SELECT \"region\".\"dnoregion\" \"region.dnoregion\",COALESCE(COUNT(\"region\".\"id\"),0) \"region.count\" FROM \"region\" \"region\" GROUP BY \"region.dnoregion\" ORDER BY \"region.dnoregion\" ASC LIMIT 3;", "saveReportSettings": { "name": null }, "reports": [{ "chartType": "BarChart", "createdAt": 1563207377.535716, "design": "region", "id": "F5KXGZLSOMXWI23ON54C2Z3JORWGCYRPIRXWG5LNMVXHI4ZPKBZG62TFMN2HGL3HNF2GYYLCF5WW6ZDFNQXXIZLTOQXHEZLQN5ZHILTNGVXQ====", "model": "carbon", "name": "test", "path": "/Users/dknox-gitlab/Documents/Projects/gitlab/model/test.report.m5o", "queryPayload": { "aggregates": ["count"], "columns": ["name"], "filters": { "aggregates": [], "columns": [] }, "joins": [{ "aggregates": [], "columns": [], "name": "entry", "timeframes": [] }, { "aggregates": [], "columns": [], "name": "generationmix" }], "limit": "3", "order": null, "table": "region", "timeframes": [] }, "slug": "test", "version": "1.0.0" }], "chartType": "BarChart", "limit": "3", "sortColumn": null, "sortDesc": false, "dialect": "sqlite", "selectedAttributeCount": 0, "filterOptions": [{ "description": "Less than", "expression": "less_than", "label": "Less than" }, { "description": "Less than or equal", "expression": "less_or_equal_than", "label": "Less than or equal" }, { "description": "Equal to", "expression": "equal_to", "label": "Equal to" }, { "description": "Greater than or equal", "expression": "greater_or_equal_than", "label": "Greater than or equal" }, { "description": "Greater than", "expression": "greater_than", "label": "Greater than" }, { "description": "Custom like expression", "expression": "like", "label": "Like" }, { "description": "Is null", "expression": "is_null", "label": "Is Null" }, { "description": "Is not null", "expression": "is_not_null", "label": "Is Not Null" }], "filters": { "columns": [], "aggregates": [] } };
    state.reports = [report]
    const wrapper = createWrapper()

    expect(wrapper.element).toMatchSnapshot()
  })

  it('a loaded report renders report name, selections, chart, SQL, and results where the Save, Load, and Run Query buttons are enabled', () => {
    // eslint-disable-next-line
    const report = { "activeReport": { "chartType": "BarChart", "createdAt": 1563207377.535716, "design": "region", "id": "F5KXGZLSOMXWI23ON54C2Z3JORWGCYRPIRXWG5LNMVXHI4ZPKBZG62TFMN2HGL3HNF2GYYLCF5WW6ZDFNQXXIZLTOQXHEZLQN5ZHILTNGVXQ====", "model": "carbon", "name": "test", "path": "/Users/dknox-gitlab/Documents/Projects/gitlab/model/test.report.m5o", "queryPayload": { "aggregates": ["count"], "columns": ["name"], "filters": { "aggregates": [], "columns": [] }, "joins": [{ "aggregates": [], "columns": [], "name": "entry", "timeframes": [] }, { "aggregates": [], "columns": [], "name": "generationmix" }], "limit": "3", "order": null, "table": "region", "timeframes": [] }, "slug": "test", "version": "1.0.0" }, "design": { "description": "Region Carbon Intensity Data", "from": "region", "graph": { "directed": true, "graph": {}, "links": [{ "source": "region", "target": "entry" }, { "source": "entry", "target": "generationmix" }], "multigraph": false, "nodes": [{ "id": "region" }, { "id": "entry" }, { "id": "generationmix" }] }, "joins": [{ "label": "Entry", "name": "entry", "relatedTable": { "columns": [{ "hidden": "yes", "label": "ID", "name": "id", "primaryKey": "yes", "sql": "{{TABLE}}.id", "type": "string", "selected": false }, { "hidden": "yes", "label": "Region ID", "name": "region_id", "sql": "{{TABLE}}.region_id", "type": "string", "selected": false }, { "label": "Forecast", "name": "forecast", "sql": "{{TABLE}}.forecast", "type": "number", "selected": false }], "name": "entry", "sqlTableName": "entry", "timeframes": [{ "description": "Selected from range in carbon data", "label": "From", "name": "from", "periods": [{ "label": "Quarter", "name": "quarter", "part": "QUARTER" }, { "label": "Week", "name": "week", "part": "WEEK" }, { "label": "Month", "name": "month", "part": "MONTH" }, { "label": "Year", "name": "year", "part": "YEAR" }], "sql": "{{TABLE}}.from", "type": "time", "selected": false }, { "description": "Selected to range in carbon data", "label": "To", "name": "to", "periods": [{ "label": "Quarter", "name": "quarter", "part": "QUARTER" }, { "label": "Week", "name": "week", "part": "WEEK" }, { "label": "Month", "name": "month", "part": "MONTH" }, { "label": "Year", "name": "year", "part": "YEAR" }], "sql": "{{TABLE}}.to", "type": "time", "selected": false }], "version": 1 }, "relationship": "many_to_one", "sql_on": "region.id = entry.region_id", "collapsed": true }, { "label": "Generation Mix", "name": "generationmix", "relatedTable": { "aggregates": [{ "description": "Average Percent (%)", "label": "Average Percent (%)", "name": "avg_perc", "sql": "{{table}}.perc", "type": "avg", "selected": false }], "columns": [{ "label": "ID", "name": "id", "primaryKey": "yes", "sql": "{{table}}.id", "type": "string", "selected": false }, { "label": "Entry ID", "name": "entry_id", "sql": "{{table}}.entry_id", "type": "string", "selected": false }, { "label": "Fuel Type", "name": "fuel", "sql": "{{table}}.fuel", "type": "string", "selected": false }, { "label": "Percent (%)", "name": "perc", "sql": "{{table}}.perc", "type": "number", "selected": false }], "name": "generationmix", "sqlTableName": "generationmix", "version": 1 }, "relationship": "many_to_one", "sql_on": "entry.id = generationmix.entry_id" }], "label": "Region", "name": "region", "relatedTable": { "aggregates": [{ "description": "Runner Count", "label": "Count", "name": "count", "sql": "{{table}}.id", "type": "count", "selected": true }], "columns": [{ "hidden": true, "name": "id", "primaryKey": true, "sql": "{{table}}.id", "type": "string", "selected": false }, { "description": "Carbon region long name", "label": "Name", "name": "name", "sql": "{{table}}.dnoregion", "type": "string", "selected": true }, { "description": "Carbon region short name", "label": "Short Name", "name": "short_name", "sql": "{{table}}.shortname", "type": "string", "selected": false }], "name": "region", "sqlTableName": "region", "version": 1 } }, "hasSQLError": false, "sqlErrorMessage": [], "currentModel": "carbon", "currentDesign": "region", "results": [{ "region.count": 1, "region.dnoregion": "Electricity North West" }, { "region.count": 1, "region.dnoregion": "England" }, { "region.count": 1, "region.dnoregion": "NPG North East" }], "keys": ["region.dnoregion", "region.count"], "columnHeaders": ["Name", "Count"], "columnNames": ["name", "count"], "resultAggregates": ["region.count"], "loadingQuery": false, "currentSQL": "SELECT \"region\".\"dnoregion\" \"region.dnoregion\",COALESCE(COUNT(\"region\".\"id\"),0) \"region.count\" FROM \"region\" \"region\" GROUP BY \"region.dnoregion\" ORDER BY \"region.dnoregion\" ASC LIMIT 3;", "saveReportSettings": { "name": null }, "reports": [{ "chartType": "BarChart", "createdAt": 1563207377.535716, "design": "region", "id": "F5KXGZLSOMXWI23ON54C2Z3JORWGCYRPIRXWG5LNMVXHI4ZPKBZG62TFMN2HGL3HNF2GYYLCF5WW6ZDFNQXXIZLTOQXHEZLQN5ZHILTNGVXQ====", "model": "carbon", "name": "test", "path": "/Users/dknox-gitlab/Documents/Projects/gitlab/model/test.report.m5o", "queryPayload": { "aggregates": ["count"], "columns": ["name"], "filters": { "aggregates": [], "columns": [] }, "joins": [{ "aggregates": [], "columns": [], "name": "entry", "timeframes": [] }, { "aggregates": [], "columns": [], "name": "generationmix" }], "limit": "3", "order": null, "table": "region", "timeframes": [] }, "slug": "test", "version": "1.0.0" }], "chartType": "BarChart", "limit": "3", "sortColumn": null, "sortDesc": false, "dialect": "sqlite", "selectedAttributeCount": 0, "filterOptions": [{ "description": "Less than", "expression": "less_than", "label": "Less than" }, { "description": "Less than or equal", "expression": "less_or_equal_than", "label": "Less than or equal" }, { "description": "Equal to", "expression": "equal_to", "label": "Equal to" }, { "description": "Greater than or equal", "expression": "greater_or_equal_than", "label": "Greater than or equal" }, { "description": "Greater than", "expression": "greater_than", "label": "Greater than" }, { "description": "Custom like expression", "expression": "like", "label": "Like" }, { "description": "Is null", "expression": "is_null", "label": "Is Null" }, { "description": "Is not null", "expression": "is_not_null", "label": "Is Not Null" }], "filters": { "columns": [], "aggregates": [] } };
    state.reports = [report]
    state.chartType = 'BarChart'
    state.keys = ['region.count']
    state.results = [{ 'region.count': 17 }]
    state.resultAggregates = ['region.count']
    const wrapper = createShallowWrapper()

    expect(wrapper.element).toMatchSnapshot()
  })
})
