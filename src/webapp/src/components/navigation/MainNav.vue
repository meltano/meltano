<script>
import { mapGetters, mapState } from 'vuex'

import utils from '@/utils/utils'

import Dropdown from '@/components/generic/Dropdown'
import Logo from '@/components/navigation/Logo'

export default {
  name: 'MainNav',
  components: {
    Dropdown,
    Logo
  },
  data() {
    return {
      isMobileMenuOpen: false
    }
  },
  computed: {
    ...mapGetters('configuration', ['getRunningPipelines']),
    ...mapGetters('system', ['updateAvailable']),
    ...mapGetters('plugins', [
      'getIsStepLoadersMinimallyValidated',
      'getIsStepTransformsMinimallyValidated',
      'getIsStepScheduleMinimallyValidated'
    ]),
    ...mapState('system', ['latestVersion', 'updating', 'version']),
    getIconColor() {
      return parentPath =>
        this.getIsSubRouteOf(parentPath)
          ? 'has-text-interactive-navigation'
          : 'has-text-grey-light'
    },
    getIsCurrentPath() {
      return path => this.$route.path.includes(path)
    },
    getIsSubRouteOf() {
      return parentPath => utils.getIsSubRouteOf(parentPath, this.$route.path)
    }
  },
  watch: {
    $route() {
      if (this.isMobileMenuOpen) {
        this.closeMobileMenu()
      }
    }
  },
  methods: {
    closeMobileMenu() {
      this.isMobileMenuOpen = false
    },
    goToSchedules() {
      this.$router.push({ name: 'schedules' })
    },
    mobileMenuClicked() {
      this.isMobileMenuOpen = !this.isMobileMenuOpen
    },
    startUpgrade() {
      this.$store.dispatch('system/upgrade').then(() => {
        document.location.reload()
      })
    }
  }
}
</script>

<template>
  <nav class="navbar is-transparent">
    <div class="navbar-brand">
      <div class="navbar-item navbar-child">
        <Logo />
        <span
          class="meltano-label is-uppercase has-text-weight-bold has-text-primary ml-05r"
          >Meltano</span
        >
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
        <div class="navbar-item navbar-child has-dropdown is-hoverable">
          <router-link
            :to="{ name: 'dataSetup' }"
            :class="{ 'router-link-active': getIsSubRouteOf('/pipeline') }"
            class="navbar-link has-text-weight-semibold"
          >
            <a
              class="button has-background-transparent is-borderless is-paddingless"
              :class="{
                'has-text-interactive-navigation': getIsSubRouteOf('/pipeline')
              }"
            >
              <span class="icon is-small" :class="getIconColor('/pipeline')">
                <font-awesome-icon icon="th-list"></font-awesome-icon>
              </span>
              <span>Pipeline</span>
              <span
                v-if="getRunningPipelines.length > 0"
                class="tag tag-running-pipelines is-rounded is-info"
                @click.prevent="goToSchedules"
              >
                {{ getRunningPipelines.length }}
              </span>
            </a>
          </router-link>

          <div class="navbar-dropdown">
            <router-link
              :to="{ name: 'extractors' }"
              class="navbar-item button is-borderless"
              :class="{
                'is-active': getIsCurrentPath('/pipeline/extract')
              }"
              tag="button"
              >Extract</router-link
            >
            <router-link
              :to="{ name: 'loaders' }"
              class="navbar-item button is-borderless"
              :class="{ 'is-active': getIsCurrentPath('/pipeline/load') }"
              :disabled="!getIsStepLoadersMinimallyValidated"
              tag="button"
              >Load</router-link
            >
            <router-link
              :to="{ name: 'transforms' }"
              class="navbar-item button is-borderless"
              :class="{
                'is-active': getIsCurrentPath('/pipeline/transform')
              }"
              :disabled="!getIsStepTransformsMinimallyValidated"
              tag="button"
              >Transform</router-link
            >
            <router-link
              :to="{ name: 'schedules' }"
              class="navbar-item button is-borderless"
              :class="{ 'is-active': getIsCurrentPath('/pipeline/schedule') }"
              :disabled="!getIsStepScheduleMinimallyValidated"
              tag="button"
              >Run</router-link
            >
          </div>
        </div>

        <router-link
          :to="{ name: 'orchestration' }"
          :class="{ 'router-link-active': getIsSubRouteOf('/orchestrate') }"
          class="navbar-item navbar-child has-text-weight-semibold"
        >
          <a
            class="button has-background-transparent is-borderless is-paddingless"
            :class="{
              'has-text-interactive-navigation': getIsSubRouteOf('/orchestrate')
            }"
          >
            <span class="icon is-small" :class="getIconColor('/orchestrate')">
              <font-awesome-icon icon="project-diagram"></font-awesome-icon>
            </span>
            <span>Orchestrate</span>
          </a>
        </router-link>

        <router-link
          :to="{ name: 'analyze' }"
          :class="{ 'router-link-active': getIsSubRouteOf('/analyze') }"
          class="navbar-item navbar-child has-text-weight-semibold"
        >
          <a
            class="button has-background-transparent is-borderless is-paddingless"
            :class="{
              'has-text-interactive-navigation': getIsSubRouteOf('/analyze')
            }"
          >
            <span class="icon is-small" :class="getIconColor('/analyze')">
              <font-awesome-icon icon="chart-line"></font-awesome-icon>
            </span>
            <span>Analyze</span>
          </a>
        </router-link>

        <router-link
          :to="{ name: 'dashboards' }"
          :class="{ 'router-link-active': getIsSubRouteOf('/dashboard') }"
          class="navbar-item navbar-child has-text-weight-semibold"
        >
          <a
            class="button has-background-transparent is-borderless is-paddingless"
            :class="{
              'has-text-interactive-navigation': getIsSubRouteOf('/dashboard')
            }"
          >
            <span class="icon is-small" :class="getIconColor('/dashboard')">
              <font-awesome-icon icon="th-large"></font-awesome-icon>
            </span>
            <span>Dashboard</span>
          </a>
        </router-link>

        <a
          class="navbar-item navbar-child has-text-weight-semibold tooltip is-tooltip-warning is-tooltip-bottom"
          data-tooltip="Help shape this feature by contributing your ideas"
          target="_blank"
          href="https://gitlab.com/meltano/meltano/issues?scope=all&utf8=%E2%9C%93&state=opened&search=model"
          >Model</a
        >

        <a
          class="navbar-item navbar-child has-text-weight-semibold tooltip is-tooltip-warning is-tooltip-bottom"
          data-tooltip="Help shape this feature by contributing your ideas"
          target="_blank"
          href="https://gitlab.com/meltano/meltano/issues?scope=all&utf8=%E2%9C%93&state=opened&search=notebook"
          >Notebook</a
        >
      </div>

      <div class="navbar-end">
        <div class="navbar-item navbar-child level">
          <div class="level-right">
            <div v-if="updateAvailable" class="level-item">
              <Dropdown
                label="Update Available"
                :button-classes="
                  `is-info is-small ${updating ? 'is-loading' : ''}`
                "
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
                        href="https://gitlab.com/meltano/meltano/blob/master/CHANGELOG.md"
                        target="_blank"
                        >CHANGELOG.md</a
                      >
                      to see what is updated by the version.
                    </p>
                    <p class="is-italic">
                      This information will be inlined here in the future via
                      <a
                        href="https://gitlab.com/meltano/meltano/issues/961"
                        target="_blank"
                        >#961</a
                      >
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
              <a
                class="button has-background-light tooltip is-tooltip-warning is-tooltip-left"
                data-tooltip="Help shape this feature by contributing your ideas"
                target="_blank"
                href="https://gitlab.com/meltano/meltano/issues?scope=all&utf8=%E2%9C%93&state=opened&search=permission"
              >
                <font-awesome-icon
                  :icon="'user'"
                  :style="{ color: '#0F3B66' }"
                  title="Login currently disabled"
                ></font-awesome-icon>
              </a>
            </div>
          </div>
        </div>
      </div>
    </div>
  </nav>
</template>

<style lang="scss">
@import '@/scss/bulma-preset-overrides.scss';

.meltano-label {
  @media screen and (min-width: $tablet) {
    display: none;
  }
}
.navbar-menu {
  background-color: transparent;
}
.navbar-burger span {
  color: $interactive-navigation;
}
.navbar-brand .navbar-item {
  padding: 0 1rem;
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
    }
  }

  .navbar-start .navbar-link::after {
    border-color: $interactive-navigation-inactive;
  }
  .navbar-start .navbar-link:hover::after {
    border-color: $interactive-navigation;
  }

  .navbar-brand > a.navbar-item:hover,
  .navbar-start > a.navbar-item.is-active,
  .navbar-start > a.navbar-item:hover {
    background: transparent;
    color: $interactive-navigation;
    border-bottom: 1px solid $interactive-navigation-inactive;
  }
}
.tag-running-pipelines {
  margin-left: 0.5rem;
}
</style>
