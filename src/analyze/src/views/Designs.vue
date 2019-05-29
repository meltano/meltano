<script>
import RouterViewLayout from '@/views/RouterViewLayout';
import DocsLink from '@/components/generic/DocsLink';

export default {
  name: 'Designs',
  components: {
    RouterViewLayout,
    DocsLink,
  },
  filters: {
    capitalize,
    underscoreToSpace,
  },
  data() {
    return {
      connectionName: '',
      connectionDatabase: '',
      connectionSchema: '',
      connectionDialect: '',
      connectionHost: '',
      connectionPort: '',
      connectionUsername: '',
      connectionPassword: '',
      connectionSqlitePath: '',
    };
  },
  beforeRouteEnter(to, from, next) {
    store.dispatch('settings/getSettings')
      .then(next)
      .catch(() => {
        next(from.path);
      });
  },
  created() {
    this.$store.dispatch('repos/getModels');
  },
  computed: {
    ...mapState('repos', [
      'models',
    ]),
    ...mapState('settings', [
      'settings',
    ]),
    ...mapGetters('repos', [
      'urlForModelDesign',
      'hasModels',
    ]),
    ...mapGetters('settings', [
      'hasConnections',
      'isConnectionDialectSqlite',
    ]),
    isSaveable() {
      // TODO proper validation
      const dialectCondition = this.isConnectionDialectSqlite(this.connectionDialect)
        ? this.connectionSqlitePath.length > 0
        : true;
      const val = dialectCondition &&
        this.connectionName.length > 0 &&
        this.connectionDatabase.length > 0 &&
        this.connectionSchema.length > 0 &&
        this.connectionDialect.length > 0 &&
        this.connectionHost.length > 0 &&
        this.connectionPort.length > 0 &&
        this.connectionUsername.length > 0 &&
        this.connectionPassword.length > 0;
      return val;
    },
  },
  methods: {
    isCurrentLink(path) {
      if (this.$route.path === path) {
        return 'is-active';
      }
      return '';
    },
  },
};
</script>

<template>
  <router-view-layout>
    <div class="container">
      <div class="content">
        <ClosableMessage title="Meltano Analyze">
          <p>
            <span class="has-text-weight-bold">Meltano</span> streamlines the collection, analysis, and dashboarding of data.
          </p>
          <p>
            <span class="is-italic">You need to connect to pipelined data first</span>. Manage your connections below to enable analyses.
          </p>
        </ClosableMessage>
        <div class="level">
          <div class="level-left">
            <h1>Analyze</h1>
          </div>
          <div class="level-right">
            <div class="tabs is-right">
              <ul>
                <li :class="isCurrentLink('/analyze/models')">
                  <router-link to="/analyze/models">Models</router-link>
                </li>
                <li :class="isCurrentLink('/analyze/settings')" class="is-marginless">
                  <router-link to="/analyze/settings">Settings</router-link>
                </li>
              </ul>
            </div>

            <div class="field" v-if="!isConnectionDialectSqlite(connectionDialect)">
              <div class="field is-grouped">
                <p class="control is-expanded">
                  <input class="input"
                          type="text"
                          placeholder="Host"
                          v-model="connectionHost">
                </p>
                <p class="control">
                  <input class="input"
                          type="text"
                          placeholder="Port"
                          v-model="connectionPort">
                </p>
              </div>

              <div class="field is-grouped">
                <p class="control is-expanded">
                  <input class="input"
                          type="text"
                          placeholder="Database"
                          v-model="connectionDatabase">
                </p>
                <p class="control">
                  <input class="input"
                          type="text"
                          placeholder="Schema"
                          v-model="connectionSchema">
                </p>
              </div>

              <div class="field is-grouped">
                <p class="control is-expanded">
                  <input class="input"
                          type="text"
                          placeholder="Username"
                          v-model="connectionUsername">
                </p>
                <p class="control is-expanded">
                  <input class="input"
                          type="password"
                          placeholder="Password"
                          v-model="connectionPassword">
                </p>
              </div>
            </div>

            <div class="field" v-if="isConnectionDialectSqlite(connectionDialect)">
              <div class="field is-grouped">
                <p class="control is-expanded">
                  <input class="input"
                          type="text"
                          placeholder="Path to SQLite file"
                          v-model="connectionSqlitePath">
                </p>
              </div>
            </div>
          </div>

          <div class="buttons is-right">
            <button
              class='button is-interactive-primary'
              :disabled='!isSaveable'
              @click.prevent="saveConnection">Save</button>
          </div>

        </section>
      </div>
      <div class="column">
        <section>
          <div class="content">
            <h3>Analyses</h3>

            <article v-if="!hasModels" class="message is-info is-small">
              <div class="message-header">
                <p>No model found in this project</p>
              </div>
              <div class="message-body">
                <p class="content">
                  Use <code>meltano add model</code> to add models to your current project.

                  See the <docs-link page="tutorial" fragment="initialize-your-project">documentation</docs-link> for more details.
                </p>
              </div>
            </article>
            <template v-for="(v, model) in models">
              <div class="navbar-item navbar-title has-text-grey-light" :key="model">
                {{model | capitalize | underscoreToSpace}}
              </div>
              <router-link
                :to="urlForModelDesign(model, design)"
                class="navbar-item navbar-child"
                v-for="design in v['designs']"
                :key="design">
                {{design | capitalize | underscoreToSpace}}
              </router-link>
            </template>
          </div>
        </div>
        <router-view />
      </div>
    </div>
  </router-view-layout>
</template>

<style lang="scss">
</style>
