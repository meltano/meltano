<template>
  <div class="container">
    <div class="columns">
        <aside class="fixed-sidebar column is-one-quarter menu has-background-white-bis">
          <div class="level">
            <div class="level-left">
              <div class="field has-addons">
                <div class="control">
                  <a
                    href="#"
                    class="button is-small"
                    :class="{'is-loading': loadingValidation}"
                    @click="lint">Lint</a>
                </div>
                <div class="control">
                  <a
                    href="#"
                    class="button is-small"
                    :class="{'is-loading': loadingUpdate}"
                    @click="sync">Sync</a>
                </div>
              </div>
            </div>
            <div class="level-right">
              <span class="tag is-success pull-right" v-if="passedValidation">Passed!</span>
              <span class="tag is-warning" v-if="!validated">Unvalidated</span>
              <span class="tag is-danger" v-if="hasError">Errors</span>
            </div>
          </div>
          <template v-if="hasError">
            <nav class="panel">
              <!-- eslint-disable-next-line vue/require-v-for-key -->
              <div class="panel-block has-background-white" v-for="err in errors">
                <ul>
                  <li class="level">
                    <div class="tags has-addons">
                      <span class="tag is-info">?</span>
                      <span class="tag">{{err.file_name}}</span>
                    </div>
                  </li>
                  <li class="error-desc-cont">
                    <code class="error-desc">{{err.message}}</code>
                  </li>
                </ul>
              </div>
            </nav>
          </template>
          <template v-for="(value, key) in files">
            <!-- eslint-disable-next-line vue/require-v-for-key -->
            <p class="menu-label">
              <a href="#">{{key}}</a>
            </p>
            <!-- eslint-disable-next-line vue/require-v-for-key -->
            <ul class="menu-list">

              <template v-if="!value.length">
                <li>
                  <a><small><em>No {{key}}</em></small></a>
                </li>
              </template>

              <template v-if="value.length">
                <li v-for="file in value" :key="file.abs">
                  <div class="columns">
                    <div class="column">
                      <a :class="{'is-active': isActive(file)}"
                          @click.prevent='getFile(file)'>
                        {{file.visual}}
                      </a>
                    </div>
                    <div v-if='isDeepRoutable(key)' class='column is-one-fifth'>
                      <router-link :to="getDeepRoute(key)"
                                    class="button is-secondary is-light is-pulled-right">
                        <span class="icon is-small">
                          <i class="fas fa-bold">*</i>
                        </span>
                      </router-link>
                    </div>
                  </div>

                </li>
              </template>

            </ul>

          </template>
        </aside>
      <div class="column" v-if="!activeView.populated">
        <div
          class="empty-state
          content
          has-background-white
          has-text-centered
          is-size-4
          is-uppercase">
          Select a file
        </div>
      </div>
      <div class="column" v-if="hasMarkdown">
        <div class="content has-background-white" v-html="activeView.file"></div>
      </div>
      <div class="column is-paddingless code-container" v-else-if="hasCode">
        <div class="content has-background-white">
          <pre>{{activeView.file}}</pre>
        </div>
      </div>
    </div>
  </div>
</template>
<script>
import { mapState, mapGetters } from 'vuex';

export default {
  name: 'Repo',
  created() {
    this.getRepo();
    this.sync();
  },
  computed: {
    ...mapGetters('repos', [
      'hasError',
      'passedValidation',
      'hasMarkdown',
      'hasCode',
    ]),
    ...mapState('repos', [
      'files',
      'activeView',
      'validated',
      'loadingValidation',
      'loadingUpdate',
      'errors',
    ]),
  },
  methods: {
    getRepo() {
      this.$store.dispatch('repos/getRepo');
    },
    isActive(f) {
      return f.unique === this.activeView.unique;
    },
    // TODO refactor isDeepRoutable/getDeepRoute https://gitlab.com/meltano/meltano/issues/347
    isDeepRoutable(type) {
      return type === 'dashboards';
    },
    getDeepRoute(key) {
      return `/${key}`;
    },
    getFile(file) {
      this.$store.dispatch('repos/getFile', file);
    },
    lint() {
      this.$store.dispatch('repos/lint');
    },
    sync() {
      this.$store.dispatch('repos/sync');
    },
  },
};
</script>
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
