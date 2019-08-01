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
      'order',
      'results',
      'keys',
    ]),
    ...mapGetters('designs', [
      'hasResults',
      'getFormattedValue',
      'isColumnSelectedAggregate',
    ]),
    getAssignedOrderable() {
      return name => this.order.assigned.find(orderable => orderable.attributeName === name);
    },
    getIsOrderableAssigned() {
      return name => Boolean(this.getAssignedOrderable(name));
    },
    getOrderables() {
      return this.order.unassigned.concat(this.order.assigned);
    },
    getOrderableStatusLabel() {
      // TODO ensure sourceName and attributeName are used
      return (name) => {
        const match = this.getAssignedOrderable(name);
        const idx = this.order.assigned.indexOf(match);
        return match ? `${idx + 1} ${match.direction}` : '';
      };
    },
  },
  methods: {
    ...mapActions('designs', [
      'updateSortAttribute',
    ]),
  },
};
</script>

<template>
  <div class="result-data">

    <div v-if="hasResults">

      <ul>
        <li v-for="(orderable, i) in getOrderables" :key="i" @click='updateSortAttribute(orderable)'>
          {{`${orderable.sourceLabel} - ${orderable.attributeLabel} - ${orderable.direction}`}}
        </li>
      </ul>

      <table class="table
          is-bordered
          is-striped
          is-narrow
          is-hoverable
          is-fullwidth
          is-size-7">
        <thead>
          <tr>
            <!-- <th v-for="(columnHeader, i) in columnHeaders"
                :key="columnHeader + i"
                :class="{
                  'has-background-warning': isColumnSelectedAggregate(keys[i]),
                  'has-background-white-ter sorted': isColumnSorted(columnNames[i]),
                  'is-desc': sortDesc,
                }"
              >
              <div class="is-flex">
                <div class='sort-header' @click='updateSortAttribute(columnHeader)'>
                  <span>{{columnHeader}}</span>
                </div>
                <Dropdown
                  :label="getOrderableStatusLabel('name')"
                  :button-classes="`is-small ${getIsOrderableAssigned('name')
                    ? 'has-text-interactive-secondary'
                    : ''}`"
                  icon-open='sort'
                  icon-close='caret-down'
                  is-right-aligned
                  is-up
                  ref='order-dropdown'>
                  <div class="dropdown-content is-unselectable">
                    <QuerySortBy></QuerySortBy>
                  </div>
                </Dropdown>
              </div>
            </th> -->
          </tr>
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
.result-data {
  table {
    width: 100%;
    max-width: 100%;

    .sort-header {
      display: flex;
      align-items: center;
      flex-grow: 1;
      cursor: pointer;
    }
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
