<template>
  <div class="container">
    <section class="section">
      <div class="columns">
        <nav class="panel column is-one-quarter">
          <p class="panel-heading">
            Dashboards
          </p>
          <div class="inner-scroll text-selection-off">

          </div>
        </nav>
      </div>
    </section>
  </div>
</template>

<script>
import { mapState, mapGetters, mapActions } from 'vuex';

export default {
  name: 'Dashboards',
  computed: {
    ...mapState('dashboards', [
      'dashboards',
      'activeDashboard',
    ]),
    ...mapGetters('dashboards', [

    ]),
  },
  methods: {
    ...mapActions('dashboards', [
      'getDashboard',
    ]),
  }
}



</script>

<style lang="scss" scoped>

</style>