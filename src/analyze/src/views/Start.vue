<template>
  <div class="section container">
    <div class="box">
      <h1 class="title is-4 has-text-centered">New Meltano Project</h1>
      <div class="field">
        <label class="label">Project Name</label>
        <div class="control">
          <input class="input"
            type="text"
            @input="projectNameInput"
            :disabled="!cwdLoaded"
            :value="project"
            placeholder="Project Name"
            :class="{'is-danger': exists}">
          <span class="has-text-danger"
            v-if="exists">Directory
            <code>{{existingPath}}</code>
          exists</span>
        </div>
      </div>
      <div class="field">
        <label class="label">Project Location</label>
        <div class="control">
          <input class="input"
            type="text"
            disabled="disabled"
            :value="cwd"
            placeholder="Project Name">
        </div>
      </div>
      <div class="field">
        <div class="control">
          <button
            class="button is-primary"
            @click.prevent="createProjectClicked"
            :disabled="exists">
            Create Project
          </button>
        </div>
      </div>
    </div>
  </div>
</template>
<script>
import { mapState, mapActions } from 'vuex';

export default {
  mounted() {
    this.getCwd();
  },
  computed: {
    ...mapState('projects', [
      'project',
      'cwdLoaded',
      'cwd',
      'exists',
      'existingPath',
    ]),
  },
  methods: {
    ...mapActions('projects', [
      'getCwd',
    ]),

    createProjectClicked() {
      this.$store.dispatch('projects/createProject')
        .then((data) => {
          if (data.data.result) {
            this.$router.push({ name: 'projectFiles', params: { projectSlug: data.data.project } });
          }
        })
        .catch(() => {});
    },

    projectNameInput(e) {
      this.$store.dispatch('projects/projectNameChanged', e.currentTarget.value);
    },
  },
};
</script>
