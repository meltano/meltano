<script>
export default {
  name: 'ConnectorSettings',
  props: {
    settings: { type: Object, required: true, default: () => {} },
  },
};
</script>

<template>
  <div>

    <div class="field is-horizontal" v-for='(val, key) in settings' :key='key'>
      <div class="field-label is-normal">
        <label class="label">{{key}}</label>
      </div>
      <div class="field-body">
        <div class="field">
          <p class="control">
            <input
              class="input"
              type="text"
              :placeholder="val"
              v-model="settings[key]">
          </p>
        </div>
      </div>
    </div>

  </div>
</template>

<style lang="scss">
</style>
