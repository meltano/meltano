<script>
import utils from '@/utils/utils';

export default {
  name: 'ConnectorSettings',
  props: {
    configSettings: { type: Object, required: true, default: () => {} },
  },
  computed: {
    getIsOfKindBoolean() {
      return kind => kind === 'boolean';
    },
    getIsOfKindDate() {
      return kind => kind === 'date_iso8601';
    },
    getIsOfKindTextBased() {
      return kind => !this.getIsOfKindBoolean(kind) && !this.getIsOfKindDate(kind);
    },
    getTextBasedInputType() {
      let type = 'text';
      return (setting) => {
        switch (setting.kind) {
          case 'password':
            type = 'password';
            break;
          case 'email':
            type = 'email';
            break;
          default:
            type = utils.inferInputType(setting.name, 'text');
            break;
        }
        return type;
      };
    },
    todaysDate() {
      return utils.getTodayYYYYMMDD();
    },
  },
};
</script>

<template>
  <div>

    <div class="field is-horizontal" v-for='setting in configSettings.settings' :key='setting.name'>
      <div class="field-label is-normal">
        <label class="label">{{ setting.label || setting.name }}</label>
      </div>
      <div class="field-body">
        <div class="field">
          <p class="control">

            <!-- Boolean -->
            <label
              v-if='getIsOfKindBoolean(setting.kind)'
              class="checkbox">
              <input
                type="checkbox"
                v-model="configSettings.config[setting.name]">
            </label>

            <!-- Date -->
            <input
              v-else-if='getIsOfKindDate(setting.kind)'
              type="date"
              :id="`date-${setting.name}`"
              :name="`date-${setting.name}`"
              v-model="configSettings.config[setting.name]"
              pattern="[0-9]{4}-[0-9]{2}-[0-9]{2}"
              min='`2000-01-01`'
              :max='todaysDate'>

            <!-- Text / Password / Email -->
            <input
              v-else-if='getIsOfKindTextBased(setting.kind)'
              class="input"
              :type="getTextBasedInputType(setting)"
              :placeholder="setting.value"
              v-model="configSettings.config[setting.name]">

          </p>
          <p
            v-if="setting.description"
            class='help'
            >{{ setting.description }}</p>
        </div>
      </div>
    </div>

  </div>
</template>

<style lang="scss">
</style>
