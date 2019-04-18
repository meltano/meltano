<template>
  <router-view-layout>
    <div>
      <div class="tile projects is-ancestor">

        <div class="tile is-parent">
          <router-link
            :to="{name: 'start'}"
            class="tile is-child box">
            <div class="content">
              <h2 class="is-size-5 has-text-weight-bold">Create Project</h2>
              <p class='is-size-7'>A project is useful for grouping extractors, loaders, transformers, database connections, and orchestration in addition to reports and dashboards.</p>
            </div>
          </router-link>
        </div>

        <template v-if='hasProjects'>
          <div class="tile is-parent" v-for="project in projects" :key="project.name">
            <div class="tile is-child box">
              <div class="content">
                <h2 class="is-size-5 has-text-weight-bold">{{project.name}}</h2>
                <hr>
                <div class="columns is-mobile">
                  <div class="column is-one-fifth">
                    <router-link
                      :to="{name: 'dataSetup', params: {projectSlug: project.name}}"
                      class="button is-success">
                      Setup
                    </router-link>
                  </div>
                  <div class="column">
                    <div class="buttons is-right">
                      <router-link
                        :to="{name: 'analyze', params: {projectSlug: project.name}}"
                        class="button">
                        Analyze
                      </router-link>
                      <router-link
                        :to="{name: 'dashboards', params: {projectSlug: project.name}}"
                        class="button">
                        Dashboards
                      </router-link>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </template>

      </div>
    </div>

  </router-view-layout>
</template>
<script>
import { mapState, mapGetters, mapActions } from 'vuex';
import RouterViewLayout from '@/views/RouterViewLayout';

export default {
  mounted() {
    this.getProjects();
  },
  components: {
    RouterViewLayout,
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
