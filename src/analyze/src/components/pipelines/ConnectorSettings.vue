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
    fieldClass: { type: String },
    configSettings: {
      type: Object,
      required: true,
      default: () => {},
    },
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
    labelClass() {
      return this.fieldClass || 'is-normal';
    },
    successClass() {
      return setting =>
        (this.getIsConfigSettingValid(setting)
          ? 'is-success has-text-success'
          : null);
    },
  },
  created() {
    /**
     * For select input elements
     * Search through settings for default values
     * Required because of v-model being undefined
     * which overrides `selected` property on options
     */
    if (this.configSettings.settings) {
      this.configSettings.settings.forEach((setting) => {
        if (setting.kind === 'dropdown') {
          const defaultSetting = setting.options.find(item => item.default === true);

          this.configSettings.config[setting.name] = defaultSetting.value;
        }
      });
    }
  },
};
</script>

<template>
  <div>
    <slot name="top" />
    <div class="field is-horizontal" v-for='setting in configSettings.settings' :key='setting.name'>
      <div :class="['field-label', labelClass]">
        <label class="label">{{ setting.label || getCleanedLabel(setting.name) }}</label>
      </div>
      <div class="field-body">
        <div class="field">
          <div class="control is-expanded">

            <!-- Boolean -->
            <label
              v-if='getIsOfKindBoolean(setting.kind)'
              class="checkbox">
              <input
                v-model="configSettings.config[setting.name]"
                :class="successClass(setting)"
                type="checkbox">
            </label>

            <!-- Date -->
            <InputDateIso8601
              v-else-if='getIsOfKindDate(setting.kind)'
              v-model="configSettings.config[setting.name]"
              :name='setting.name'
              input-classes='is-small' />

            <!-- Dropdown -->
            <div v-else-if="setting.kind === 'dropdown'" class="select is-small">
              <select
                v-model="configSettings.config[setting.name]"
                :name="`${setting.name}-dropdown`"
                :id="`${setting.name}-select-menu`">
                <option v-for="(option, index) in setting.options"
                  :key="`${option.label}-${index}`"
                  :value="option.value"
                >
                  {{ option.label }}
                </option>
              </select>
            </div>

            <!-- Text / Password / Email -->
            <input
              v-else-if='getIsOfKindTextBased(setting.kind)'
              v-model="configSettings.config[setting.name]"
              :class="['input', fieldClass, successClass(setting)]"
              @focus="$event.target.select()"
              :type="getTextBasedInputType(setting)"
              :placeholder="setting.value || setting.name">
          </div>
          <p
            v-if="setting.description"
            class="help is-italic"
            >
            {{ setting.description }}
          </p>
          <p
            v-if="setting.documentation"
            class="help"
            >
            <a :href="setting.documentation">More Info.</a>
          </p>
        </div>
      </div>
    </div>
    <slot name="bottom" />
  </div>
</template>

<style lang="scss">
</style>
