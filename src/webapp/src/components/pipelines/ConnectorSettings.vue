<script>
import axios from 'axios'

import { ENV, MELTANO_YML } from '@/utils/constants'
import InputDateIso8601 from '@/components/generic/InputDateIso8601'
import ConnectorLogo from '@/components/generic/ConnectorLogo'
import utils from '@/utils/utils'

export default {
  name: 'ConnectorSettings',
  components: {
    ConnectorLogo,
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
    isShowConfigWarning: {
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
  data: () => ({
    source: ''
  }),
  computed: {
    computedSettings() {
      return this.isTapGitLab
        ? this.gitLabSettings
        : this.configSettings.settings
    },
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
      return axios.getUri({
        url: window.FLASK
          ? this.plugin.docs
          : this.plugin.docs.replace(
              'https://meltano.com/',
              'http://localhost:8081/'
            ),
        params: {
          embed: true
        }
      })
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
    getIsOfKindOAuth() {
      return kind => this.isOAuthEnabled && kind === 'oauth'
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
    getHasAddons(getters) {
      return setting =>
        getters.getIsProtected(setting) ||
        getters.getIsOfKindOAuth(setting.kind)
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
    gitLabSettings() {
      const currentSourceApiLabel = this.source + 's'
      const ignoreList = ['groups', 'projects'].filter(
        item => item !== currentSourceApiLabel
      )

      if (this.isTapGitLab) {
        // Copy over currentSettings and add in custom select menu
        const newSettings = this.configSettings.settings.map(setting => setting)
        newSettings.splice(2, 0, {
          name: 'source',
          kind: 'options',
          options: [
            { label: 'Choose Group or Project', value: '' },
            { label: 'Group', value: 'group' },
            { label: 'Project', value: 'project' }
          ]
        })

        return newSettings.filter(setting => !ignoreList.includes(setting.name))
      }

      return []
    },
    isOAuthEnabled() {
      return !!this.$flask['oauthServiceUrl']
    },
    isTapGitLab() {
      return this.plugin.name === 'tap-gitlab'
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
    successClass() {
      return setting => (setting ? 'has-text-success' : null)
    }
  },
  watch: {
    'configSettings.profileInFocusIndex': {
      handler(newVal, oldVal) {
        this.refocusInput(newVal, oldVal)
        this.clearUploadFormData()
      }
    }
  },
  mounted() {
    this.focusInputIntelligently()
    this.isTapGitLab ? this.setGitLabSource() : null
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
            anchor: anchorName.replace('setting-', '').replace(/_/g, '-')
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
    openOAuthPopup(provider) {
      const oauthUrl = `${this.$flask.oauthServiceUrl}/${provider}`
      const winOpts =
        'resizable=no,scrollbars=no,close=yes,height=640,width=480'

      window.open(oauthUrl, name, winOpts)
    },
    setGitLabSource() {
      const currentProfile = this.configSettings.profiles[
        this.configSettings.profileInFocusIndex
      ]
      const hasGroupSetting = currentProfile.config.groups
      const hasProjectSetting = currentProfile.config.projects

      if (hasProjectSetting) {
        this.source = 'project'
      } else if (hasGroupSetting) {
        this.source = 'group'
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
                class="is-size-7 has-text-underlined is-pulled-right"
                >View Documentation Externally
              </a>
            </div>
          </div>
        </div>
      </div>
    </div>

    <div class="columns">
      <div class="column" :class="{ 'is-two-fifths': isShowDocs }">
        <article v-if="isShowConfigWarning" class="message is-warning is-small">
          <div class="message-body">
            <div class="content">
              <p>
                Take note that changing non-date related settings of an existing
                configuration can result in overwritten or merged data.
              </p>
            </div>
          </div>
        </article>
        <form>
          <div
            v-for="setting in computedSettings"
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
                :class="{
                  'has-addons': getHasAddons(setting)
                }"
              >
                <div class="control is-expanded">
                  <!-- Hidden -->
                  <input
                    v-if="getIsOfKindHidden(setting.kind)"
                    :id="getFormFieldForId(setting)"
                    v-model="connectorProfile.config[setting.name]"
                    type="hidden"
                  />

                  <!-- Boolean -->
                  <input
                    v-else-if="getIsOfKindBoolean(setting.kind)"
                    :id="getFormFieldForId(setting)"
                    v-model="connectorProfile.config[setting.name]"
                    class="checkbox"
                    :class="successClass(setting)"
                    :disabled="getIsProtected(setting)"
                    type="checkbox"
                  />

                  <!-- Date -->
                  <InputDateIso8601
                    v-else-if="getIsOfKindDate(setting.kind)"
                    v-model="connectorProfile.config[setting.name]"
                    :name="setting.name"
                    :for-id="getFormFieldForId(setting)"
                    :input-classes="`is-small ${successClass(setting)}`"
                    :disabled="getIsProtected(setting)"
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
                          :disabled="getIsProtected(setting)"
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
                        class="file-name is-file-fullwidth"
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

                  <!-- Custom Temporary Dropdown for tap-gitlab -->
                  <div
                    v-else-if="getIsOfKindOptions(setting.kind) && isTapGitLab"
                    class="select is-small is-fullwidth"
                  >
                    <select
                      :id="`${setting.name}-select-menu`"
                      v-model="source"
                      :name="`${setting.name}-options`"
                      :class="successClass(setting)"
                      :disabled="getIsProtected(setting)"
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
                      :disabled="getIsProtected(setting)"
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
                    v-model="connectorProfile.config[setting.name]"
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
                      href="https://meltano.com/developer-tools/environment-variables.html#connector-settings-configuration"
                      target="_blank"
                      class="button is-small"
                    >
                      <span
                        class="icon has-text-grey-dark tooltip is-tooltip-left"
                        :data-tooltip="protectedFieldMessage(setting)"
                      >
                        <font-awesome-icon icon="lock"></font-awesome-icon>
                      </span>
                    </a>
                  </div>

                  <!-- OAuth helper -->
                  <div v-if="getIsOfKindOAuth(setting.kind)" class="control">
                    <button
                      class="button is-small is-primary"
                      @click.prevent="openOAuthPopup(setting.oauth.provider)"
                    >
                      <span class="mr-025r">Get with</span>
                      <span class="icon has-text-grey-dark">
                        <connector-logo :connector="plugin.name" />
                      </span>
                    </button>
                  </div>
                </template>
              </div>
            </div>
          </div>
          <span class="is-italic is-pulled-right is-size-7"
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
// Refactor at will if a better file style approach (or component) comes along.
.file {
  .is-file-fullwidth {
    width: 100%;
  }
  .file-name {
    max-width: none;
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
