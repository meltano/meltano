<script>
import Dropdown from '@/components/generic/Dropdown'

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
    }
  },
  data() {
    return {
      addProfileSettings: { name: null },
      profiles: [] // TEMP replace with proper passed props
    }
  },
  methods: {
    addProfile() {
      this.profiles.push(Object.assign({}, this.addProfileSettings))
      this.addProfileSettings = { name: null }
    },
    setProfileName(name) {
      this.addProfileSettings.name = name
      // TODO likely auto swap to this newly created profile
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
      <p>Current profile:</p>
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
                  :value="addProfileSettings.name"
                  class="input"
                  type="text"
                  placeholder="Name new profile"
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
      <span
        class="icon has-text-grey-light tooltip is-tooltip-multiline"
        :data-tooltip="
          `Profiles enable a single connector (${
            connector.name
          } for example) to be reused with multiple accounts or configurations.`
        "
      >
        <font-awesome-icon icon="info-circle"></font-awesome-icon>
      </span>
    </div>
  </div>
</template>

<style lang="scss"></style>
