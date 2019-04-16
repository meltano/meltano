<template>
  <router-view-layout-sidebar>

    <div slot='left'>

      <nav class="panel">
        <p class="panel-heading">
          Dashboards
        </p>

        <div class='panel-block'>
          <a class='button is-secondary is-fullwidth'
              @click="toggleNewDashboardModal">New Dashboard</a>
        </div>

        <div v-for="dashboard in dashboards"
            class='panel-block'
            :class="{'is-active': isActive(dashboard)}"
            :key="dashboard.id"
            @click="setDashboard(dashboard)">
          <div>
            <div>{{dashboard.name}}</div>
          </div>
        </div>

      </nav>

    </div>

    <div slot='right'>
      <h1>{{activeDashboard.name}}</h1>
      <h2 v-if="activeDashboard.description">{{activeDashboard.description}}</h2>
      <hr v-if="activeDashboardReports.length">
      <div
        class='box'
        v-for="report in activeDashboardReports"
        :key="report.id">
        <p>{{report.name}}</p>
        <chart :chart-type='report.chartType'
                :results='report.queryResults'
                :result-aggregates='report.queryResultAggregates'></chart>
      </div>

      <!-- New Dashboard Modal -->
      <NewDashboardModal v-if="isNewDashboardModalOpen" @close="toggleNewDashboardModal" />

    </div>

  </router-view-layout-sidebar>
</template>

<script>
import { mapState, mapActions } from 'vuex';
import Chart from '../components/designs/Chart';
import NewDashboardModal from '../components/dashboards/NewDashboardModal';
import RouterViewLayoutSidebar from '@/views/RouterViewLayoutSidebar';

export default {
  name: 'Dashboards',
  created() {
    this.initialize(this.$route.params.slug);
  },
  data() {
    return {
      isNewDashboardModalOpen: false,
    };
  },
  components: {
    Chart,
    NewDashboardModal,
    RouterViewLayoutSidebar,
  },
  computed: {
    ...mapState('dashboards', [
      'activeDashboard',
      'activeDashboardReports',
      'dashboards',
      'reports',
    ]),
  },
  methods: {
    ...mapActions('dashboards', [
      'initialize',
      'setDashboard',
      'getActiveDashboardReportsWithQueryResults',
    ]),
    isActive(dashboard) {
      return dashboard.id === this.activeDashboard.id;
    },
    toggleNewDashboardModal() {
      this.isNewDashboardModalOpen = !this.isNewDashboardModalOpen;
    },
  },
  watch: {
    activeDashboard() {
      this.getActiveDashboardReportsWithQueryResults();
    },
  },
};

</script>

<style lang="scss" scoped>
</style>
