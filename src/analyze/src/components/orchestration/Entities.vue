<script>
import { mapGetters, mapState } from 'vuex';

export default {
  name: 'Entities',
  data() {
    return {
      filterExtractorsText: '',
    };
  },
  created() {
    this.$store.dispatch('orchestrations/getAll');
    this.$store.dispatch('orchestrations/getInstalledPlugins');
  },
  computed: {
    ...mapGetters('orchestrations', [
      'getExtractorImageUrl',
      'getExtractorNameWithoutPrefixedTapDash',
    ]),
    ...mapState('orchestrations', [
      'installedPlugins',
      'extractors',
    ]),
    filteredExtractors() {
      // Alphabetize filter (TODO: temp until getInstalledPlugins is alphabetical like getAll)
      const alphabetized = this.extractors.filter(
        extractor => this.installedPlugins.extractors.find(item => item.name === extractor));

      // Input filter
      if (this.filterExtractorsText) {
        return alphabetized.filter(item => item.indexOf(this.filterExtractorsText) > -1);
      }
      return alphabetized;
    },
  },
  methods: {
    udpateExtractorEntities(extractor) {
      this.$router.push({ name: 'extractorEntities', params: { extractor } });
    },
  },
};
</script>

<template>

  <div>

    <div class="columns">
      <div class="column is-4 is-offset-4">
        <input
          type="text"
          v-model="filterExtractorsText"
          placeholder="Filter installed extractors..."
          class="input connector-input">
      </div>
    </div>

    <div class="tile is-ancestor flex-and-wrap">
      <div
        class="tile is-parent is-3"
        v-for="(extractor, index) in filteredExtractors"
        :key="`${extractor}-${index}`">
        <div class="tile level is-child box">
          <div class="image level-item is-64x64 container">
            <img
              :src='getExtractorImageUrl(extractor)'
              :alt="`${getExtractorNameWithoutPrefixedTapDash(extractor)} logo`">
          </div>
          <div class="content is-small">
            <p class='has-text-centered'>
              {{extractor}}
            </p>

            <a
              class='button is-interactive-primary is-outlined is-block is-small'
              @click="udpateExtractorEntities(extractor)">Edit Selections</a>

          </div>
        </div>
      </div>
    </div>

  </div>

</template>

<style lang="scss">
</style>
