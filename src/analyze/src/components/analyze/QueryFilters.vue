<script>
import { mapState, mapGetters, mapActions } from 'vuex';

export default {
  name: 'QueryFilters',
  computed: {
    ...mapState('designs', [
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
  <div>Query Filters...</div>
</template>

<style lang="scss">
</style>
