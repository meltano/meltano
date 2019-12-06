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
    },
    plugin: {
      type: Object,
      required: true
    },
    requiredSettingsKeys: {
      type: Array,
      required: true
    }
  },
  computed: {
    getLabel() {
      return setting =>
        setting.label || utils.titleCase(utils.underscoreToSpace(setting.name))
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
    getIsOfKindHidden() {
      return kind => kind === 'hidden'
    },
    getIsOfKindOptions() {
      return kind => kind === 'options'
    },
    getIsOfKindTextBased() {
      return kind =>
        !this.getIsOfKindBoolean(kind) &&
        !this.getIsOfKindDate(kind) &&
        !this.getIsOfKindOptions(kind)
    },
    getIsProtected() {
      return setting => setting.protected === true
    },
    getPlaceholder() {
      return setting => setting.placeholder || setting.value || setting.name
    },
    getRequiredLabel() {
      return setting =>
        this.requiredSettingsKeys.includes(setting.name) ? '*' : ''
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
    pluginType() {
      const pluginName = this.plugin.name

      if (pluginName.startsWith('tap')) {
        return 'extractor'
      } else if (pluginName.startsWith('target')) {
        return 'loader'
      } else {
        return 'plugin'
      }
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
    },
    'configSettings.profileInFocusIndex': {
      handler(newVal, oldVal) {
        this.refocusInput(newVal, oldVal)
      }
    }
  },
  mounted() {
    this.focusInputIntelligently()
  },
  methods: {
    focusInputIntelligently() {
      this.$nextTick(() => {
        const inputs = Array.from(this.$el.getElementsByTagName('input'))
        if (inputs.length) {
          const firstEmptyInput = inputs.find(el => !el.value)
          const targetInput = firstEmptyInput || inputs[0]
          targetInput.focus()
        }
      })
    },
    refocusInput(newVal, oldVal) {
      if (newVal !== oldVal) {
        this.focusInputIntelligently()
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

    <slot name="docs">
      <div v-if="plugin.docs" class="content has-text-centered mt1r">
        <p class="content">
          View the
          <a :href="plugin.docs" target="_blank" class="has-text-underlined">
            {{ plugin.label || plugin.name }}
            {{ pluginType }}
          </a>
          documentation.
        </p>
      </div>
    </slot>

    <form>
      <div
        v-for="setting in configSettings.settings"
        :key="setting.name"
        :class="{ 'field is-horizontal': !getIsOfKindHidden(setting.kind) }"
      >
        <div
          :class="['field-label', labelClass]"
          v-if="!getIsOfKindHidden(setting.kind)"
        >
          <label class="label" :for="getFormFieldForId(setting)">
            <a
              v-if="setting.documentation"
              target="_blank"
              :href="setting.documentation"
              class="label"
            >
              <span
                class="has-text-underlined tooltip"
                :data-tooltip="
                  `Learn more about the ${getLabel(setting)} setting.`
                "
                >{{ getLabel(setting) }}</span
              >
              <span>{{ getRequiredLabel(setting) }}</span>
            </a>
            <span v-else>
              <span>{{ getLabel(setting) }}</span>
              <span>{{ getRequiredLabel(setting) }}</span>
            </span>
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
              <!-- Hidden -->
              <input
                v-if="getIsOfKindHidden(setting.kind)"
                :id="getFormFieldForId(setting)"
                v-model="
                  configSettings.profiles[configSettings.profileInFocusIndex]
                    .config[setting.name]
                "
                type="hidden"
              />

              <!-- Boolean -->
              <input
                v-else-if="getIsOfKindBoolean(setting.kind)"
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
                :placeholder="getPlaceholder(setting)"
                :disabled="getIsProtected(setting)"
                :readonly="getIsProtected(setting)"
                @focus="$event.target.select()"
              />
            </div>

            <!-- Visual helpers  -->
            <template v-if="!getIsOfKindHidden(setting.kind)">
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

              <p
                v-if="setting.description || setting.documentation"
                class="help"
              >
                <a
                  v-if="setting.documentation"
                  target="_blank"
                  :href="setting.documentation"
                  class="tooltip"
                  :data-tooltip="
                    `Learn more about the ${getLabel(setting)} setting.`
                  "
                >
                  <span v-if="!setting.description" class="has-text-underlined"
                    >Learn More.</span
                  >
                  <span class="icon has-text-link">
                    <font-awesome-icon
                      icon="external-link-square-alt"
                    ></font-awesome-icon>
                  </span>
                </a>
                <span v-if="setting.description" class="is-italic"
                  >{{ setting.description }}.
                </span>
              </p>
            </template>
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
