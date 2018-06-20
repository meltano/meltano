<template>
  <section class="section">
    <div class="container box" v-if="hasProjects">
      <h1 class="title">Project</h1>
      <div class="field is-horizontal">
        <div class="field-label is-normal">
          <label class="label">Name</label>
        </div>
        <div class="field-body">
          <div class="field">
            <p class="control">
              <input class="input is-static" v-model="project.name" readonly>
            </p>
          </div>
        </div>
      </div>
      <div class="field is-horizontal">
        <div class="field-label is-normal">
          <label class="label">Git URL</label>
        </div>
        <div class="field-body">
          <div class="field">
            <p class="control">
              <input class="input is-static" v-model="project.git_url" readonly>
            </p>
          </div>
        </div>
      </div>
      <router-link to="/repo" class="button">Go to Repo</router-link>
    </div>
    <div class="container box" v-else="">
      <h1 class="title">Project</h1>
      <h2>You don't have a project yet.</h2>
      <router-link to="/project/new" class="button is-primary">Add New Project</router-link>
    </div>
  </section>
</template>
<script>
import { mapState, mapGetters } from 'vuex';

export default {
  name: 'Project',
  created() {
    this.getProjects(true);
  },
  computed: {
    ...mapState('projects', {
      project: state => state.project,
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
