<script>
import { mapActions, mapGetters, mapState } from 'vuex'
import _ from 'lodash'

export default {
  name: 'QueryFilters',
  data() {
    return {
      addFilterModel: {
        attributeHelper: {
          attribute: null,
          type: '',
          sourceName: ''
        },
        expression: '',
        value: '',
        isActive: true
      }
    }
  },
  computed: {
    ...mapState('designs', ['filterOptions', 'filters']),
    ...mapGetters('designs', ['getFilterAttributes', 'hasFilters']),
    getFlattenedFilters() {
      return this.hasFilters
        ? _.sortBy(this.filters.columns.concat(this.filters.aggregates), 'name')
        : []
    },
    getFilterInputType() {
      return filterType => (filterType === 'aggregate' ? 'number' : 'text')
    },
    getHasValidatedOptionals() {
      return (expression, value) =>
        this.getIsExpressionNullRelated(expression) || Boolean(value)
    },
    getIsExpressionNullRelated() {
      return expression =>
        expression === 'is_null' || expression === 'is_not_null'
    },
    getIsFilterValid() {
      return filter =>
        this.getHasValidatedOptionals(filter.expression, filter.value)
    },
    isFirstFilterMatch() {
      return filter => {
        const match = this.getFlattenedFilters.find(
          tempFilter =>
            tempFilter.sourceName === filter.sourceName &&
            tempFilter.name === filter.name
        )
        return match === filter
      }
    },
    isValidAdd() {
      const vm = this.addFilterModel
      const hasRequiredValues =
        vm.attributeHelper.attribute &&
        vm.attributeHelper.sourceName &&
        vm.expression
      const hasValidatedOptionals = this.getHasValidatedOptionals(
        vm.expression,
        vm.value
      )
      return hasRequiredValues && hasValidatedOptionals
    }
  },
  methods: {
    ...mapActions('designs', ['removeFilter']),
    addFilter() {
      const vm = this.addFilterModel
      this.$store.dispatch('designs/addFilter', {
        sourceName: vm.attributeHelper.sourceName,
        attribute: vm.attributeHelper.attribute,
        filterType: vm.attributeHelper.type,
        expression: vm.expression,
        value: vm.value,
        isActive: vm.isActive
      })
      this.selectivelyClearAddFilterModel()
    },
    onChangeExpressionSelector(filter) {
      const isNullRelated = this.getIsExpressionNullRelated(filter.expression)
      if (isNullRelated) {
        filter.value = ''
      }
    },
    onChangeFilterValue(filter) {
      const hasValidatedOptionals = this.getHasValidatedOptionals(
        filter.expression,
        filter.value
      )
      filter.isActive = hasValidatedOptionals
    },
    selectivelyClearAddFilterModel() {
      this.addFilterModel.value = ''
    }
  }
}
</script>

<template>
  <div>
    <table class="table is-size-7 is-fullwidth is-narrow is-hoverable">
      <thead>
        <tr>
          <th>
            <span>Attribute</span>
            <span
              class="icon has-text-grey-light tooltip is-tooltip-right"
              data-tooltip="The column or aggregate to filter."
            >
              <font-awesome-icon icon="info-circle"></font-awesome-icon>
            </span>
          </th>
          <th class="has-text-centered">
            <span>Operation</span>
            <span
              class="icon has-text-grey-light tooltip"
              data-tooltip="The filter expression for the selected column or aggregate."
            >
              <font-awesome-icon icon="info-circle"></font-awesome-icon>
            </span>
          </th>
          <th class="has-text-centered">
            <span>Value</span>
            <span
              class="icon has-text-grey-light tooltip"
              data-tooltip="The value to operate on when filtering."
            >
              <font-awesome-icon icon="info-circle"></font-awesome-icon>
            </span>
          </th>
          <th class="has-text-right">
            <span>Actions</span>
          </th>
        </tr>
      </thead>

      <tbody>
        <tr>
          <td>
            <p class="control is-expanded">
              <span class="select is-fullwidth is-small">
                <select v-model="addFilterModel.attributeHelper">
                  <optgroup
                    v-for="attribute in getFilterAttributes"
                    :key="attribute.tableLabel"
                    :label="attribute.tableLabel"
                  >
                    <option disabled>Columns</option>
                    <option
                      v-for="column in attribute.columns"
                      :key="column.label"
                      :value="{
                        attribute: column,
                        sourceName: attribute.sourceName,
                        type: 'column'
                      }"
                    >
                      {{ column.label }}
                    </option>
                    <option disabled>Aggregates</option>
                    <option
                      v-for="aggregate in attribute.aggregates"
                      :key="aggregate.label"
                      :value="{
                        attribute: aggregate,
                        sourceName: attribute.sourceName,
                        type: 'aggregate'
                      }"
                    >
                      {{ aggregate.label }}
                    </option>
                  </optgroup>
                </select>
              </span>
            </p>
          </td>
          <td>
            <p class="control is-expanded">
              <span class="select is-fullwidth is-small">
                <select
                  v-model="addFilterModel.expression"
                  @change="onChangeExpressionSelector(addFilterModel)"
                >
                  <option
                    v-for="filterOption in filterOptions"
                    :key="filterOption.label"
                    :value="filterOption.expression"
                    >{{ filterOption.label }}</option
                  >
                </select>
              </span>
            </p>
          </td>
          <td>
            <p class="control is-expanded">
              <input
                class="input is-small"
                :disabled="
                  getIsExpressionNullRelated(addFilterModel.expression)
                "
                :type="getFilterInputType(addFilterModel.attributeHelper.type)"
                @focus="$event.target.select()"
                v-model="addFilterModel.value"
                placeholder="Filter value"
              />
            </p>
          </td>
          <td>
            <div class="control">
              <button
                class="button is-small is-fullwidth is-interactive-primary is-outlined"
                :disabled="!isValidAdd"
                @click="addFilter"
              >
                Add
              </button>
            </div>
          </td>
        </tr>

        <template v-if="hasFilters">
          <br />

          <tr
            v-for="(filter, index) in getFlattenedFilters"
            :key="`${filter.sourceName}-${filter.name}-${index}`"
          >
            <td>
              <p class="is-small">
                <span v-if="isFirstFilterMatch(filter)">
                  {{ filter.attribute.label }}
                </span>
              </p>
            </td>
            <td>
              <p class="control is-expanded">
                <span class="select is-fullwidth is-small">
                  <select
                    v-model="filter.expression"
                    @change="onChangeExpressionSelector(filter)"
                  >
                    <option
                      v-for="filterOption in filterOptions"
                      :key="filterOption.label"
                      :value="filterOption.expression"
                      >{{ filterOption.label }}</option
                    >
                  </select>
                </span>
              </p>
            </td>
            <td>
              <p class="control has-icons-right is-expanded">
                <input
                  class="input is-small"
                  :class="{ 'is-danger': !getIsFilterValid(filter) }"
                  :disabled="getIsExpressionNullRelated(filter.expression)"
                  :type="getFilterInputType(filter.filterType)"
                  @focus="$event.target.select()"
                  @input="onChangeFilterValue(filter)"
                  v-model="filter.value"
                  :placeholder="
                    getIsFilterValid(filter) ? 'Filter value' : 'Invalid value'
                  "
                />
                <span class="icon is-small is-right">
                  <font-awesome-icon
                    :icon="
                      getIsFilterValid(filter)
                        ? 'check'
                        : 'exclamation-triangle'
                    "
                  ></font-awesome-icon>
                </span>
              </p>
            </td>
            <td>
              <div class="control">
                <button
                  class="button is-small is-fullwidth"
                  @click.stop="removeFilter(filter)"
                >
                  Remove
                </button>
              </div>
            </td>
          </tr>
        </template>
      </tbody>
    </table>
  </div>
</template>

<style lang="scss"></style>
