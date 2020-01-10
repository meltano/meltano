<script>
import { mapGetters, mapState, mapActions } from 'vuex'

import AnalyzeList from '@/components/analyze/AnalyzeList'
import Dropdown from '@/components/generic/Dropdown'
import Logo from '@/components/navigation/Logo'
import utils from '@/utils/utils'

export default {
  name: 'MainNav',
  components: {
    AnalyzeList,
    Dropdown,
    Logo
  },
  data() {
    return {
      isMobileMenuOpen: false
    }
  },
  computed: {
    ...mapGetters('orchestration', ['getRunningPipelines']),
    ...mapGetters('plugins', [
      'getIsStepLoadersMinimallyValidated',
      'getIsStepScheduleMinimallyValidated'
    ]),
    ...mapGetters('repos', ['hasModels']),
    ...mapGetters('system', ['updateAvailable']),
    ...mapState('system', ['latestVersion', 'updating', 'version', 'identity']),
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
  created() {
    this.$store.dispatch('orchestration/getAllPipelineSchedules')
    this.$store.dispatch('plugins/getAllPlugins')
    this.$store.dispatch('plugins/getInstalledPlugins')
    this.$store.dispatch('repos/getAllModels')
  },
  methods: {
    ...mapActions('system', ['logout']),
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
            :to="{
              name: getIsStepScheduleMinimallyValidated
                ? 'schedules'
                : 'dataSetup'
            }"
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
                <font-awesome-icon icon="stream"></font-awesome-icon>
              </span>
              <span>Pipelines</span>
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
              :to="{ name: 'schedules' }"
              class="navbar-item button is-borderless"
              :class="{ 'is-active': getIsCurrentPath('/pipeline/schedule') }"
              :disabled="!getIsStepScheduleMinimallyValidated"
              tag="button"
              >Schedule</router-link
            >
          </div>
        </div>

        <div class="navbar-item navbar-child has-dropdown is-hoverable">
          <a
            :class="{ 'router-link-active': getIsSubRouteOf('/analyze') }"
            class="navbar-link has-text-weight-semibold"
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
          </a>

          <div class="navbar-dropdown navbar-dropdown-scrollable">
            <template v-if="hasModels">
              <AnalyzeList></AnalyzeList>
            </template>
            <template v-else>
              <div class="box is-borderless is-shadowless is-marginless">
                <div class="content">
                  <h3 class="is-size-6">
                    No Models Installed
                  </h3>
                  <p>
                    Models are inferred and automatically installed for you
                    based off the installed Extractors from your data pipelines.
                    Set up a pipeline first.
                  </p>
                  <router-link
                    class="button is-interactive-primary"
                    :to="{ name: 'dataSetup' }"
                    >Create Data Pipeline</router-link
                  >
                </div>
              </div>
            </template>
          </div>
        </div>

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
            <span>Dashboards</span>
          </a>
        </router-link>
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
              <div class="buttons">
                <a
                  v-if="!updateAvailable && version"
                  class="button is-small is-text has-background-transparent tooltip is-tooltip-left"
                  data-tooltip="View this version's additions, changes, & fixes"
                  href="https://gitlab.com/meltano/meltano/blob/master/CHANGELOG.md"
                  target="_blank"
                >
                  v{{ version }}
                </a>
                <a
                  v-if="identity"
                  class="button is-small has-background-transparent tooltip is-tooltip-left"
                  :data-tooltip="`Sign out: ${identity.username}`"
                  @click="logout"
                >
                  <span>Sign Out</span>
                  <span class="icon">
                    <font-awesome-icon icon="user"></font-awesome-icon>
                  </span>
                </a>
                <a
                  class="button is-small has-background-transparent tooltip is-tooltip-left"
                  data-tooltip="I need help"
                  target="_blank"
                  href="https://meltano.com/docs/getting-help.html"
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
.box-analyze-nav {
  min-width: 240px;
}
.navbar-menu {
  background-color: transparent;
}
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
    }

    .navbar-dropdown-scrollable {
      overflow-y: scroll;
      max-height: 90vh;
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
