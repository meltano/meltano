<script>
import InputDateIso8601 from '@/components/generic/InputDateIso8601'

import utils from '@/utils/utils'
import { ENV, MELTANO_YML } from '@/utils/constants'

export default {
  name: 'ConnectorSettings',
  components: {
    InputDateIso8601
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
    isShowDocs: {
      type: Boolean,
      default: false
    },
    plugin: {
      type: Object,
      required: true
    },
    requiredSettingsKeys: {
      type: Array,
      required: true
    },
    uploadFormData: {
      type: FormData,
      required: false,
      default: () => null
    }
  },
  computed: {
    connectorProfile() {
      return this.configSettings
        ? this.configSettings.profiles[this.configSettings.profileInFocusIndex]
        : {}
    },
    fileValue() {
      return setting => {
        let fullPath = this.connectorProfile.config[setting.name]
        return fullPath && utils.extractFileNameFromPath(fullPath)
      }
    },
    getInlineDocsUrl() {
      const path = window.FLASK
        ? this.plugin.docs
        : this.plugin.docs.replace(
            'https://meltano.com/',
            'http://localhost:8081/'
          )
      return `${path}?embed=true`
    },
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
    getIsOfKindFile() {
      return kind => kind === 'file'
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
        !this.getIsOfKindFile(kind) &&
        !this.getIsOfKindOptions(kind)
    },
    getIsProtected() {
      return setting => {
        const settingSource = this.connectorProfile.configSources[setting.name]

        return (
          setting.protected === true ||
          settingSource === ENV ||
          settingSource === MELTANO_YML
        )
      }
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
    protectedFieldMessage() {
      let configSources = this.configSettings.profiles[0].configSources

      return setting => {
        const configSource = configSources[setting.name]

        if (configSource === ENV) {
          return 'This setting is currently controlled by an environment variable.'
        } else if (configSource === MELTANO_YML) {
          return 'This setting is currently controlled through meltano.yml.'
        } else {
          return 'This setting is temporarily locked for added security until role-based access control is enabled. Click to learn more.'
        }
      }
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
        this.clearUploadFormData()
      }
    }
  },
  mounted() {
    this.focusInputIntelligently()
  },
  methods: {
    clearUploadFormData() {
      this.$emit('onChangeUploadFormData', null)
    },
    focusInputIntelligently() {
      this.$nextTick(() => {
        const inputs = Array.from(this.$el.getElementsByTagName('input'))
        if (inputs.length) {
          const firstEmptyInput = inputs.find(el => !el.value)
          const firstEnabledInput = inputs.find(el => !el.disabled)
          const targetInput = firstEmptyInput || firstEnabledInput || inputs[0]
          targetInput.blur()
          targetInput.focus()
        }
      })
    },
    onFileChange(event, setting) {
      const file = event.target.files[0]
      if (file) {
        // Queue file upload vs. greedy upload
        // Refactor needed if a setting requires multiple files and/or 2+ settings are `kind: file`
        const uploadFormData = new FormData()
        uploadFormData.append('file', file)
        uploadFormData.append('setting_name', setting.name)
        this.$emit('onChangeUploadFormData', uploadFormData)

        // Model update as v-model on `<input type="file">` not supported
        const profile = this.configSettings.profiles[
          this.configSettings.profileInFocusIndex
        ]
        profile.config[setting.name] = file.name
      }
    },
    onFocusInput(el) {
      const anchorName = el.id
      if (anchorName) {
        this.$refs.docs.contentWindow.postMessage(
          {
            source: 'meltano',
            anchor: anchorName.replace('setting-', '').replace('_', '-')
          },
          '*'
        )
      }
    },
    onFocusInputViaClick(event) {
      const el = event.currentTarget.querySelector('input')
      if (el) {
        el.focus()
        this.onFocusInput(el)
      }
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
            vm.connectorProfile.account = parsedAccountId
          }, 1000)
        } else {
          this.connectorProfile.account =
            newVal.profiles[newVal.profileInFocusIndex].config.account
        }
      }
    }
  }
}
</script>

<template>
  <div>
    <slot name="top" />

    <div class="columns">
      <div class="column" :class="{ 'is-two-fifths': isShowDocs }">
        <div class="content ">
          <h3 class="is-title">Configuration</h3>
        </div>
      </div>
      <div
        v-if="isShowDocs"
        class="column"
        :class="{ 'is-three-fifths': isShowDocs }"
      >
        <div class="content">
          <div class="columns">
            <div class="column">
              <h3 class="is-title">Documentation</h3>
            </div>
            <div class="column">
              <a
                :href="plugin.docs"
                target="_blank"
                class="has-text-underlined is-pulled-right"
                >View Documentation Externally
              </a>
            </div>
          </div>
        </div>
      </div>
    </div>

    <div class="columns">
      <div class="column" :class="{ 'is-two-fifths': isShowDocs }">
        <form>
          <div
            v-for="setting in configSettings.settings"
            :key="setting.name"
            :class="{ 'field is-horizontal': !getIsOfKindHidden(setting.kind) }"
            class=" has-cursor-pointer"
            @click.stop="onFocusInputViaClick"
            @focusin="onFocusInput($event.target)"
          >
            <div
              v-if="!getIsOfKindHidden(setting.kind)"
              :class="['field-label', labelClass]"
            >
              <label
                class="label"
                :class="isShowDocs ? 'has-cursor-pointer' : ''"
                :for="getFormFieldForId(setting)"
              >
                <span>
                  <span class="has-text-underlined">{{
                    getLabel(setting)
                  }}</span>
                  <span>
                    <strong>{{ getRequiredLabel(setting) }}</strong></span
                  >
                </span>
              </label>
            </div>
            <div class="field-body">
              <div
                class="field"
                :class="{ 'has-addons': getIsProtected(setting) }"
              >
                <div class="control is-expanded has-icons-right">
                  <!-- Hidden -->
                  <input
                    v-if="getIsOfKindHidden(setting.kind)"
                    :id="getFormFieldForId(setting)"
                    v-model="
                      configSettings.profiles[
                        configSettings.profileInFocusIndex
                      ].config[setting.name]
                    "
                    type="hidden"
                  />

                  <!-- Boolean -->
                  <input
                    v-else-if="getIsOfKindBoolean(setting.kind)"
                    :id="getFormFieldForId(setting)"
                    v-model="
                      configSettings.profiles[
                        configSettings.profileInFocusIndex
                      ].config[setting.name]
                    "
                    class="checkbox"
                    :class="successClass(setting)"
                    type="checkbox"
                  />

                  <!-- Date -->
                  <InputDateIso8601
                    v-else-if="getIsOfKindDate(setting.kind)"
                    v-model="
                      configSettings.profiles[
                        configSettings.profileInFocusIndex
                      ].config[setting.name]
                    "
                    :name="setting.name"
                    :for-id="getFormFieldForId(setting)"
                    :input-classes="`is-small ${successClass(setting)}`"
                  />

                  <!-- File -->
                  <div
                    v-else-if="getIsOfKindFile(setting.kind)"
                    class="file has-name is-small"
                  >
                    <label class="file-label is-file-fullwidth">
                      <div>
                        <input
                          :id="getFormFieldForId(setting)"
                          class="file-input"
                          type="file"
                          :name="setting.name"
                          @change="onFileChange($event, setting)"
                        />
                        <span class="file-cta has-background-white">
                          <span class="file-icon">
                            <font-awesome-icon
                              icon="file-upload"
                            ></font-awesome-icon>
                          </span>
                          <span class="file-label">
                            <span>Upload</span>
                          </span>
                        </span>
                      </div>
                      <span
                        class="file-name is-file-fullwidth file-name-width"
                        :class="
                          fileValue(setting)
                            ? 'has-text-success'
                            : 'has-text-grey-light'
                        "
                      >
                        {{ fileValue(setting) || setting.placeholder }}
                      </span>
                    </label>
                  </div>

                  <!-- Dropdown -->
                  <div
                    v-else-if="getIsOfKindOptions(setting.kind)"
                    class="select is-small is-fullwidth"
                  >
                    <select
                      :id="`${setting.name}-select-menu`"
                      v-model="
                        configSettings.profiles[
                          configSettings.profileInFocusIndex
                        ].config[setting.name]
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
                      configSettings.profiles[
                        configSettings.profileInFocusIndex
                      ].config[setting.name]
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
                </template>
              </div>
            </div>
          </div>
          <span class="is-italic is-pulled-right"
            >Required Inputs<strong>*</strong></span
          >
        </form>
      </div>
      <div
        v-if="isShowDocs"
        class="column"
        :class="{ 'is-three-fifths': isShowDocs }"
      >
        <div class="docs-container">
          <iframe
            ref="docs"
            class="docs"
            :src="getInlineDocsUrl"
            @load="focusInputIntelligently"
          />
        </div>
      </div>
    </div>

    <slot name="bottom" />
  </div>
</template>

<style lang="scss">
// This file input is fragile style-wise as Bulma tricks the <input> for display purposes
// As such, we set an explicit value in order to get the desired width with an "Upload" label.
// Refactor at will if a better file style approach (or component) comes along.
.file {
  .is-file-fullwidth {
    max-width: 20em;
    width: 100%;
  }
  .file-name-width {
    @media screen and (min-width: $tablet) {
      max-width: 14.6em;
    }
    max-width: 60em;
  }
}

.docs-container {
  display: flex;
  flex-direction: column;
  min-height: 50vh;
  height: 100%;

  iframe.docs {
    flex: 1;
    border: 1px solid $grey-lightest;
  }
}

.label-tooltip {
  margin-left: 0.25em;
}
</style>
