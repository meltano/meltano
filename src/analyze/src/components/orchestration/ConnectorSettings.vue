<template>
  <div>

    <div class="columns">
      <div class="column">
        <h3>Connector Settings</h3>
      </div>
    </div>
    <pre>{{extractorSettings}}</pre>
  </div>
</template>

<script>
export default {
  name: 'ConnectorSettings',
  props: {
    extractor: {
      type: Object,
      default() {
        return {};
      },
    },
    extractorSettings: {
      type: Object,
      default() {
        return {};
      },
    },
  },
  created() {
    this.$store.dispatch('orchestrations/getExtractorSettings', this.extractor.name);
  },
  destroyed() {
    this.$store.dispatch('orchestrations/clearExtractorSettings');
  },
};
</script>

<style lang="scss">

</style>
