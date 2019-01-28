<template>
  <div class="container">
    <section class="section">
      <div class="columns">

        <nav class="panel column is-one-quarter">
          <p class="panel-heading">
            Dashboards
          </p>
          <div class="panel-block">
            <div class="inner-scroll text-selection-off">
              <ul>
                <li v-for="dashboard in dashboards"
                    :key="dashboard.id">
                  {{dashboard.name}}
                </li>
              </ul>
            </div>
          </div>
        </nav>

        <div class="column is-three-quarters">

        </div>

      </div>
    </section>
  </div>
</template>

<script>
import { mapState, mapActions } from 'vuex';

export default {
  name: 'Dashboards',
  created() {
    this.getDashboards();
  },
  computed: {
    ...mapState('dashboards', [
      'dashboards',
      'activeDashboard',
    ]),
  },
  methods: {
    ...mapActions('dashboards', [
      'getDashboards',
      'getDashboard',
    ]),
  },
};

</script>

<style lang="scss" scoped>

</style>
