<script>
import Plugin from '@/components/pipelines/Plugin'

export default {
  name: 'PluginList',
  components: {
    Plugin,
  },
  props: {
    items: {
      type: Array,
      required: true,
    },
    pluginType: {
      type: String,
      required: true,
    },
  },
  computed: {
    getColumns() {
      const length = this.items.length
      const halfLength = length / 2
      const columnOneLength = Math.ceil(halfLength)
      const columnOne = this.items.slice(0, columnOneLength)
      const columnTwo = this.items.slice(columnOneLength, length)
      return [columnOne, columnTwo]
    },
  },
}
</script>

<template>
  <div class="columns">
    <div v-for="(column, idx) in getColumns" :key="idx" class="column">
      <Plugin
        v-for="plugin in column"
        :key="plugin.name"
        :type="pluginType"
        :plugin="plugin"
      />
    </div>
  </div>
</template>

<style lang="scss"></style>
