<template>
  <div>

    <div class="columns">
      <div class="column">
        <h3>Extractor Connection Settings</h3>
      </div>
    </div>
    <pre>{{extractor.config}}</pre>
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
  },
};
</script>

<style lang="scss">

</style>
