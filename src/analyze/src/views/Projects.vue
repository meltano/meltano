<template>
  <div class="section">
    <h1 class="title is-4 has-text-centered">Projects</h1>
    <div class="tile projects is-ancestor">
      <div class="tile is-parent is-3" v-for="project in projects" :key="project.name">
        <router-link
          :to="{name: 'projectFiles', params: {slug: project.name}}"
          class="tile project is-child box">
          <h2 class="is-5">{{project.name}}</h2>
        </router-link>
      </div>
      <div class="tile is-parent is-3">
        <router-link
          :to="{name: 'start'}"
          class="tile project is-child box">
          <h2 class="is-5">Create project</h2>
        </router-link>
      </div>
    </div>
  </div>
</template>
<script>
import { mapState, mapGetters, mapActions } from 'vuex';

export default {
  mounted() {
    this.getProjects();
  },
  computed: {
    ...mapGetters('projects', [
      'hasProjects',
    ]),
    ...mapState('projects', [
      'projects',
    ]),
  },

  methods: {
    ...mapActions('projects', [
      'getProjects',
    ]),
  },
};
</script>
<style lang="scss">
.projects {
  flex-wrap: wrap;
}
</style>
