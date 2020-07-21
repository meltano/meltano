<script>
import { mapActions, mapGetters } from 'vuex'

import ExtractorList from '@/components/pipelines/ExtractorList'
import RouterViewLayout from '@/views/RouterViewLayout'

export default {
  name: 'Extractors',
  components: {
    ExtractorList,
    RouterViewLayout
  },
  data() {
    return {
      hasInstalled: false,
      isLoading: true
    }
  },
  computed: {
    ...mapGetters('plugins', ['getIsPluginInstalled', 'visibleExtractors']),
    getAvailableExtractors() {
      return this.visibleExtractors.filter(
        ({ name }) => !this.getIsPluginInstalled('extractors', name)
      )
    },
    getInstalledExtractors() {
      return this.visibleExtractors.filter(({ name }) =>
        this.getIsPluginInstalled('extractors', name)
      )
    },
    getModalName() {
      return this.$route.name
    },
    isModal() {
      return this.$route.meta.isModal
    }
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
    ...mapActions('plugins', ['getInstalledPlugins'])
  }
}
</script>

<template>
  <router-view-layout>
    <div class="container view-body is-widescreen">
      <h2 id="data" class="title">Extractors</h2>

      <div class="columns">
        <div class="column">
          <div class="box">
            <progress
              v-if="isLoading"
              class="progress is-small is-info"
            ></progress>
            <template v-else>
              <template v-if="getInstalledExtractors.length">
                <h3 class="has-text-weight-bold">Installed</h3>
                <hr />
                <ExtractorList :items="getInstalledExtractors" />
              </template>
              <h3 class="has-text-weight-bold">Available</h3>
              <hr />
              <ExtractorList :items="getAvailableExtractors" />
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
                          <span class="has-text-weight-bold"
                            >Don't see your extractor here?</span
                          >
                          <br />
                          <small>
                            Additional extractors are available when using the
                            command line interface. You can also easily add any
                            existing Singer tap as a custom extractor or create
                            your own from scratch.
                          </small>
                        </p>
                        <div class="buttons">
                          <a
                            href="https://www.meltano.com/plugins/extractors/"
                            target="_blank"
                            class="button is-interactive-primary"
                            >Learn More</a
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
