<script>
import { mapGetters, mapState } from 'vuex'
import fileTypeEnums from '@/utils/fileTypeEnums'
import pretty from '@/filters/pretty'
import RouterViewLayout from '@/views/RouterViewLayout'
import utils from '@/utils/utils'

export default {
  name: 'Repo',
  components: {
    RouterViewLayout
  },
  filters: {
    pretty
  },
  computed: {
    ...mapGetters('repos', [
      'hasFiles',
      'hasError',
      'passedValidation',
      'hasMarkdown',
      'hasCode'
    ]),
    ...mapState('repos', [
      'files',
      'activeView',
      'validated',
      'loadingValidation',
      'loadingUpdate',
      'errors'
    ])
  },
  created() {
    this.getRepo()
    this.sync()
  },
  methods: {
    getRepo() {
      this.$store.dispatch('repos/getRepo')
    },
    jsDashify(type, name) {
      return utils.jsDashify(type, name)
    },
    isActive(f) {
      return f.id === this.activeView.id
    },
    isDeepRoutable(type) {
      return type === fileTypeEnums.dashboards || type === fileTypeEnums.reports
    },
    getDeepRoute(key, file) {
      const name = utils.capitalize(utils.singularize(key))
      const params = { slug: file.slug }
      if (file.model && file.design) {
        params.model = file.model
        params.design = file.design
      }
      return { name, params }
    },
    getFile(file) {
      this.$store.dispatch('repos/getFile', file)
    },
    lint() {
      this.$store.dispatch('repos/lint')
    },
    sync() {
      this.$store.dispatch('repos/sync')
    }
  }
}
</script>

<template>
  <router-view-layout>
    <div class="container view-header">
      <div class="content">
        <div class="level">
          <h1 class="is-marginless">Repo</h1>
        </div>
      </div>
    </div>

    <div class="container view-body">
      <section>
        <div class="columns is-gapless">
          <aside class="column is-one-quarter">
            <div class="level">
              <div class="level-left">
                <div class="field has-addons">
                  <div class="control">
                    <a
                      href="#"
                      class="button is-small"
                      :class="{ 'is-loading': loadingValidation }"
                      @click="lint"
                      >Lint</a
                    >
                  </div>
                  <div class="control">
                    <a
                      href="#"
                      class="button is-small"
                      :class="{ 'is-loading': loadingUpdate }"
                      @click="sync"
                      >Sync</a
                    >
                  </div>
                </div>
              </div>
              <div class="level-right">
                <span v-if="passedValidation" class="tag is-success pull-right"
                  >Passed!</span
                >
                <span v-if="!validated" class="tag is-warning"
                  >Unvalidated</span
                >
                <span v-if="hasError" class="tag is-danger">Errors</span>
              </div>
            </div>
            <template v-if="hasError">
              <nav class="panel">
                <!-- eslint-disable-next-line vue/require-v-for-key -->
                <div
                  v-for="err in errors"
                  class="panel-block has-background-white"
                >
                  <ul>
                    <li class="level">
                      <div class="tags has-addons">
                        <span class="tag is-info">?</span>
                        <span class="tag">{{ err.fileName }}</span>
                      </div>
                    </li>
                    <li class="error-desc-cont">
                      <code class="error-desc">{{ err.message }}</code>
                    </li>
                  </ul>
                </div>
              </nav>
            </template>
            <template v-if="!hasFiles">
              <p class="menu-label">
                No files found
              </p>
            </template>
            <template v-for="(value, key) in files">
              <!-- eslint-disable-next-line vue/require-v-for-key -->
              <p class="menu-label">
                {{ value.label }}
              </p>
              <!-- eslint-disable-next-line vue/require-v-for-key -->
              <ul class="menu-list">
                <template v-if="value.items">
                  <li v-for="file in value.items" :key="file.abs">
                    <div class="columns is-vcentered">
                      <div class="column">
                        <a
                          :class="[
                            { 'is-active': isActive(file) },
                            jsDashify(value.label, file.name)
                          ]"
                          @click.prevent="getFile(file)"
                        >
                          {{ file.name }}
                        </a>
                      </div>
                      <div
                        v-if="isDeepRoutable(key)"
                        class="column is-one-fifth"
                      >
                        <router-link
                          :to="getDeepRoute(key, file)"
                          class="button is-secondary is-light is-small is-pulled-right"
                        >
                          <!-- TODO temporary icon, find better solution -->
                          <font-awesome-icon icon="arrow-right" />
                        </router-link>
                      </div>
                    </div>
                  </li>
                </template>
              </ul>
            </template>
          </aside>
          <div class="column is-three-quarters">
            <div v-if="!activeView.populated">
              <div
                class="empty-state
                has-background-white
                has-text-centered
                is-size-4
                is-uppercase"
              >
                Select a file
              </div>
            </div>
            <div v-if="hasMarkdown">
              <div
                class="js-markdown-preview has-background-white"
                v-html="activeView.file"
              ></div>
            </div>
            <div
              v-else-if="hasCode"
              class="js-code-preview is-paddingless code-container"
            >
              <div class="has-background-white">
                <pre>{{ activeView.file | pretty }}</pre>
              </div>
            </div>
          </div>
        </div>
      </section>
    </div>
  </router-view-layout>
</template>

<style lang="scss" scoped>
.content {
  padding: 10px;
  position: fixed;
  top: 52px;
  left: 430px;
  right: 0;
  bottom: 0;
  overflow: scroll;
  z-index: 1;
}

.code-container {
  // to overcome the important on paddingless
  padding-left: 1rem !important;
}

.error-desc-cont {
  .tag {
    margin-bottom: 0.5rem;
  }
  .error-desc {
    display: block;
  }
}

.empty-state {
  padding-top: 200px;
}
</style>
