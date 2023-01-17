<script>
import { mapActions, mapGetters } from 'vuex'

import Dropdown from '@/components/generic/Dropdown'
import pluralize from 'pluralize'
import utils from '@/utils/utils'

export default {
  name: 'Plugin',
  components: {
    Dropdown,
  },
  props: {
    plugin: {
      type: Object,
      required: true,
    },
    type: {
      type: String,
      required: true,
    },
  },
  data() {
    return {
      isAdding: false,
    }
  },
  computed: {
    ...mapGetters('plugins', ['getIsInstallingPlugin', 'getIsPluginInstalled']),
    ...mapGetters('orchestration', [
      'getHasPipelineWithPlugin',
      'getPipelinesWithPlugin',
    ]),
    description() {
      return this.plugin.description || ''
    },
    label() {
      return this.plugin.label || ''
    },
    name() {
      return this.plugin.name
    },
    variants() {
      return this.plugin.variants
    },
    getPipelines() {
      return this.getPipelinesWithPlugin(this.singularizedType, this.name)
    },
    getPipelinesLabel() {
      const pipelineAmount = this.getPipelines.length
      return pluralize('pipeline', pipelineAmount, true)
    },
    getHasPipeline() {
      return this.getHasPipelineWithPlugin(this.singularizedType, this.name)
    },
    getPipelinesTooltip() {
      if (this.getHasPipeline) {
        const pipelineNames = this.getPipelines.map((el) => el.name)
        return pipelineNames.join(', ')
      } else {
        return 'Create a pipeline'
      }
    },
    getPipelinesRoute() {
      if (this.getHasPipeline) {
        return {
          name: 'pipelines',
        }
      }
      return {
        name: 'createPipelineSchedule',
        query: {
          [this.singularizedType]: this.name,
        },
      }
    },
    isInstalled() {
      return this.getIsPluginInstalled(this.type, this.name)
    },
    singularizedType() {
      return utils.singularize(this.type)
    },
    hasVariants() {
      return this.variants.length > 1
    },
  },
  methods: {
    ...mapActions('plugins', ['addPlugin', 'installPlugin']),
    goToSettings() {
      this.$router.push({
        name: `${this.singularizedType}Settings`,
        params: { plugin: this.name },
      })
    },
    addToProject(variant) {
      this.isAdding = true
      const addConfig = {
        pluginType: this.type,
        name: this.name,
        variant: variant && variant.name,
      }
      this.addPlugin(addConfig)
        .then(() => {
          this.goToSettings()
          this.$store.dispatch('plugins/getInstalledPlugins').then(() => {
            this.isAdding = false
          })
          this.installPlugin(addConfig)
        })
        .catch((err) => {
          this.$error.handle(err)
          this.isAdding = false
        })
    },
  },
}
</script>
<template>
  <div>
    <article class="media" :data-test-id="`${name}-extractor-card`">
      <figure class="media-left">
        <p class="image level-item is-48x48 container">
          <img :src="plugin.logoUrl" alt="" />
        </p>
      </figure>
      <div class="media-content">
        <div class="content">
          <p>
            <span class="has-text-weight-bold">{{ label || name }}</span>
            <br />
            <small>{{ description }}</small>
          </p>
          <div v-if="isInstalled" class="buttons">
            <button class="button" @click="goToSettings">
              <span>Configure</span>
            </button>

            <router-link
              class="button tooltip is-borderless"
              :data-tooltip="getPipelinesTooltip"
              tag="button"
              :to="getPipelinesRoute"
            >
              <span
                class="icon is-small"
                :class="getHasPipeline ? 'has-text-success' : 'has-text-danger'"
              >
                <font-awesome-icon
                  :icon="
                    getHasPipeline ? 'check-circle' : 'exclamation-triangle'
                  "
                ></font-awesome-icon>
              </span>
              <span>
                {{ getPipelinesLabel }}
              </span>
            </router-link>
          </div>
          <div
            v-else
            class="control"
            :class="{ 'field has-addons': hasVariants }"
          >
            <div class="control">
              <button
                class="button is-interactive-primary"
                :class="{
                  'is-loading': isAdding,
                }"
                :disabled="isAdding"
                @click="addToProject()"
              >
                <span>Add to project</span>
              </button>
            </div>

            <div v-if="hasVariants" class="control">
              <Dropdown
                :disabled="isAdding"
                button-classes="is-interactive-primary"
              >
                <div class="dropdown-content">
                  <a
                    v-for="variant in variants"
                    :key="variant.name"
                    class="dropdown-item"
                    data-dropdown-auto-close
                    @click="addToProject(variant)"
                  >
                    Add variant '{{ variant.name }}'

                    <template v-if="variant.default"> (default) </template>
                    <template v-else-if="variant.deprecated">
                      (deprecated)
                    </template>
                  </a>
                </div>
              </Dropdown>
            </div>
          </div>
        </div>
      </div>
    </article>
  </div>
</template>
