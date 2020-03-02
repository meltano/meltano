<script>
import { CHART_MODELS } from '@/components/analyze/charts/ChartModels'
import Dropdown from '@/components/generic/Dropdown'

export default {
  name: 'ChartTypePicker',
  components: {
    Dropdown
  },
  props: {
    chartType: { type: String, required: true }
  },
  computed: {
    getActiveModel() {
      return this.getModels.find(model => model.type === this.chartType)
    },
    getIcon() {
      return this.getActiveModel.icon
    },
    getLabel() {
      return this.getActiveModel.label
    },
    getModels() {
      return Object.values(CHART_MODELS)
    }
  },
  methods: {
    onChartTypeChange(type) {
      this.$emit('chart-type-change', type)
    }
  }
}
</script>

<template>
  <Dropdown
    :label="getLabel"
    :icon-open="getIcon"
    button-classes="has-text-interactive-secondary"
    is-right-aligned
  >
    <div class="dropdown-content">
      <a
        v-for="model in getModels"
        :key="model.type"
        class="dropdown-item"
        data-dropdown-auto-close
        @click="onChartTypeChange(model.type)"
      >
        <div
          class="is-flex is-vcentered"
          data-dropdown-auto-close
          :class="{
            'is-active has-text-interactive-secondary':
              getActiveModel.type === model.type
          }"
        >
          <span class="icon is-small mr-05r" data-dropdown-auto-close>
            <font-awesome-icon
              :icon="model.icon"
              data-dropdown-auto-close
            ></font-awesome-icon>
          </span>
          <span data-dropdown-auto-close>{{ model.label }}</span>
        </div>
      </a>
    </div>
  </Dropdown>
</template>

<style lang="scss"></style>
