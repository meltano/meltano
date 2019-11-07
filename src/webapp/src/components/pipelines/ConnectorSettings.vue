<script>
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
    configSettings: {
      type: Object,
      required: true,
      default: () => {}
    },
    fieldClass: {
      type: String,
      default: ''
    }
  },
  computed: {
    getCleanedLabel() {
      return value => utils.titleCase(utils.underscoreToSpace(value))
    },
    getFormFieldForId() {
      return setting => `setting-${setting.name}`
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
    getIsProtected() {
      return setting => setting.protected === true
    },
    getIsOfKindTextBased() {
      return kind =>
        !this.getIsOfKindBoolean(kind) &&
        !this.getIsOfKindDate(kind) &&
        !this.getIsOfKindOptions(kind)
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
            type = utils.inferInputType(setting.name)
            break
        }
        return type
      }
    },
    labelClass() {
      return this.fieldClass || 'is-normal'
    },
    successClass() {
      return setting => (setting ? 'has-text-success' : null)
    }
  },
  watch: {
    configSettings: {
      handler(newVal) {
        this.snowflakeHelper(newVal)
      },
      deep: true
    }
  },
  mounted() {
    this.$nextTick(this.focusInputIntelligently)
  },
  methods: {
    findLabel(setting) {
      return setting.options.find(item => item.value === setting.value).label
    },
    focusInputIntelligently() {
      const inputs = Array.from(this.$el.getElementsByTagName('input'))
      if (inputs.length) {
        const firstEmptyInput = inputs.find(el => !el.value)
        const targetInput = firstEmptyInput || inputs[0]
        targetInput.focus()
      }
    },
    snowflakeHelper(newVal) {
      /**
       * Improve account UX by auto-detecting Account ID via URL
       * for configs that have `account`
       * This is currently Loader-Snowflake specific
       * and we'll need a more robust solution
       * when/if we add UX helpers like this for more connectors
       * TODO: Need to add a loader indicator to show something is "processing"
       */
      const accountInput =
        newVal.profiles[newVal.profileInFocusIndex].config.account
      if (accountInput) {
        const parsedAccountId = utils.snowflakeAccountParser(accountInput)

        if (parsedAccountId) {
          const vm = this

          setTimeout(() => {
            vm.configSettings.profiles[
              vm.configSettings.profileInFocusIndex
            ].account = parsedAccountId
          }, 1000)
        } else {
          this.configSettings.profiles[
            this.configSettings.profileInFocusIndex
          ].account = newVal.profiles[newVal.profileInFocusIndex].config.account
        }
      }
    }
  }
}
</script>

<template>
  <div>
    <slot name="top" />

    <form>
      <div
        v-for="setting in configSettings.settings"
        :key="setting.name"
        class="field is-horizontal"
      >
        <div :class="['field-label', labelClass]">
          <label class="label" :for="getFormFieldForId(setting)"
            >{{ setting.label || getCleanedLabel(setting.name) }}
            <TooltipCircle
              v-if="setting.tooltip"
              :text="setting.tooltip"
              class="label-tooltip"
            />
          </label>
        </div>
        <div class="field-body">
          <div class="field" :class="{ 'has-addons': getIsProtected(setting) }">
            <div class="control is-expanded has-icons-right">
              <!-- Boolean -->
              <input
                v-if="getIsOfKindBoolean(setting.kind)"
                :id="getFormFieldForId(setting)"
                v-model="
                  configSettings.profiles[configSettings.profileInFocusIndex]
                    .config[setting.name]
                "
                class="checkbox"
                :class="successClass(setting)"
                type="checkbox"
              />

              <!-- Date -->
              <InputDateIso8601
                v-else-if="getIsOfKindDate(setting.kind)"
                v-model="
                  configSettings.profiles[configSettings.profileInFocusIndex]
                    .config[setting.name]
                "
                :name="setting.name"
                :for-id="getFormFieldForId(setting)"
                :input-classes="`is-small ${successClass(setting)}`"
              />

              <!-- Dropdown -->
              <div
                v-else-if="getIsOfKindOptions(setting.kind)"
                class="select is-small is-fullwidth"
              >
                <select
                  :id="`${setting.name}-select-menu`"
                  v-model="
                    configSettings.profiles[configSettings.profileInFocusIndex]
                      .config[setting.name]
                  "
                  :name="`${setting.name}-options`"
                  :class="successClass(setting)"
                >
                  <option
                    v-for="(option, index) in setting.options"
                    :id="getFormFieldForId(setting)"
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
                :id="getFormFieldForId(setting)"
                v-model="
                  configSettings.profiles[configSettings.profileInFocusIndex]
                    .config[setting.name]
                "
                :class="['input', fieldClass, successClass(setting)]"
                :type="getTextBasedInputType(setting)"
                :placeholder="setting.value || setting.name"
                :disabled="getIsProtected(setting)"
                :readonly="getIsProtected(setting)"
                @focus="$event.target.select()"
              />
            </div>
            <div v-if="getIsProtected(setting)" class="control">
              <a
                href="https://meltano.com/docs/environment-variables.html#connector-settings-configuration"
                target="_blank"
                class="button is-small"
              >
                <span
                  class="icon has-text-grey-dark tooltip is-tooltip-multiline"
                  data-tooltip="This setting is temporarily locked for added security until role-based access control is enabled. Click to learn more."
                >
                  <font-awesome-icon icon="lock"></font-awesome-icon>
                </span>
              </a>
            </div>

            <p v-if="setting.description" class="help is-italic">
              {{ setting.description }}
            </p>
            <p v-if="setting.documentation" class="help">
              <a
                :href="setting.documentation"
                target="_blank"
                class="has-text-underlined"
                >More Info.</a
              >
            </p>
          </div>
        </div>
      </div>
    </form>

    <slot name="bottom" />
  </div>
</template>

<style lang="scss">
.label-tooltip {
  margin-left: 0.25em;
}
</style>
