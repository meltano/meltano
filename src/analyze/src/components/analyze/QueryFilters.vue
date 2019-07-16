<script>
import { mapActions, mapGetters, mapState } from 'vuex';

import _ from 'lodash';

export default {
  name: 'QueryFilters',
  data() {
    return {
      addFilterModel: {
        attributeHelper: {
          attribute: null,
          type: '',
          table_name: '',
        },
        expression: '',
        value: '',
      },
    };
  },
  computed: {
    ...mapState('designs', [
      'filterOptions',
      'filters',
    ]),
    ...mapGetters('designs', [
      'getAttributesByTable',
      'hasFilters',
    ]),
    getFlattenedFilters() {
      return this.hasFilters
        ? _.sortBy(this.filters.columns.concat(this.filters.aggregates), 'name')
        : [];
    },
    getFilterInputType() {
      return filterType => (filterType === 'aggregate' ? 'number' : 'text');
    },
    isFirstFilterMatch() {
      return (filter) => {
        const match = this.getFlattenedFilters.find(tempFilter => tempFilter.table_name === filter.table_name && tempFilter.name === filter.name);
        return match === filter;
      };
    },
    isValidAdd() {
      const vm = this.addFilterModel;
      return vm.attributeHelper.attribute && vm.attributeHelper.table_name && vm.expression && vm.value;
    },
  },
  methods: {
    ...mapActions('designs', [
      'removeFilter',
    ]),
    addFilter() {
      const vm = this.addFilterModel;
      this.$store.dispatch('designs/addFilter', {
        table_name: vm.attributeHelper.table_name,
        attribute: vm.attributeHelper.attribute,
        filterType: vm.attributeHelper.type,
        expression: vm.expression,
        value: vm.value,
      });
      this.selectivelyClearAddFilterModel();
    },
    selectivelyClearAddFilterModel() {
      this.addFilterModel.value = '';
    },
  },
};
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
              data-tooltip="The column or aggregate to filter.">
              <font-awesome-icon icon="info-circle"></font-awesome-icon>
            </span>
          </th>
          <th class='has-text-centered'>
            <span>Operation</span>
            <span
              class="icon has-text-grey-light tooltip"
              data-tooltip='The filter expression for the selected column or aggregate.'>
              <font-awesome-icon icon="info-circle"></font-awesome-icon>
            </span>
          </th>
          <th class='has-text-centered'>
            <span>Value</span>
            <span
              class="icon has-text-grey-light tooltip"
              data-tooltip='The value to operate on when filtering.'>
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
              <span
                class="select is-fullwidth is-small">
                <select v-model='addFilterModel.attributeHelper'>
                  <optgroup
                    v-for="attributeTable in getAttributesByTable"
                    :key='attributeTable.tableLabel'
                    :label="attributeTable.tableLabel">
                    <option disabled>Columns</option>
                    <option
                      v-for="column in attributeTable.columns"
                      :key='column.label'
                      :value="{
                        attribute: column,
                        table_name: attributeTable.table_name,
                        type: 'column'}">
                      {{column.label}}
                    </option>
                    <option disabled>Aggregates</option>
                    <option
                      v-for="aggregate in attributeTable.aggregates"
                      :key='aggregate.label'
                      :value="{
                        attribute: aggregate,
                        table_name: attributeTable.table_name,
                        type: 'aggregate'}">
                      {{aggregate.label}}
                    </option>
                  </optgroup>
                </select>
              </span>
            </p>
          </td>
          <td>
            <p class="control is-expanded">
              <span
                class="select is-fullwidth is-small">
                <select v-model='addFilterModel.expression'>
                  <option
                    v-for="filterOption in filterOptions"
                    :key='filterOption.label'
                    :value='filterOption.expression'>{{filterOption.label}}</option>
                </select>
              </span>
            </p>
          </td>
          <td>
            <p class="control is-expanded">
              <input
                class="input is-small"
                :type="getFilterInputType(addFilterModel.attributeHelper.type)"
                @focus="$event.target.select()"
                v-model='addFilterModel.value'
                placeholder="Filter value">
            </p>
          </td>
          <td>
            <div class="control">
              <button
                class="button is-small is-fullwidth is-interactive-primary is-outlined"
                :disabled='!isValidAdd'
                @click='addFilter'>
                Add</button>
            </div>
          </td>
        </tr>

        <template v-if='hasFilters'>
          <br>

          <tr
            v-for='(filter, index) in getFlattenedFilters'
            :key='`${filter.table_name}-${filter.name}-${index}`'>
            <td>
              <p class="is-small">
                <span v-if='isFirstFilterMatch(filter)'>
                  {{filter.attribute.label}}
                </span>
              </p>
            </td>
            <td>
              <p class="control is-expanded">
                <span
                  class="select is-fullwidth is-small">
                  <select v-model='filter.expression'>
                    <option
                      v-for="filterOption in filterOptions"
                      :key='filterOption.label'
                      :value='filterOption.expression'>{{filterOption.label}}</option>
                  </select>
                </span>
              </p>
            </td>
            <td>
              <p class="control is-expanded">
                <input
                  class="input is-small"
                  :type="getFilterInputType(filter.filterType)"
                  @focus="$event.target.select()"
                  v-model='filter.value'
                  placeholder="Filter value">
              </p>
            </td>
            <td>
              <div class="control">
                <button
                  class="button is-small is-fullwidth"
                  @click.stop='removeFilter(filter)'>
                  Remove</button>
              </div>
            </td>
          </tr>
        </template>

      </tbody>
    </table>

  </div>
</template>

<style lang="scss">
</style>
