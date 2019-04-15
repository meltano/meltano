<template>
  <nav class="navbar is-info">
    <div class="navbar-brand">
      <router-link
          :to="{name: 'projects'}"
          class="navbar-item navbar-child">
        <logo></logo>
      </router-link>
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

        <div class="navbar-item navbar-child">
          <span v-if="currentProjectSlug">
            <em>{{currentProjectSlug}}</em>
          </span>
          <span v-else>Projects</span>
        </div>

        <router-link
          v-if="currentProjectSlug"
          :to="{name: 'connectors', params: { projectSlug: currentProjectSlug }}"
          class="navbar-item navbar-child">
          Connectors
        </router-link>

        <router-link
          v-if="currentProjectSlug"
          :to="{name: 'transformations', params: { projectSlug: currentProjectSlug }}"
          class="navbar-item navbar-child">
          Transformations
        </router-link>

        <router-link
          v-if="currentProjectSlug"
          :to="{name: 'orchestration', params: { projectSlug: currentProjectSlug }}"
          class="navbar-item navbar-child">
          Orchestration
        </router-link>

        <router-link
          v-if="currentProjectSlug"
          :to="{name: 'analyze', params: { projectSlug: currentProjectSlug }}"
          class="navbar-item navbar-child">
          Analyze
        </router-link>

        <router-link
          v-if="currentProjectSlug"
          :to="{name: 'dashboards', params: { projectSlug: currentProjectSlug }}"
          class="navbar-item navbar-child">
          Dashboards
        </router-link>

      </div>
      <div class="navbar-end">
        <div v-if="$auth.user"
             class="navbar-item has-dropdown is-hoverable">
          <div class="navbar-link">
            @{{ $auth.user.username }}
          </div>
          <div class="navbar-dropdown is-boxed">
            <a class="navbar-item navbar-child"
               @click.capture="$auth.logout()">
              Logout
            </a>
          </div>
        </div>
        <div
          v-if="currentProjectSlug"
          class="navbar-item has-dropdown is-hoverable">
          <div class="navbar-link">
            Settings
          </div>
          <div class="navbar-dropdown is-boxed">
            <router-link :to="{name:'database', params: { projectSlug: currentProjectSlug }}"
                         class="navbar-item navbar-child">
              Database
            </router-link>
            <router-link :to="{name:'connectors', params: { projectSlug: currentProjectSlug }}"
                         class="navbar-item navbar-child">
              Connectors
            </router-link>
          </div>
        </div>
      </div>
    </div>
  </nav>
</template>
<script>
import { mapState } from 'vuex';
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
      design: '',
      model: '',
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
    ...mapState('projects', [
      'currentProjectSlug',
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
