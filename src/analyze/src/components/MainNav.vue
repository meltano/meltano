<template>
  <nav class="navbar is-info">
    <div class="navbar-brand">
      <a class="navbar-item" href="#">
        <logo></logo>
      </a>
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
        <router-link to="/" class="navbar-item navbar-child">
          Files
        </router-link>

        <div class="navbar-item has-dropdown is-hoverable">
          <a class="navbar-link">
            Analyze
          </a>
          <div class="navbar-dropdown
                is-boxed"
                :class="{'has-been-clicked': navbarClicked}">
            <template v-for="(v,model) in models">
            <div class="navbar-item navbar-title has-text-grey-light" :key="model">
              {{model | capitalize | underscoreToSpace}}
            </div>
            <router-link :to="urlForModelDesign(model, design)"
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
        <div v-if="$auth.authenticated()"
             class="navbar-item has-dropdown is-hoverable">
          <div class="navbar-link">
            <Profile />
          </div>
          <div class="navbar-dropdown is-boxed">
            <a class="navbar-item navbar-child"
               @click.capture="$auth.logout()">
              Logout
            </a>
          </div>
        </div>

        <div class="navbar-item has-dropdown is-hoverable">
          <div class="navbar-link">
            Settings
          </div>
          <div class="navbar-dropdown is-boxed">
            <router-link to="/settings/database"
                         class="navbar-item navbar-child">
              Database
            </router-link>
            <router-link to="/settings/roles"
                         class="navbar-item navbar-child">
              Roles
            </router-link>
          </div>
        </div>
      </div>
    </div>
  </nav>
</template>
<script>
import { mapState, mapGetters } from 'vuex';
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
    printable(value) {
      return value.label ? value.label : value.name;
    },
    underscoreToSpace(value) {
      return value.replace(/_/g, ' ');
    },
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

.navbar.is-info {
  background: $primary;
  .navbar-start > a.navbar-item.is-active,
  .navbar-start > a.navbar-item:hover {
    background: darken($primary, 20%);
  }
}
.navbar-item .navbar-child {
  padding-left: 1.5rem;
}
.navbar-dropdown.is-boxed.has-been-clicked {
  // trick to unhover the menu dropdown
  display: none !important;
}
</style>
