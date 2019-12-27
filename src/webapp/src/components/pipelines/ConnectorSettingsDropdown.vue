<script>
import { mapActions } from 'vuex'
import Vue from 'vue'

import Dropdown from '@/components/generic/Dropdown'
import utils from '@/utils/utils'

export default {
  name: 'ExtractorSettingsModal',
  components: {
    Dropdown
  },
  props: {
    configSettings: {
      type: Object,
      required: true,
      default: () => {}
    },
    connector: {
      type: Object,
      required: true,
      default: () => {}
    },
    pluginType: {
      type: String,
      required: true
    }
  },
  data() {
    return {
      addProfileSettings: { name: null }
    }
  },
  computed: {
    displayName() {
      return profile => profile.label || profile.name
    }
  },
  methods: {
    ...mapActions('orchestration', ['addConfigurationProfile']),
    addProfile() {
      const payload = {
        name: this.connector.name,
        type: this.pluginType,
        profile: Object.assign({}, this.addProfileSettings)
      }
      this.addConfigurationProfile(payload).then(response => {
        const profile = this.setAddedProfileDefaults(response.data)
        this.configSettings.profiles.push(profile)
        this.switchProfile(profile.name)
        Vue.toasted.global.success(`New Profile Added - ${profile.name}`)

        this.addProfileSettings = { name: null }
      })
    },
    setAddedProfileDefaults(profile) {
      const config = profile.config
      this.configSettings.settings.forEach(setting => {
        const isIso8601Date = setting.kind && setting.kind === 'date_iso8601'
        const isDefaultNeeded =
          config.hasOwnProperty(setting.name) && config[setting.name] === null
        if (isIso8601Date && isDefaultNeeded) {
          config[setting.name] = utils.getFirstOfMonthAsIso8601()
        }
      })
      return profile
    },
    setProfileName(name) {
      this.addProfileSettings.name = name
    },
    switchProfile(name) {
      const targetProfile = this.configSettings.profiles.find(
        profile => profile.name === name
      )
      const idx = this.configSettings.profiles.indexOf(targetProfile)
      this.configSettings.profileInFocusIndex = idx
    }
  }
}
</script>

<template>
  <div class="level">
    <div class="level-item level-right">
      <p>Current profile:</p>
      <Dropdown
        :label="
          displayName(
            configSettings.profiles[configSettings.profileInFocusIndex]
          )
        "
        button-classes="is-small ml-05r"
        is-right-aligned
      >
        <div class="dropdown-content is-unselectable">
          <div class="dropdown-item" data-dropdown-auto-close>
            <div class="field">
              <div class="control">
                <input
                  :value="addProfileSettings.name"
                  class="input"
                  type="text"
                  placeholder="Name profile"
                  @input="setProfileName($event.target.value)"
                />
              </div>
            </div>
            <div class="buttons is-right">
              <button class="button is-text" data-dropdown-auto-close>
                Cancel
              </button>
              <button
                data-test-id="button-save-report"
                class="button"
                :disabled="!addProfileSettings.name"
                data-dropdown-auto-close
                @click="addProfile"
              >
                Add
              </button>
            </div>
          </div>
          <template v-if="configSettings.profiles.length">
            <div class="dropdown-divider"></div>
            <a
              v-for="profile in configSettings.profiles"
              :key="profile.name"
              class="dropdown-item"
              data-dropdown-auto-close
              @click="switchProfile(profile.name)"
            >
              {{ displayName(profile) }}
            </a>
          </template>
        </div>
      </Dropdown>
      <span
        class="icon has-text-grey-light tooltip is-tooltip-multiline"
        :data-tooltip="
          `Profiles enable a single connector (${connector.name} for example) to be reused with multiple accounts or configurations.`
        "
      >
        <font-awesome-icon icon="info-circle"></font-awesome-icon>
      </span>
    </div>
  </div>
</template>

<style lang="scss"></style>
