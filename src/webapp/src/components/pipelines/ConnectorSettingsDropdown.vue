<script>
import Dropdown from '@/components/generic/Dropdown'

export default {
  name: 'ExtractorSettingsModal',
  components: {
    Dropdown
  },
  props: {},
  data() {
    return {
      addConfigurationSettings: { name: null },
      profiles: [] // TEMP replace with proper passed props
    }
  },
  methods: {
    addConfiguration() {
      this.profiles.push(Object.assign({}, this.addConfigurationSettings))
      this.addConfigurationSettings = { name: null }
    },
    setConfigurationName(name) {
      this.addConfigurationSettings.name = name
    },
    switchProfile(profile) {
      console.log('swap profile: ', profile.name)
    }
  }
}
</script>

<template>
  <div class="level">
    <div class="level-item">
      <p>Editing configuration named:</p>
      <Dropdown
        label="Default"
        button-classes="is-small ml-05r"
        menu-classes="dropdown-menu-300"
        is-right-aligned
      >
        <div class="dropdown-content is-unselectable">
          <div class="dropdown-item" data-dropdown-auto-close>
            <div class="field">
              <div class="control">
                <input
                  :value="addConfigurationSettings.name"
                  class="input"
                  type="text"
                  placeholder="Name your configuration"
                  @input="setConfigurationName($event.target.value)"
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
                :disabled="!addConfigurationSettings.name"
                data-dropdown-auto-close
                @click="addConfiguration"
              >
                Add
              </button>
            </div>
          </div>
          <template v-if="profiles.length">
            <div class="dropdown-divider"></div>
            <a
              v-for="profile in profiles"
              :key="profile.name"
              class="dropdown-item"
              data-dropdown-auto-close
              @click="switchProfile(profile)"
            >
              {{ profile.name }}
            </a>
          </template>
        </div>
      </Dropdown>
    </div>
  </div>
</template>

<style lang="scss"></style>
