<script>
import { mapGetters } from 'vuex'
import ConnectorLogo from '@/components/generic/ConnectorLogo'

export default {
  name: 'ExtractorList',
  components: {
    ConnectorLogo
  },
  computed: {
    ...mapGetters('plugins', [
      'visibleExtractors',
      'getIsAddingPlugin',
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
    <div class="box is-borderless is-shadowless is-marginless">
      <progress
        v-if="isLoadingExtractors"
        class="progress is-small is-info"
      ></progress>

      <div v-else>
        <article
          v-for="(extractor, index) in visibleExtractors"
          :key="`${extractor.name}-${index}`"
          class="media has-cursor-pointer"
          :data-test-id="`${extractor.name}-extractor-card`"
          data-dropdown-auto-close
          @click="updateExtractorSettings(extractor.name)"
        >
          <figure class="media-left">
            <p class="image level-item is-48x48 container">
              <ConnectorLogo :connector="extractor.name" />
            </p>
          </figure>
          <div class="media-content">
            <div class="content">
              <p>
                <strong>{{ extractor.name }}</strong>
                <br />
                <small>{{ extractor.description }}</small>
              </p>
            </div>
          </div>
        </article>
      </div>
      <progress
        v-if="!visibleExtractors"
        class="progress is-small is-info"
      ></progress>
    </div>
  </div>
</template>

<style lang="scss"></style>
