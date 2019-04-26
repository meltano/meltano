<template>
  <nav class="navbar is-info">
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
          class="navbar-item navbar-child">
          Configuration
        </router-link>

        <router-link
          :to="{name: 'transformations'}"
          class="navbar-item navbar-child">
          Transformations
        </router-link>

        <router-link
          :to="{name: 'orchestration'}"
          class="navbar-item navbar-child">
          Orchestration
        </router-link>

        <div
          class="navbar-item has-dropdown is-hoverable">
          <a class="navbar-link">
            Analyze
          </a>
          <div
            class="navbar-dropdown"
            :class="{'has-been-clicked': navbarClicked}">
            <template v-for="(v, model) in models">
              <div class="navbar-item navbar-title has-text-grey-light" :key="model">
                {{model | capitalize | underscoreToSpace}}
              </div>
              <router-link
                :to="urlForModelDesign(model, design)"
                class="navbar-item navbar-child"
                v-for="design in v['designs']"
                @click.native="menuSelected"
                :key="design">
                {{design | capitalize | underscoreToSpace}}
              </router-link>
            </template>
          </div>
        </div>

        <router-link to="/dashboards"
        class="navbar-item navbar-child">
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
import { mapState, mapGetters } from 'vuex';
import capitalize from '@/filters/capitalize';
import underscoreToSpace from '@/filters/underscoreToSpace';
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
  created() {
    this.$store.dispatch('repos/getModels');
  },
  data() {
    return {
      isMobileMenuOpen: false,
    };
  },
  filters: {
    capitalize,
    underscoreToSpace,
  },
  computed: {
    ...mapState('repos', [
      'models',
      'navbarClicked',
    ]),
    ...mapGetters('repos', [
      'urlForModelDesign',
    ]),
  },
  methods: {
    menuSelected() {
      this.$store.dispatch('repos/navbarHideDropdown');
      if (this.isMobileMenuOpen) {
        this.closeMobileMenu();
      }
    },
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
.navbar.is-info {
  background-color: transparent;

  .navbar-start .navbar-link,
  .navbar-start > .navbar-item {
    color: $interactive-navigation;
  }

  .navbar-start .navbar-link::after {
    border-color: $interactive-navigation;
  }

  .navbar-item.has-dropdown:hover .navbar-link,
  .navbar-brand > a.navbar-item:hover,
  .navbar-start > a.navbar-item.is-active,
  .navbar-start > a.navbar-item:hover {
    background: darken($app-background-color, 5%);
    color: $interactive-navigation;
  }
}
.navbar-item .navbar-child {
  padding-left: 1.5rem;
}
</style>
