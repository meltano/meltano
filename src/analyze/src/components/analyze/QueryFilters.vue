<script>
import { mapState, mapGetters, mapActions } from 'vuex';

export default {
  name: 'QueryFilters',
  computed: {
    ...mapState('designs', [
      'filterOptions',
      'filters',
    ]),
    ...mapGetters('designs', [
      'getAttributesByTable',
      'hasFilters',
    ]),
  },
  methods: {
    ...mapActions('designs', [
      'toggleFilter',
      'removeFilter',
    ]),
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
              data-tooltip='The filter operation for the selected column or aggregate.'>
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
                <select>
                  <optgroup
                    v-for="table in getAttributesByTable"
                    :key='table.label'
                    :label="table.label">
                    <option disabled>Columns</option>
                    <option
                      v-for="column in table.columns"
                      :key='column.label'>{{column.label}}</option>
                    <option disabled>Aggregates</option>
                    <option
                      v-for="aggregate in table.aggregates"
                      :key='aggregate.label'>{{aggregate.label}}</option>
                  </optgroup>
                </select>
              </span>
            </p>
          </td>
          <td>
            <p class="control is-expanded">
              <span
                class="select is-fullwidth is-small">
                <select>
                  <option
                    v-for="filterOption in filterOptions"
                    :key='filterOption.label'>{{filterOption.label}}</option>
                </select>
              </span>
            </p>
          </td>
          <td>
            <p class="control is-expanded">
              <input
                class="input is-small"
                type="text"
                ref='value'
                @focus="$event.target.select()"
                placeholder="Filter value">
            </p>
          </td>
          <td>
            <div class="control">
              <button class="button is-small is-fullwidth">Delete</button>
            </div>
          </td>
        </tr>
      </tbody>
    </table>
  </div>
</template>

<style lang="scss">
</style>
