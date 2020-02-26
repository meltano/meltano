<script>
import { mapActions, mapState } from 'vuex'

export default {
  name: 'Explore',
  data() {
    return {
      title: 'Explore',
      hasLoadedReports: false
    }
  },
  computed: {
    ...mapState('reports', ['reports'])
  },
  created() {
    this.loadReports().then(() => (this.hasLoadedReports = true))
  },
  methods: {
    ...mapActions('reports', ['loadReports'])
  }
}
</script>

<template>
  <div>
    <h2 id="explore" class="title">{{ title }}</h2>

    <div class="columns">
      <!-- Report Templates -->
      <div class="column">
        <div class="content">
          <h3 id="report-templates" class="title">Report Templates</h3>
        </div>
        <div class="box">
          <progress v-if="true" class="progress is-small is-info"></progress>
          <template v-else>
            ...
          </template>
        </div>
      </div>

      <!-- Reports -->
      <div class="column">
        <div class="content">
          <h3 id="reports" class="title">Reports</h3>
        </div>
        <div class="box">
          <progress
            v-if="!hasLoadedReports"
            class="progress is-small is-info"
          ></progress>
          <template v-else-if="reports.length">
            <a v-for="report in reports" :key="report.name">
              {{ report.name }}
            </a>
          </template>
          <template v-else>
            <div class="content"><p>No reports</p></div>
          </template>
        </div>
      </div>

      <!-- Dashboards -->
      <div class="column">
        <div class="content">
          <h3 id="dashboards" class="title">Dashboards</h3>
        </div>
        <div class="box">
          <progress v-if="true" class="progress is-small is-info"></progress>
          <template v-else>
            ...
          </template>
        </div>
      </div>
    </div>
  </div>
</template>

<style lang="scss"></style>
