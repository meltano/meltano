<template>
    <div class="result-data" v-if="isResultsTab">
      <div class="notification is-info" v-if="!hasResults">
        No results
      </div>
      <table class="table
          is-bordered
          is-striped
          is-narrow
          is-hoverable
          is-fullwidth"
          v-if="hasResults">
        <thead>
          <th v-for="(columnHeader, i) in columnHeaders"
              class="sortable-header"
              :key="columnHeader + i"
              :class="{
                'has-background-warning': isColumnSelectedAggregate(keys[i]),
                'has-background-white-ter sorted': isColumnSorted(names[i]),
                'is-desc': sortDesc,
              }"
              @click="sortBy(names[i])">
            {{columnHeader}}
          </th>
        </thead>
        <tbody>
          <!-- eslint-disable-next-line vue/require-v-for-key -->
          <tr v-for="result in results">
            <template v-for="key in keys">
            <td :key="key" v-if="isColumnSelectedAggregate(key)">
              {{getFormattedValue(resultAggregates[key]['value_format'], result[key])}}
            </td>
            <td :key="key" v-else>
              {{result[key]}}
            </td>
            </template>
          </tr>
        </tbody>
      </table>
    </div>
</template>
<script>
import { mapState, mapGetters, mapActions } from 'vuex';

export default {
  name: 'ResultTable',
  computed: {
    ...mapState('designs', [
      'resultAggregates',
      'columnHeaders',
      'names',
      'results',
      'keys',
      'sortDesc',
    ]),
    ...mapGetters('designs', [
      'hasResults',
      'isColumnSorted',
      'getFormattedValue',
      'isColumnSelectedAggregate',
      'isResultsTab',
    ]),
  },

  methods: {
    ...mapActions('designs', [
      'sortBy',
    ]),
  },
};
</script>
<style lang="scss">
.sortable-header {
  cursor: pointer;
}
.result-data {
  width: 100%;
  overflow-x: auto;
  table {
    width: 100%;
    max-width: 100%;
  }
}
.sorted {
  &::after {
    content: "asc";
    position: relative;
    width: 22px;
    height: 20px;
    float: right;
    font-size: 9px;
    padding: 2px;
    color: #AAA;
    border: 1px solid #AAA;
    border-radius: 4px;
    margin-top: 2px;
  }
  &.is-desc {
    &::after {
      content: "desc";
      width: 28px;
    }
  }
}
</style>
