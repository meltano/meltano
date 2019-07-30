<script>
import { mapState, mapGetters, mapActions } from 'vuex';

import Dropdown from '@/components/generic/Dropdown';
import QuerySortBy from '@/components/analyze/QuerySortBy';

export default {
  name: 'ResultTable',
  components: {
    Dropdown,
    QuerySortBy,
  },
  computed: {
    ...mapState('designs', [
      'resultAggregates',
      'columnHeaders',
      'columnNames',
      'order',
      'results',
      'keys',
      'sortDesc',
    ]),
    ...mapGetters('designs', [
      'hasResults',
      'isColumnSorted',
      'getFormattedValue',
      'isColumnSelectedAggregate',
    ]),
    getOrderStatusLabel() {
      // TODO ensure tableName and attributeName are used
      return (name) => {
        const match = this.order.assigned.find(orderStatus => orderStatus.attributeName === name);
        const idx = this.order.assigned.indexOf(match);
        return match ? `${idx + 1} ${match.direction}` : '';
      };
    },
  },
  methods: {
    ...mapActions('designs', [
      'sortBy',
    ]),
  },
};
</script>

<template>
  <div class="result-data">

    <div v-if="hasResults">

      <table class="table
          is-bordered
          is-striped
          is-narrow
          is-hoverable
          is-fullwidth
          is-size-7">
        <thead>
          <th v-for="(columnHeader, i) in columnHeaders"
              class="sortable-header"
              :key="columnHeader + i"
              :class="{
                'has-background-warning': isColumnSelectedAggregate(keys[i]),
                'has-background-white-ter sorted': isColumnSorted(columnNames[i]),
                'is-desc': sortDesc,
              }"
            >
            <span>{{columnHeader}}</span>
            <div class='is-pulled-right'>
              <!-- TODO -->
              <Dropdown
                :label="getOrderStatusLabel('name')"
                button-classes="is-small has-text-interactive-secondary"
                icon-open='sort'
                icon-close='caret-down'
                is-right-aligned
                is-up
                ref='order-dropdown'>
                <div class="dropdown-content">
                  <QuerySortBy></QuerySortBy>
                </div>
              </Dropdown>
            </div>
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

    <div class="notification is-italic" v-else>
      No results
    </div>

  </div>
</template>

<style lang="scss">
.sortable-header {
  cursor: pointer;
}
.result-data {
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
