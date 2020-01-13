<script>
import { mapActions, mapGetters, mapState } from 'vuex'

import Dropdown from '@/components/generic/Dropdown'
import LoadingOverlay from '@/components/generic/LoadingOverlay'
import QuerySortBy from '@/components/analyze/QuerySortBy'
import { selected } from '@/utils/predicates'

export default {
  name: 'ResultTable',
  components: {
    Dropdown,
    LoadingOverlay,
    QuerySortBy
  },
  props: {
    isLoading: { type: Boolean, required: true, default: false }
  },
  computed: {
    ...mapState('designs', [
      'queryAttributes',
      'results',
      'resultAggregates',
      'order'
    ]),
    ...mapGetters('designs', [
      'getAttributes',
      'getFormattedValue',
      'hasResults',
      'isColumnSelectedAggregate'
    ]),
    getAssignedOrderable() {
      return attributeName =>
        this.order.assigned.find(
          orderable => orderable.attribute.name === attributeName
        )
    },
    getHasMinimalSelectionRequirements() {
      const hasColumn = this.getAttributes(['columns']).find(selected)
      const hasAggregate = this.getAttributes(['aggregates']).find(selected)
      return hasColumn || hasAggregate
    },
    getIsOrderableAssigned() {
      return attributeName => Boolean(this.getAssignedOrderable(attributeName))
    },
    getOrderables() {
      return this.order.unassigned.concat(this.order.assigned)
    },
    getOrderableStatusLabel() {
      return queryAttribute => {
        const match = this.getAssignedOrderable(queryAttribute.attributeName)
        const idx = this.order.assigned.indexOf(match)
        return match ? `${idx + 1}. ${match.direction}` : ''
      }
    },
    keys() {
      return this.queryAttributes.map(attr => attr.key)
    }
  },
  methods: {
    ...mapActions('designs', ['updateSortAttribute'])
  }
}
</script>

<template>
  <div class="result-data has-position-relative v-min-2r">
    <LoadingOverlay :is-loading="isLoading"></LoadingOverlay>

    <div v-if="hasResults">
      <table
        class="table
          is-bordered
          is-striped
          is-narrow
          is-hoverable
          is-fullwidth
          is-size-7"
      >
        <thead>
          <tr>
            <th
              v-for="(queryAttribute, idx) in queryAttributes"
              :key="
                `${queryAttribute.sourceName}-${
                  queryAttribute.attributeName
                }-${idx}`
              "
            >
              <div class="is-flex">
                <div
                  class="sort-header"
                  @click="updateSortAttribute(queryAttribute)"
                >
                  <span>{{ queryAttribute.attributeLabel }}</span>
                </div>
                <Dropdown
                  ref="order-dropdown"
                  :label="getOrderableStatusLabel(queryAttribute)"
                  :button-classes="
                    `is-small ${
                      getIsOrderableAssigned(queryAttribute.attributeName)
                        ? 'has-text-interactive-secondary'
                        : ''
                    }`
                  "
                  :menu-classes="'dropdown-menu-300'"
                  icon-open="sort"
                  icon-close="caret-down"
                  is-right-aligned
                  is-up
                >
                  <div class="dropdown-content is-unselectable">
                    <QuerySortBy></QuerySortBy>
                  </div>
                </Dropdown>
              </div>
            </th>
          </tr>
        </thead>
        <tbody>
          <!-- eslint-disable-next-line vue/require-v-for-key -->
          <tr v-for="(result, i) in results" :key="i">
            <template v-for="key in keys">
              <td v-if="isColumnSelectedAggregate(key)" :key="key">
                {{
                  getFormattedValue(
                    resultAggregates[key]['value_format'],
                    result[key]
                  )
                }}
              </td>
              <td v-else :key="key">
                {{ result[key] }}
              </td>
            </template>
          </tr>
        </tbody>
      </table>
    </div>

    <article
      v-else-if="!getHasMinimalSelectionRequirements"
      class="message is-info"
    >
      <div class="message-body">
        <div class="content">
          <p>To display a <em>Table</em>:</p>
          <ol>
            <li>
              Select at least one <strong>Column</strong> or
              <strong>Aggregate</strong> from the <em>Attributes</em> panel
            </li>
            <li>
              Manually click the <em>Run</em> button (if
              <em>Autorun Queries</em> is toggled off)
            </li>
          </ol>
        </div>
      </div>
    </article>
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
    content: 'asc';
    position: relative;
    width: 22px;
    height: 20px;
    float: right;
    font-size: 9px;
    padding: 2px;
    color: $grey-light;
    border: 1px solid $grey-light;
    border-radius: 4px;
    margin-top: 2px;
  }
  &.is-desc {
    &::after {
      content: 'desc';
      width: 28px;
    }
  }
}
</style>
