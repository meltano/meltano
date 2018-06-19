<template>
  <div class="container">
    <div class="columns">
        <aside class="sidebar column is-one-quarter menu has-background-white-bis">
          <div class="level">
            <a
              href="#"
              class="button is-small"
              :class="{'is-loading': loadingValidation}"
              @click="lint">Validate</a>
            <a
              href="#"
              class="button is-small"
              :class="{'is-loading': loadingUpdate}"
              :disabled="!validated"
              @click="update">Update Database</a>
            <span class="tag is-success" v-if="passedValidation">Passed!</span>
            <span class="tag is-warning" v-if="!validated">Unvalidated</span>
            <span class="tag is-danger" v-if="hasError">Errors</span>
          </div>
          <template v-if="hasError">
            <nav class="panel">
              <!-- eslint-disable-next-line vue/require-v-for-key -->
              <div class="panel-block has-background-white" v-for="err in errors">
                <ul>
                  <li class="level">
                    <div class="tags has-addons">
                      <span class="tag is-info">{{err._file_type}}</span>
                      <span class="tag">{{err._file_name}}</span>
                    </div>
                  </li>
                  <li class="error-desc-cont">
                    <div class="tag">{{err.error.name}}</div>
                    <code class="error-desc">{{err.error.message}}</code>
                    <code class="error-desc">Start: {{err.error.location.start}}</code>
                    <code class="error-desc">End: {{err.error.location.end}}</code>
                  </li>
                </ul>
              </div>
            </nav>
          </template>
          <template v-for="(value, key) in blobs">
            <!-- eslint-disable-next-line vue/require-v-for-key -->
            <p class="menu-label">
              <a href="#">{{key}}</a>
            </p>
            <!-- eslint-disable-next-line vue/require-v-for-key -->
            <ul class="menu-list">
              <li v-for="blob in value" :key="blob.abs">
                <a :class="{'is-active': isActive(blob)}"
                  @click.prevent='getBlob(blob)'>{{blob.visual}}</a>
              </li>
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
        <div class="content has-background-white" v-html="activeView.blob"></div>
      </div>
      <div class="column is-paddingless code-container" v-else-if="hasCode">
        <div class="content has-background-white">
          <pre>{{activeView.blob}}</pre>
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
  },
  computed: {
    ...mapGetters('repos', [
      'hasError',
      'passedValidation',
      'hasMarkdown',
      'hasCode',
    ]),
    ...mapState('repos', [
      'blobs',
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
      return f.hexsha === this.activeView.hexsha;
    },
    getBlob(blob) {
      this.$store.dispatch('repos/getBlob', blob);
    },
    lint() {
      this.$store.dispatch('repos/lint');
    },
    update() {
      this.$store.dispatch('repos/update');
    },
  },
};
</script>
<style lang="scss" scoped>
.sidebar {
  position: fixed;
  overflow: scroll;
  top: 72px;
  bottom: 0;
  left: 0;
}

.content {
  padding: 10px;
  position: fixed;
  top: 72px;
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
