<script>
import { mapState, mapGetters, mapActions } from 'vuex';

export default {
  name: 'QueryFilters',
  computed: {
    ...mapState('designs', [
      'filterOptions',
      'filters',
    ]),
    ...mapGetters('designs', [
      'hasFilters',
    ]),
  },
  methods: {
    ...mapActions('designs', [
      'toggleFilter',
      'removeFilter',
    ]),
  },
};
</script>

<template>
  <div>
    <div>{{filterOptions}}</div>
  </div>
</template>

<style lang="scss">
</style>
