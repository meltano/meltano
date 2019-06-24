<script>
import utils from '@/utils/utils';

export default {
  name: 'ConnectorSettings',
  props: {
    configSettings: { type: Object, required: true, default: () => {} },
  },
  computed: {
    getCleanedLabel() {
      return value => utils.titleCase(utils.underscoreToSpace(value));
    },
    getInputDateMeta() {
      return utils.getInputDateMeta();
    },
    getIsConfigSettingValid() {
      return value => value !== null && value !== undefined && value !== '';
    },
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
  },
};
</script>

<template>
  <div>

    <div class="field is-horizontal" v-for='setting in configSettings.settings' :key='setting.name'>
      <div class="field-label is-normal">
        <label class="label is-small">{{ getCleanedLabel(setting.label || setting.name) }}</label>
      </div>
      <div class="field-body">
        <div class="field">
          <p class="control is-expanded">

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
              :pattern="getInputDateMeta.pattern"
              :min='getInputDateMeta.min'
              :max='getInputDateMeta.today'>

            <!-- Text / Password / Email -->
            <input
              v-else-if='getIsOfKindTextBased(setting.kind)'
              class="input is-small"
              @focus="$event.target.select()"
              :type="getTextBasedInputType(setting)"
              :placeholder="setting.value || setting.name"
              v-model="configSettings.config[setting.name]">

          </p>
          <p
            v-if='!getIsConfigSettingValid(configSettings.config[setting.name])'
            class="help has-text-grey-light is-italic">
            This field is required
          </p>
          <p
            v-if="setting.description"
            class='help'
            >
            {{ setting.description }}
          </p>
        </div>
      </div>
    </div>

  </div>
</template>

<style lang="scss">
</style>
