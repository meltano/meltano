<template>
  <section class="section">
    <form class="container box">
      <h2>New Project</h2>
      <div class="field">
        <label class="label">Name
        <div class="control">
          <input class="input" type="text" v-model="name" placeholder="Project Name">
        </div>
        </label>
      </div>
      <div class="field">
        <label class="label">URL
        <div class="control">
          <input class="input" type="text" v-model="git_url" placeholder="Git URL">
        </div>
        </label>
      </div>
      <div class="field is-grouped">
        <div class="control">
          <button class="button is-link" @click.prevent="saveProject">Save</button>
        </div>
        <div class="control">
          <router-link class="button is-text" to="/projects">Cancel</router-link>
        </div>
      </div>
    </form>
  </section>
</template>
<script>
export default {
  name: 'NewProjectForm',
  data() {
    return {
      name: 'GitLab',
      git_url: '/Users/jacobschatz/projects/looker',
    };
  },
  methods: {
    saveProject() {
      this.$store.dispatch('projects/saveProject', {
        name: this.name,
        git_url: this.git_url,
      });
    },
  },
};
</script>
