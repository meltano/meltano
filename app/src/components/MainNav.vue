<template>
  <nav class="navbar is-info">
    <div class="navbar-brand">
      <a class="navbar-item" href="#">
        <logo></logo>
      </a>
      <div class="navbar-burger burger" data-target="meltnavbar-transparent">
        <span></span>
        <span></span>
        <span></span>
      </div>
    </div>

    <div id="meltnavbar-transparent"
        class="navbar-menu">
      <div class="navbar-start">
        <a class="navbar-item" href="/">
          Home
        </a>
        <a class="navbar-item" href="/orchestrations">
          Orchestrate
        </a>
        <div class="navbar-item has-dropdown is-hoverable">
          <a class="navbar-link" href="#">
            Explore
          </a>
          <div class="navbar-dropdown
                is-boxed"
                :class="{'has-been-clicked': navbarClicked}">
            <template v-for="model in models">
            <div class="navbar-item navbar-title has-text-grey-light" :key="model.label">
              {{model | printable | capitalize | underscoreToSpace}}
            </div>
            <router-link :to="explore.link"
            class="navbar-item navbar-child"
            v-for="explore in model.explores"
            @click.native="menuSelected"
            :key="explore.view_label">
              {{explore.settings.label}}
            </router-link>
            </template>
          </div>
        </div>
        <router-link to="/repo" class="navbar-item">{{project.name}}</router-link>
      </div>
      <div class="navbar-end">
        <router-link to="/settings"
        class="navbar-item navbar-child">
          Settings
        </router-link>
      </div>
    </div>
  </nav>
</template>
<script>
import { mapState } from 'vuex';
import Logo from './Logo';

export default {
  name: 'MainNav',
  components: {
    Logo,
  },
  created() {
    this.$store.dispatch('projects/getProjects');
    this.$store.dispatch('repos/getModels');
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
    ...mapState('projects', [
      'project',
    ]),
    ...mapState('repos', [
      'models',
      'navbarClicked',
    ]),
  },

  methods: {
    menuSelected() {
      this.$store.dispatch('repos/navbarHideDropdown');
    },
  },
};
</script>
<style lang="scss">
.navbar.is-info {
  background: #464ACB;
}
.navbar-item .navbar-child {
  padding-left: 1.5rem;
}

.navbar-dropdown.is-boxed.has-been-clicked {
  // trick to unhover the menu dropdown
  display: none !important;
}
</style>
