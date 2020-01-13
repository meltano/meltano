<script>
import { mapGetters, mapState } from 'vuex'

import capitalize from '@/filters/capitalize'
import underscoreToSpace from '@/filters/underscoreToSpace'

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
    ...mapGetters('repos', ['hasModels', 'urlForModelDesign']),
    ...mapState('repos', ['models']),
    contextualModels() {
      const contextualModels = {}

      if (this.isDisplayContextualModels) {
        // Split based on '@' profiles convention
        const extractor = this.pipeline.extractor.split('@')[0]
        const namespace = this.getInstalledPlugin('extractors', extractor)
          .namespace
        for (const prop in this.models) {
          if (this.models[prop].plugin_namespace === namespace) {
            contextualModels[prop] = this.models[prop]
          }
        }
      }

      return contextualModels
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
    },
    getTargetModels() {
      return this.isDisplayContextualModels
        ? this.contextualModels
        : this.models
    },
    hasContextualModels() {
      return Object.keys(this.contextualModels).length > 0
    },
    isDisplayContextualModels() {
      return this.pipeline !== null
    },
    isShowNoModelsMessage() {
      return (
        !this.hasModels ||
        (this.isDisplayContextualModels && !this.hasContextualModels)
      )
    }
  }
}
</script>

<template>
  <div>
    <template v-if="isShowNoModelsMessage">
      <div class="box is-borderless is-shadowless is-marginless">
        <div class="content">
          <h3 class="is-size-6">
            No Models Installed
          </h3>
          <p>
            There are no models for this pipeline yet.
          </p>
          <p>
            <a
              href="https://www.meltano.com/docs/architecture.html#meltano-model"
              target="_blank"
              class="has-text-underlined"
              >Learn More</a
            >
          </p>
        </div>
      </div>
    </template>
    <template v-else>
      <div
        v-for="(model, modelKey) in getTargetModels"
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
            >{{ design | capitalize | underscoreToSpace }}</router-link
          >
        </div>
      </div>
    </template>
  </div>
</template>

<style lang="scss"></style>
