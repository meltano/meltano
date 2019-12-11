<script>
import { mapGetters } from 'vuex'
import ConnectorLogo from '@/components/generic/ConnectorLogo'
import SpeedRunIcon from '@/components/pipelines/SpeedRunIcon'

export default {
  name: 'Extractors',
  components: {
    ConnectorLogo,
    SpeedRunIcon
  },
  data: () => ({
    speedRunExtractor: 'tap-carbon-intensity'
  }),
  computed: {
    ...mapGetters('plugins', [
      'visibleExtractors',
      'getIsAddingPlugin',
      'getIsPluginInstalled',
      'getIsInstallingPlugin'
    ]),
    isLoadingExtractors() {
      return this.visibleExtractors && this.visibleExtractors.length === 0
    }
  },
  methods: {
    updateExtractorSettings(extractor) {
      this.$router.push({ name: 'extractorSettings', params: { extractor } })
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
              <span>Tell us which extractor(s) to install</span>
            </a>
            <span class="step-spacer">then</span>
            <a class="button is-small is-static is-marginless is-borderless">
              <span>Configure and save their settings</span>
            </a>
          </p>
        </div>
      </div>
    </div>

    <progress
      v-if="isLoadingExtractors"
      class="progress is-small is-info"
    ></progress>

    <div v-else class="tile is-ancestor is-flex is-flex-wrap">
      <div
        v-for="(extractor, index) in visibleExtractors"
        :key="`${extractor.name}-${index}`"
        :data-test-id="`${extractor.name}-extractor-card`"
        class="tile is-parent is-3 is-relative"
      >
        <SpeedRunIcon v-if="extractor.name === speedRunExtractor" />
        <div class="tile level is-child box">
          <div class="image level-item is-64x64 container">
            <ConnectorLogo
              :connector="extractor.name"
              :is-grayscale="
                !getIsPluginInstalled('extractors', extractor.name)
              "
            />
          </div>
          <div class="content is-small">
            <p class="has-text-centered has-text-weight-semibold">
              {{ extractor.name }}
            </p>
            <p class="has-text-centered">
              {{ extractor.description }}
            </p>

            <template v-if="getIsPluginInstalled('extractors', extractor.name)">
              <div class="columns is-variable is-1">
                <div class="column">
                  <a
                    class="button is-interactive-primary is-small is-block"
                    @click="updateExtractorSettings(extractor.name)"
                    >Configure</a
                  >
                </div>
              </div>
            </template>
            <template v-else>
              <a
                :class="{
                  'is-loading':
                    getIsAddingPlugin('extractors', extractor.name) ||
                    getIsInstallingPlugin('extractors', extractor.name)
                }"
                class="button is-interactive-primary is-outlined is-block is-small"
                @click="updateExtractorSettings(extractor.name)"
                >Install</a
              >
            </template>
          </div>
        </div>
      </div>
    </div>
    <progress
      v-if="!visibleExtractors"
      class="progress is-small is-info"
    ></progress>
  </div>
</template>

<style lang="scss"></style>
