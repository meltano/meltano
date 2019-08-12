<script>
import { mapState } from 'vuex'

import ConnectorLogo from '@/components/generic/ConnectorLogo'

export default {
  name: 'Entities',
  components: {
    ConnectorLogo
  },
  created() {
    this.$store.dispatch('plugins/getInstalledPlugins')
  },
  computed: {
    ...mapState('plugins', ['installedPlugins'])
  },
  methods: {
    udpateExtractorEntities(extractor) {
      this.$router.push({ name: 'extractorEntities', params: { extractor } })
    }
  }
}
</script>

<template>
  <div>
    <div class="columns">
      <div class="column is-three-fifths is-offset-one-fifth">
        <div class="content has-text-centered">
          <p class="level-item buttons">
            <a class="button is-small is-static is-marginless is-borderless">
              <span>Select all or a subset of the available data</span>
            </a>
            <span class="step-spacer">then</span>
            <a class="button is-small is-static is-marginless is-borderless">
              <span>Save your selection</span>
            </a>
          </p>
        </div>
      </div>
    </div>

    <div class="tile is-ancestor is-flex is-flex-wrap">
      <div
        class="tile is-parent is-3"
        v-for="(extractor, index) in installedPlugins.extractors"
        :key="`${extractor.name}-${index}`"
      >
        <div class="tile level is-child box">
          <div class="image level-item is-64x64 container">
            <ConnectorLogo :connector="extractor.name" />
          </div>
          <div class="content is-small">
            <p class="has-text-centered">
              {{ extractor.name }}
            </p>

            <a
              class="button is-interactive-primary is-block is-small"
              @click="udpateExtractorEntities(extractor.name)"
              >Edit Selections</a
            >
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<style lang="scss"></style>
