<script>
import { mapGetters } from 'vuex'
import InputDateIso8601 from '@/components/generic/InputDateIso8601'
import TooltipCircle from '@/components/generic/TooltipCircle'

import utils from '@/utils/utils'

export default {
  name: 'ConnectorSettings',
  components: {
    InputDateIso8601,
    TooltipCircle
  },
  props: {
    fieldClass: { type: String },
    configSettings: {
      type: Object,
      required: true,
      default: () => {}
    }
  },
  watch: {
    configSettings: {
      handler(newVal) {
        /**
         * Improve account UX by auto-detecting Account ID via URL for configs that have `account`
         * This is currently Loader-Snowflake specific and we'll need a more robust solution
         * when/if we add UX helpers like this for more connectors
         */
        const accountInput = newVal.config.account
        if (accountInput) {
          const parsedAccountId = utils.snowflakeAccountParser(accountInput)
          this.configSettings.config.account =
            parsedAccountId || newVal.config.account
        }
      },
      deep: true
    }
  },
  computed: {
    ...mapGetters('configuration', ['getIsConfigSettingValid']),
    getCleanedLabel() {
      return value => utils.titleCase(utils.underscoreToSpace(value))
    },
    getIsOfKindBoolean() {
      return kind => kind === 'boolean'
    },
    getIsOfKindDate() {
      return kind => kind === 'date_iso8601'
    },
    getIsOfKindOptions() {
      return kind => kind === 'options'
    },
    getIsOfKindTextBased() {
      return kind =>
        !this.getIsOfKindBoolean(kind) && !this.getIsOfKindDate(kind)
    },
    getTextBasedInputType() {
      let type = 'text'
      return setting => {
        switch (setting.kind) {
          case 'password':
            type = 'password'
            break
          case 'email':
            type = 'email'
            break
          default:
            type = utils.inferInputType(setting.name, 'text')
            break
        }
        return type
      }
    },
    labelClass() {
      return this.fieldClass || 'is-normal'
    },
    successClass() {
      return setting =>
        this.getIsConfigSettingValid(setting)
          ? 'is-success has-text-success'
          : null
    }
  },
  methods: {
    findLabel(setting) {
      return setting.options.find(item => item.value === setting.value).label
    }
  }
}
</script>

<template>
  <div>
    <slot name="top" />
    <div
      class="field is-horizontal"
      v-for="setting in configSettings.settings"
      :key="setting.name"
    >
      <div :class="['is-flex', 'field-label', labelClass]">
        <label class="label">{{
          setting.label || getCleanedLabel(setting.name)
        }}</label>
        <TooltipCircle
          v-if="setting.tooltip"
          :text="setting.tooltip"
          class="label-tooltip"
        />
      </div>
      <div class="field-body">
        <div class="field">
          <div class="control is-expanded">
            <!-- Boolean -->
            <label v-if="getIsOfKindBoolean(setting.kind)" class="checkbox">
              <input
                v-model="configSettings.config[setting.name]"
                :class="successClass(setting)"
                type="checkbox"
              />
            </label>

            <!-- Date -->
            <InputDateIso8601
              v-else-if="getIsOfKindDate(setting.kind)"
              v-model="configSettings.config[setting.name]"
              :name="setting.name"
              input-classes="is-small"
            />

            <!-- Dropdown -->
            <div
              v-else-if="getIsOfKindOptions(setting.kind)"
              class="select is-small is-fullwidth"
            >
              <select
                v-model="configSettings.config[setting.name]"
                :name="`${setting.name}-options`"
                :id="`${setting.name}-select-menu`"
              >
                <option
                  v-for="(option, index) in setting.options"
                  :key="`${option.label}-${index}`"
                  :value="option.value"
                >
                  {{ option.label }}
                </option>
              </select>
            </div>

            <!-- Text / Password / Email -->
            <input
              v-else-if="getIsOfKindTextBased(setting.kind)"
              v-model="configSettings.config[setting.name]"
              :class="['input', fieldClass, successClass(setting)]"
              @focus="$event.target.select()"
              :type="getTextBasedInputType(setting)"
              :placeholder="setting.value || setting.name"
            />
          </div>
          <p v-if="setting.description" class="help is-italic">
            {{ setting.description }}
          </p>
          <p v-if="setting.documentation" class="help">
            <a :href="setting.documentation">More Info.</a>
          </p>
        </div>
      </div>
    </div>
    <slot name="bottom" />
  </div>
</template>

<style lang="scss">
.label-tooltip {
  margin-left: 0.25em;
}
</style>
