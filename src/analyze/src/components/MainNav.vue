<template>
  <nav class="navbar is-transparent">
    <div class="navbar-brand">
      <div class="navbar-item navbar-child">
        <logo></logo>
      </div>
      <div class="navbar-burger burger"
           :class="{'is-active': isMobileMenuOpen}"
           data-target="meltnavbar-transparent"
           @click="mobileMenuClicked">
        <span></span>
        <span></span>
        <span></span>
      </div>
    </div>

    <div id="meltnavbar-transparent"
         class="navbar-menu"
         :class="{'is-active': isMobileMenuOpen}">
      <div class="navbar-start">

        <router-link
          :to="{name: 'dataSetup'}"
          class="navbar-item navbar-child has-text-weight-semibold">
          Configuration
        </router-link>

        <router-link
          :to="{name: 'transformations'}"
          class="navbar-item navbar-child has-text-weight-semibold">
          Transformations
        </router-link>

        <router-link
          :to="{name: 'orchestration'}"
          class="navbar-item navbar-child has-text-weight-semibold">
          Orchestration
        </router-link>

        <router-link
          :to="{name: 'analyze'}"
          class="navbar-item navbar-child has-text-weight-semibold">
          Analyze
        </router-link>

        <router-link to="/dashboards"
          class="navbar-item navbar-child has-text-weight-semibold">
          Dashboards
        </router-link>

      </div>

      <div class="navbar-end">
        <div class="navbar-item navbar-child">
          <font-awesome-icon
            :icon="'user'"
            :style="{ color: '#0F3B66' }"
            title="Login currently disabled"></font-awesome-icon>
        </div>
      </div>

    </div>
  </nav>
</template>
<script>
import Logo from './Logo';
import Profile from './Profile';

export default {
  name: 'MainNav',
  components: {
    Logo,
    Profile,
  },
  watch: {
    $route() {
      if (this.isMobileMenuOpen) {
        this.closeMobileMenu();
      }
    },
  },
  data() {
    return {
      isMobileMenuOpen: false,
    };
  },
  methods: {
    mobileMenuClicked() {
      this.isMobileMenuOpen = !this.isMobileMenuOpen;
    },
    closeMobileMenu() {
      this.isMobileMenuOpen = false;
    },
  },
};
</script>
<style lang="scss">
@import '@/scss/bulma-preset-overrides.scss';

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
    border-bottom: 1px solid transparent;

    &.router-link-active {
      color: $interactive-navigation;
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
</style>
