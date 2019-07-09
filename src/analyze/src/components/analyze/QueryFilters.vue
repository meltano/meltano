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
    <table class="table pipelines-table is-fullwidth">

      <thead>
        <tr>
          <th>
            <span>Attribute</span>
            <span
              class="icon has-text-grey-light tooltip is-tooltip-multiline is-tooltip-right"
              data-tooltip="The column or aggregate to filter.">
              <font-awesome-icon icon="info-circle"></font-awesome-icon>
            </span>
          </th>
          <th class='has-text-centered'>
            <span>Operation</span>
            <span
              class="icon has-text-grey-light tooltip is-tooltip-multiline"
              data-tooltip='The filter operation for the selected column or aggregate.'>
              <font-awesome-icon icon="info-circle"></font-awesome-icon>
            </span>
          </th>
          <th class='has-text-centered'>
            <span>Value</span>
            <span
              class="icon has-text-grey-light tooltip is-tooltip-multiline"
              data-tooltip='The value to operate on when filtering.'>
              <font-awesome-icon icon="info-circle"></font-awesome-icon>
            </span>
          </th>
        </tr>
      </thead>

      <tbody>
        <tr>
          <td>
            <p class="control is-expanded">
              <span
                class="select is-fullwidth">
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
              <span
                class="select is-fullwidth">
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
                class="input"
                type="text"
                ref='value'
                @focus="$event.target.select()"
                placeholder="Filter value">
            </p>
          </td>
        </tr>
      </tbody>
    </table>
  </div>
</template>

<style lang="scss">
</style>
