<script>
import { mapGetters, mapState, mapActions } from 'vuex'

import Dropdown from '@/components/generic/Dropdown'
import Logo from '@/components/navigation/Logo'
import utils from '@/utils/utils'

const READONLY_INFO = {
  project_readonly: {
    label: 'Read-only project',
    tooltip: 'This Meltano project is deployed as read-only',
    url: 'https://docs.meltano.com/reference/settings#project-readonly',
  },
  'ui.readonly': {
    label: 'Read-only UI',
    tooltip: 'Meltano UI is running in read-only mode',
    url: 'https://docs.meltano.com/reference/settings#ui-readonly',
  },
  'ui.anonymous_readonly': {
    label: 'Read-only UI',
    tooltip: 'Meltano UI is running in read-only mode until you sign in',
    url: 'https://docs.meltano.com/reference/settings#ui-anonymous-readonly',
  },
}

export default {
  name: 'MainNav',
  components: {
    Dropdown,
    Logo,
  },
  data() {
    return {
      isMobileMenuOpen: false,
    }
  },
  computed: {
    ...mapGetters('orchestration', ['getRunningPipelines']),
    ...mapGetters('repos', ['hasModels']),
    ...mapGetters('system', ['updateAvailable']),
    ...mapState('system', ['latestVersion', 'updating', 'version', 'identity']),
    isAnalysisEnabled() {
      return !!this.$flask.isAnalysisEnabled
    },
    getIconColor() {
      return (parentPath) =>
        this.getIsSubRouteOf(parentPath)
          ? 'has-text-interactive-navigation'
          : 'has-text-grey-light'
    },
    getIsCurrentPath() {
      return (path) => this.$route.path.includes(path)
    },
    getIsSubRouteOf() {
      return (parentPath) => utils.getIsSubRouteOf(parentPath, this.$route.path)
    },
    readonlySetting() {
      return this.$flask.isReadonlyEnabled
        ? 'ui.readonly'
        : this.$flask.isAnonymousReadonlyEnabled &&
          this.identity &&
          this.identity.anonymous
        ? 'ui.anonymous_readonly'
        : this.$flask.isProjectReadonlyEnabled
        ? 'project_readonly'
        : null
    },
    isReadonly() {
      return !!this.readonlySetting
    },
    readonlyLabel() {
      return READONLY_INFO[this.readonlySetting].label
    },
    readonlyTooltip() {
      return READONLY_INFO[this.readonlySetting].tooltip
    },
    readonlyUrl() {
      return READONLY_INFO[this.readonlySetting].url
    },
    logoUrl() {
      return this.$flask.logoUrl
    },
  },
  watch: {
    $route() {
      if (this.isMobileMenuOpen) {
        this.closeMobileMenu()
      }
    },
  },
  created() {
    this.$store.dispatch('plugins/getPlugins')
    this.$store.dispatch('plugins/getInstalledPlugins')
    this.$store.dispatch('repos/getModels')
  },
  methods: {
    ...mapActions('system', ['logout', 'login']),
    closeMobileMenu() {
      this.isMobileMenuOpen = false
    },
    mobileMenuClicked() {
      this.isMobileMenuOpen = !this.isMobileMenuOpen
    },
    startUpgrade() {
      this.$store.dispatch('system/upgrade').then(() => {
        document.location.reload()
      })
    },
  },
}
</script>

<template>
  <nav class="navbar is-transparent">
    <div class="navbar-brand">
      <div class="navbar-item navbar-child">
        <img v-if="logoUrl" :src="logoUrl" />
        <Logo v-else />
      </div>
      <div
        class="navbar-burger burger"
        :class="{ 'is-active': isMobileMenuOpen }"
        data-target="meltnavbar-transparent"
        @click="mobileMenuClicked"
      >
        <span></span>
        <span></span>
        <span></span>
      </div>
    </div>

    <div
      id="meltnavbar-transparent"
      class="navbar-menu"
      :class="{ 'is-active': isMobileMenuOpen }"
    >
      <div class="navbar-start">
        <router-link
          :to="{ name: 'extractors' }"
          :class="{ 'router-link-active': getIsSubRouteOf('/extractors') }"
          class="navbar-item navbar-child has-text-weight-semibold"
        >
          <a
            class="button has-background-transparent is-borderless is-paddingless"
            :class="{
              'has-text-interactive-navigation': getIsSubRouteOf('/extractors'),
            }"
          >
            <span class="icon is-small" :class="getIconColor('/extractors')">
              <font-awesome-icon icon="sign-out-alt"></font-awesome-icon>
            </span>
            <span>Extractors</span>
          </a>
        </router-link>

        <router-link
          :to="{ name: 'loaders' }"
          :class="{ 'router-link-active': getIsSubRouteOf('/loaders') }"
          class="navbar-item navbar-child has-text-weight-semibold"
        >
          <a
            class="button has-background-transparent is-borderless is-paddingless"
            :class="{
              'has-text-interactive-navigation': getIsSubRouteOf('/loaders'),
            }"
          >
            <span class="icon is-small" :class="getIconColor('/loaders')">
              <font-awesome-icon icon="sign-in-alt"></font-awesome-icon>
            </span>
            <span>Loaders</span>
          </a>
        </router-link>

        <router-link
          :to="{ name: 'pipelines' }"
          :class="{ 'router-link-active': getIsSubRouteOf('/pipelines') }"
          class="navbar-item navbar-child has-text-weight-semibold"
        >
          <a
            class="button has-background-transparent is-borderless is-paddingless"
            :class="{
              'has-text-interactive-navigation': getIsSubRouteOf('/pipelines'),
            }"
          >
            <span class="icon is-small" :class="getIconColor('/pipelines')">
              <font-awesome-icon icon="stream"></font-awesome-icon>
            </span>
            <span>Pipelines</span>
            <span
              v-if="getRunningPipelines.length > 0"
              class="tag ml-05r is-rounded is-info"
            >
              {{ getRunningPipelines.length }}
            </span>
          </a>
        </router-link>
      </div>

      <div class="navbar-end">
        <div class="navbar-item navbar-child level">
          <div class="level-right">
            <div v-if="updateAvailable" class="level-item">
              <Dropdown
                label="Update Available"
                :button-classes="`is-info is-small ${
                  updating ? 'is-loading' : ''
                }`"
                menu-classes="dropdown-menu-600"
                icon-open="gift"
                icon-close="caret-up"
                is-right-aligned
              >
                <div class="dropdown-content is-unselectable">
                  <div class="dropdown-item">
                    <p>
                      View the
                      <a
                        href="https://github.com/meltano/meltano/blob/main/CHANGELOG.md"
                        target="_blank"
                        >CHANGELOG.md</a
                      >
                      to see what is updated by the version.
                    </p>
                  </div>
                  <div class="dropdown-item">
                    <div class="level">
                      <div class="level-left">
                        <div class="field is-grouped is-grouped-multiline">
                          <div class="control">
                            <div class="tags has-addons">
                              <span class="tag">Current</span>
                              <span class="tag is-info">{{ version }}</span>
                            </div>
                          </div>
                          <div class="control">
                            <div class="tags has-addons">
                              <span class="tag">Latest</span>
                              <span class="tag is-info">{{
                                latestVersion
                              }}</span>
                            </div>
                          </div>
                        </div>
                      </div>
                      <div class="level-right">
                        <div class="buttons is-right">
                          <button
                            class="button is-text"
                            data-dropdown-auto-close
                          >
                            Cancel
                          </button>
                          <button
                            class="button is-interactive-primary"
                            data-dropdown-auto-close
                            @click="startUpgrade"
                          >
                            Update Meltano
                          </button>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              </Dropdown>
            </div>
            <div class="level-item">
              <div class="buttons">
                <a
                  v-if="isReadonly"
                  class="button is-small is-text has-background-transparent tooltip is-tooltip-left"
                  :data-tooltip="readonlyTooltip"
                  :href="readonlyUrl"
                  target="_blank"
                >
                  <span class="icon">
                    <font-awesome-icon icon="eye"></font-awesome-icon>
                  </span>
                  <span>{{ readonlyLabel }}</span>
                </a>

                <a
                  v-if="!updateAvailable && version"
                  class="button is-small is-text has-background-transparent tooltip is-tooltip-left"
                  data-tooltip="View this version's additions, changes, & fixes"
                  href="https://github.com/meltano/meltano/blob/main/CHANGELOG.md"
                  target="_blank"
                >
                  <span class="icon">
                    <font-awesome-icon icon="history"></font-awesome-icon>
                  </span>
                  <span>v{{ version }}</span>
                </a>

                <a
                  v-if="identity && !identity.anonymous"
                  class="button is-small has-background-transparent tooltip is-tooltip-left"
                  :data-tooltip="`Sign out: ${identity.username}`"
                  @click="logout"
                >
                  <span class="icon">
                    <font-awesome-icon icon="user"></font-awesome-icon>
                  </span>
                  <span>Sign Out</span>
                </a>

                <a
                  v-if="identity && identity.canSignIn"
                  class="button is-small has-background-transparent"
                  @click="login"
                >
                  <span class="icon">
                    <font-awesome-icon icon="user"></font-awesome-icon>
                  </span>
                  <span>Sign In</span>
                </a>

                <a
                  class="button is-small has-background-transparent tooltip is-tooltip-left"
                  data-tooltip="I need help"
                  target="_blank"
                  href="https://www.meltano.com/slack"
                >
                  <span class="icon">
                    <font-awesome-icon
                      icon="question-circle"
                    ></font-awesome-icon>
                  </span>
                </a>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </nav>
</template>

<style lang="scss">
.navbar-burger span {
  color: $interactive-navigation;
}
.navbar-brand .navbar-item {
  padding: 0 1.75rem 0 1.25rem;
}
.navbar.is-transparent {
  background-color: transparent;

  .navbar-start .navbar-link,
  .navbar-start > .navbar-item {
    color: $interactive-navigation-inactive;
    border-bottom: 1px solid $grey-lighter;

    &.router-link-active {
      color: $interactive-navigation;
      border-color: $interactive-navigation;
    }
  }
  .navbar-item {
    &.has-dropdown {
      border-bottom: none;

      .explore-dropdown-shell {
        min-width: 300px;
      }
    }

    .navbar-dropdown-scrollable {
      overflow-y: scroll;
      max-height: 80vh;
    }
  }
}
</style>
