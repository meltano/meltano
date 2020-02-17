<script>
import ReportEmbed from '@/components/embeds/ReportEmbed'

export default {
  name: 'DashboardEmbed',
  components: {
    ReportEmbed
  },
  props: {
    dashboard: { type: Object, default: null },
    reportsWithQueryResults: { type: Array, default: null }
  }
}
</script>

<template>
  <div>
    <div class="columns is-vcentered">
      <div class="column">
        <h2 class="title">{{ dashboard.name }}</h2>
        <h3 v-if="dashboard.description" class="subtitle">
          {{ dashboard.description }}
        </h3>
      </div>
    </div>

    <div v-if="reportsWithQueryResults.length" class="columns is-multiline">
      <div
        v-for="report in reportsWithQueryResults"
        :key="report.id"
        class="column is-half"
      >
        <div class="box">
          <ReportEmbed :report="report" />
        </div>
      </div>
    </div>

    <div v-else class="columns">
      <div class="column">
        <div class="box">
          <div class="content">
            <p>No reports yet...</p>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<style lang="scss"></style>
