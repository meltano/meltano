<script>
import { mapGetters } from 'vuex';

import InputDateIso8601 from '@/components/generic/InputDateIso8601';

import utils from '@/utils/utils';

export default {
  name: 'ConnectorSettings',
  components: {
    InputDateIso8601,
  },
  props: {
    configSettings: { type: Object, required: true, default: () => {} },
  },
  computed: {
    ...mapGetters('configuration', [
      'getIsConfigSettingValid',
    ]),
    getCleanedLabel() {
      return value => utils.titleCase(utils.underscoreToSpace(value));
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
                v-model="configSettings.config[setting.name]"
                :class='{ "is-interactive-secondary has-text-interactive-secondary": getIsConfigSettingValid(configSettings.config[setting.name]) }'
                type="checkbox">
            </label>

            <!-- Date -->
            <InputDateIso8601
              v-else-if='getIsOfKindDate(setting.kind)'
              v-model="configSettings.config[setting.name]"
              :name='setting.name' />

            <!-- Text / Password / Email -->
            <input
              v-else-if='getIsOfKindTextBased(setting.kind)'
              v-model="configSettings.config[setting.name]"
              class="input is-small"
              :class='{ "is-interactive-secondary has-text-interactive-secondary": getIsConfigSettingValid(configSettings.config[setting.name]) }'
              @focus="$event.target.select()"
              :type="getTextBasedInputType(setting)"
              :placeholder="setting.value || setting.name">
          </p>
          <p
            v-if="setting.description"
            class='help is-italic'
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
