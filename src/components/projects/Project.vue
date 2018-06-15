<template>
  <section class="section">
    <div class="container box" v-if="hasProjects">
      <h1 class="title">Projects</h1>
      <h2>Your projects</h2>
    </div>
    <div class="container box" v-else>
      <h1 class="title">Projects</h1>
      <h2>You don't have any projects yet.</h2>
      <a href="#" class="button is-primary">Add My Project</a>
    </div>
  </section>
</template>
<script>
import { mapState, mapGetters } from 'vuex';

export default {
  name: 'Project',
  created() {
    this.getProjects();
  },
  computed: {
    ...mapState({
      projects: state => state.projects.all,
    }),
    ...mapGetters('projects', {
      hasProjects: 'hasProjects',
    }),
  },
  methods: {
    getProjects() {
      this.$store.dispatch('projects/getProjects');
    },
  },
};
</script>
