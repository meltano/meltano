<script>
import { mapActions, mapGetters } from 'vuex'
import utils from '@/utils/utils'

import PluginList from '@/components/pipelines/PluginList'
import RouterViewLayout from '@/views/RouterViewLayout'

export default {
  name: 'Plugins',
  components: {
    PluginList,
    RouterViewLayout,
  },
  props: {
    pluginType: {
      type: String,
      required: true,
    },
  },
  data() {
    return {
      isLoading: true,
    }
  },
  computed: {
    ...mapGetters('plugins', [
      'availablePluginsOfType',
      'installedPluginsOfType',
    ]),
    availablePlugins() {
      return this.availablePluginsOfType(this.pluginType)
    },
    installedPlugins() {
      return this.installedPluginsOfType(this.pluginType)
    },
    getModalName() {
      return this.$route.name
    },
    getTitle() {
      return utils.titleCase(this.pluginType)
    },
    isModal() {
      return this.$route.meta.isModal
    },
    singularizedType() {
      return utils.singularize(this.pluginType)
    },
  },
  created() {
    Promise.all([this.getInstalledPlugins(), this.getPipelineSchedules()]).then(
      () => {
        this.isLoading = false
      }
    )
  },
  methods: {
    ...mapActions('orchestration', ['getPipelineSchedules']),
    ...mapActions('plugins', ['getInstalledPlugins']),
  },
}
</script>

<template>
  <router-view-layout>
    <div class="container view-body is-widescreen">
      <h2 id="data" class="title">{{ getTitle }}</h2>

      <div class="columns">
        <div class="column">
          <div class="box content">
            <progress
              v-if="isLoading"
              class="progress is-small is-info"
            ></progress>
            <template v-else>
              <template v-if="installedPlugins.length">
                <h3 class="title">Installed</h3>
                <PluginList
                  :items="installedPlugins"
                  :plugin-type="pluginType"
                />
              </template>
              <template v-if="availablePlugins.length">
                <h3 class="title">Available</h3>
                <PluginList
                  :items="availablePlugins"
                  :plugin-type="pluginType"
                />
              </template>
              <hr />
              <div class="columns is-vcentered">
                <div class="column">
                  <article class="media">
                    <figure class="media-left">
                      <p class="image level-item container">
                        <span class="icon is-large fa-2x has-text-grey-light">
                          <font-awesome-icon icon="plus"></font-awesome-icon>
                        </span>
                      </p>
                    </figure>
                    <div class="media-content">
                      <div class="content">
                        <p>
                          <span class="has-text-weight-bold">
                            Don't see your data
                            {{
                              pluginType === 'extractors'
                                ? 'source'
                                : 'destination'
                            }}
                            listed here?
                          </span>
                          <br />
                          <small>
                            Additional {{ pluginType }} (including arbitrary
                            Singer
                            {{
                              pluginType === 'extractors' ? 'taps' : 'targets'
                            }}) are available when using the command line
                            interface.
                          </small>
                        </p>
                        <div class="buttons">
                          <a
                            :href="`https://www.meltano.com/plugins/${pluginType}/`"
                            target="_blank"
                            class="button is-interactive-primary"
                            >Learn more</a
                          >
                        </div>
                      </div>
                    </div>
                  </article>
                </div>
                <div class="column"></div>
              </div>
            </template>
          </div>
        </div>
      </div>

      <div v-if="isModal">
        <router-view :name="getModalName"></router-view>
      </div>
    </div>
  </router-view-layout>
</template>

<style lang="scss"></style>
