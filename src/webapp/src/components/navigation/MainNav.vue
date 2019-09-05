<script>
import { mapGetters } from 'vuex'

import utils from '@/utils/utils'

import Logo from '@/components/navigation/Logo'

export default {
  name: 'MainNav',
  components: {
    Logo
  },
  data() {
    return {
      isMobileMenuOpen: false
    }
  },
  computed: {
    ...mapGetters('configuration', ['getRunningPipelineJobsCount']),
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
    goToSchedules() {
      this.$router.push({ name: 'schedules' })
    },
    mobileMenuClicked() {
      this.isMobileMenuOpen = !this.isMobileMenuOpen
    },
    closeMobileMenu() {
      this.isMobileMenuOpen = false
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
          class="meltano-label is-uppercase has-text-weight-bold has-text-primary ml-half-r"
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
        <router-link
          :to="{ name: 'dataSetup' }"
          :class="{ 'router-link-active': getIsSubRouteOf('/pipelines') }"
          class="navbar-item navbar-child has-text-weight-semibold"
        >
          <a
            class="button has-background-transparent is-borderless is-paddingless"
            :class="{
              'has-text-interactive-navigation': getIsSubRouteOf('/pipelines')
            }"
          >
            <span class="icon is-small" :class="getIconColor('/pipelines')">
              <font-awesome-icon icon="th-list"></font-awesome-icon>
            </span>
            <span>Pipeline</span>
            <span
              v-if="getRunningPipelineJobsCount > 0"
              class="tag tag-running-pipelines is-rounded is-info"
              @click.prevent="goToSchedules"
            >
              {{ getRunningPipelineJobsCount }}
            </span>
          </a>
        </router-link>

        <router-link
          :to="{ name: 'orchestration' }"
          :class="{ 'router-link-active': getIsSubRouteOf('/orchestration') }"
          class="navbar-item navbar-child has-text-weight-semibold"
        >
          <a
            class="button has-background-transparent is-borderless is-paddingless"
            :class="{
              'has-text-interactive-navigation': getIsSubRouteOf(
                '/orchestration'
              )
            }"
          >
            <span class="icon is-small" :class="getIconColor('/orchestration')">
              <font-awesome-icon icon="project-diagram"></font-awesome-icon>
            </span>
            <span>Orchestrate</span>
          </a>
        </router-link>

        <div class="navbar-item has-dropdown is-hoverable">
          <router-link
            :to="{ name: 'analyze' }"
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
          </router-link>

          <div class="navbar-dropdown">
            <router-link :to="{ name: 'analyzeModels' }" class="navbar-item"
              :class="{ 'is-active': getIsCurrentPath('/analyze/models') }"
              >Models</router-link
            >
            <router-link :to="{ name: 'analyzeSettings' }" class="navbar-item"
              :class="{ 'is-active': getIsCurrentPath('/analyze/settings') }"
              >Connections</router-link
            >
          </div>
        </div>

        <router-link
          :to="{ name: 'dashboards' }"
          :class="{ 'router-link-active': getIsSubRouteOf('/dashboards') }"
          class="navbar-item navbar-child has-text-weight-semibold"
        >
          <a
            class="button has-background-transparent is-borderless is-paddingless"
            :class="{
              'has-text-interactive-navigation': getIsSubRouteOf('/dashboards')
            }"
          >
            <span class="icon is-small" :class="getIconColor('/dashboards')">
              <font-awesome-icon icon="th-large"></font-awesome-icon>
            </span>
            <span>Dashboard</span>
          </a>
        </router-link>
      </div>

      <div class="navbar-end">
        <div class="navbar-item navbar-child">
          <a
            class="button has-background-light tooltip is-tooltip-warning is-tooltip-multiline is-tooltip-left"
            data-tooltip="This feature is queued. Feel free to contribute at gitlab.com/meltano/meltano/issues."
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
.navbar-project-label {
  padding-right: 1.2rem;
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
.navbar-item .navbar-child {
  padding-left: 1.5rem;
}
.tag-running-pipelines {
  margin-left: 0.5rem;
}
</style>
