<script>
import { mapGetters, mapState } from 'vuex'

import capitalize from '@/filters/capitalize'
import underscoreToSpace from '@/filters/underscoreToSpace'
import utils from '@/utils/utils'

export default {
  name: 'AnalyzeList',
  filters: {
    capitalize,
    underscoreToSpace
  },
  props: {
    pipeline: { type: Object, required: false, default: null }
  },
  computed: {
    ...mapGetters('orchestration', ['getSuccessfulPipelines']),
    ...mapGetters('plugins', ['getInstalledPlugin', 'visibleExtractors']),
    ...mapGetters('repos', ['urlForModelDesign']),
    ...mapState('repos', ['models']),
    contextualModels() {
      // Default to all unless pipeline is provided for contextual display
      let models = this.models

      // Contextual dropdown based on specific pipeline
      if (this.pipeline) {
        // Split based on '@' profiles convention
        const extractor = this.pipeline.extractor.split('@')[0]
        const namespace = this.getInstalledPlugin('extractors', extractor)
          .namespace
        const filteredModels = {}
        for (const prop in models) {
          if (models[prop].plugin_namespace === namespace) {
            filteredModels[prop] = models[prop]
          }
        }

        // Fallback to all if no match
        models =
          Object.keys(filteredModels).length === 0
            ? this.models
            : filteredModels
      }

      return models
    },
    getIsModelEnabled() {
      return model => {
        if (!this.getSuccessfulPipelines || !this.visibleExtractors) {
          return false
        }

        const matchedPlugins = this.visibleExtractors.filter(extractor => {
          return this.getSuccessfulPipelines.find(
            pipeline => pipeline.extractor === extractor.name
          )
        })

        return matchedPlugins.find(
          plugin => plugin.namespace === model.plugin_namespace
        )
      }
    }
  },
  methods: {
    prepareAnalyzeLoader(model, design) {
      if (this.pipeline) {
        localStorage.setItem(
          utils.concatLoaderModelDesign(model, design),
          this.pipeline.loader
        )
      }
    }
  }
}
</script>

<template>
  <div>
    <div
      v-for="(model, modelKey) in contextualModels"
      :key="`${modelKey}-panel`"
      class="box box-analyze-nav is-borderless is-shadowless is-marginless"
    >
      <div class="content">
        <h3 class="is-size-6">
          {{ model.name | capitalize | underscoreToSpace }}
        </h3>
        <h4 class="is-size-7 has-text-grey">
          {{ model.namespace }}
        </h4>
      </div>
      <div class="buttons">
        <router-link
          v-for="design in model['designs']"
          :key="design"
          class="button is-small is-interactive-primary is-outlined"
          :disabled="!getIsModelEnabled(model)"
          :to="urlForModelDesign(modelKey, design)"
          @click.native="prepareAnalyzeLoader(model.name, design)"
          >{{ design | capitalize | underscoreToSpace }}</router-link
        >
      </div>
    </div>
  </div>
</template>

<style lang="scss"></style>
