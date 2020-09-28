<script>
import { mapActions, mapGetters } from 'vuex'

import ConnectorLogo from '@/components/generic/ConnectorLogo'
import pluralize from 'pluralize'
import utils from '@/utils/utils'

export default {
  name: 'Plugin',
  components: {
    ConnectorLogo
  },
  props: {
    plugin: {
      type: Object,
      required: true
    },
    type: {
      type: String,
      required: true
    }
  },
  data() {
    return {
      isAdding: false
    }
  },
  computed: {
    ...mapGetters('plugins', ['getIsInstallingPlugin', 'getIsPluginInstalled']),
    ...mapGetters('orchestration', [
      'getHasPipelineWithPlugin',
      'getPipelinesWithPlugin'
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
    getPipelines() {
      return this.getPipelinesWithPlugin(this.singularizedType, this.name)
    },
    getPipelinesLabel() {
      const pipelineAmount = this.getPipelines.length
      return pluralize('pipeline', pipelineAmount, true)
    },
    getButtonLabel() {
      return this.isInstalled ? 'Configure' : 'Add to project'
    },
    getHasPipeline() {
      return this.getHasPipelineWithPlugin(this.singularizedType, this.name)
    },
    getPipelinesTooltip() {
      if (this.getHasPipeline) {
        const pipelineNames = this.getPipelines.map(el => el.name)
        return pipelineNames.join(', ')
      } else {
        return 'Create a pipeline'
      }
    },
    getPipelinesRoute() {
      if (this.getHasPipeline) {
        return {
          name: 'pipelines'
        }
      }
      return {
        name: 'createPipelineSchedule',
        query: {
          [this.singularizedType]: this.name
        }
      }
    },
    isInstalled() {
      return this.getIsPluginInstalled(this.type, this.name)
    },
    singularizedType() {
      return utils.singularize(this.type)
    }
  },
  methods: {
    ...mapActions('plugins', ['addPlugin', 'installPlugin']),
    goToSettings() {
      this.$router.push({
        name: `${this.singularizedType}Settings`,
        params: { plugin: this.name }
      })
    },
    handleClick() {
      if (this.isInstalled) {
        this.goToSettings()
      } else {
        this.isAdding = true
        const addConfig = {
          pluginType: this.type,
          name: this.name
        }
        this.addPlugin(addConfig)
          .then(() => {
            this.goToSettings()
            this.$store.dispatch('plugins/getInstalledPlugins').then(() => {
              this.isAdding = false
            })
            this.installPlugin(addConfig)
          })
          .catch(err => {
            this.$error.handle(err)
            this.close()
          })
      }
    }
  }
}
</script>
<template>
  <div>
    <article class="media" :data-test-id="`${name}-extractor-card`">
      <figure class="media-left">
        <p class="image level-item is-48x48 container">
          <ConnectorLogo :connector="name" />
        </p>
      </figure>
      <div class="media-content">
        <div class="content">
          <p>
            <span class="has-text-weight-bold">{{ label || name }}</span>
            <br />
            <small>{{ description }}</small>
          </p>
          <div class="buttons">
            <button
              class="button"
              :class="{
                'is-interactive-primary': !isInstalled,
                'is-loading': isAdding,
                disabled: isAdding
              }"
              @click="handleClick"
            >
              <span>{{ getButtonLabel }}</span>
            </button>
            <router-link
              v-if="isInstalled"
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
        </div>
      </div>
    </article>
  </div>
</template>
