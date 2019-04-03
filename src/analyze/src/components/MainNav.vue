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
        <router-link
          :to="{name: 'projects'}"
          class="navbar-item navbar-child">Projects</router-link>
        <router-link
          v-if="slug"
          :to="{name: 'projectFiles', params: {slug: slug}}"
          class="navbar-item navbar-child">
          Files
        </router-link>

        <div class="navbar-item has-dropdown is-hoverable">
          <a class="navbar-link" v-if="slug">
            Analyze
          </a>
          <div class="navbar-dropdown
                is-boxed"
                :class="{'has-been-clicked': navbarClicked}">
            <template v-for="(v,model) in models">
            <div class="navbar-item navbar-title has-text-grey-light" :key="model">
              {{model | capitalize | underscoreToSpace}}
            </div>
            <router-link
              :to="{name:'analyze',
                    params:
                      {
                        slug: slug,
                        model: model,
                        design: design
                      }
                    }"
            class="navbar-item navbar-child"
            v-for="design in v['designs']"
            @click.native="menuSelected"
            :key="design">
              {{design | capitalize | underscoreToSpace}}
            </router-link>
            </template>
          </div>
        </div>

        <router-link
          v-if="slug"
          to="/dashboards"
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
          v-if="slug"
          class="navbar-item has-dropdown is-hoverable">
          <div class="navbar-link">
            Settings
          </div>
          <div class="navbar-dropdown is-boxed">
            <router-link :to="{name:'database', params: {slug}}"
                         class="navbar-item navbar-child">
              Database
            </router-link>
          </div>
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
      this.slug = this.$route.params.slug;
      if (this.isMobileMenuOpen) {
        this.closeMobileMenu();
      }
    },
  },
  created() {
    this.$store.dispatch('repos/getModels');
    this.slug = this.$route.params.slug;
  },
  data() {
    return {
      isMobileMenuOpen: false,
      slug: '',
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
