<script>
import { mapGetters, mapState } from 'vuex';
import store from '@/store';

export default {
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
  computed: {
    ...mapState('settings', [
      'settings',
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
    saveConnection() {
      this.$store.dispatch('settings/saveConnection', {
        name: this.connectionName,
        database: this.connectionDatabase,
        schema: this.connectionSchema,
        dialect: this.connectionDialect,
        host: this.connectionHost,
        port: this.connectionPort,
        username: this.connectionUsername,
        password: this.connectionPassword,
        path: this.connectionSqlitePath,
      });
      this.connectionName = '';
      this.connectionDatabase = '';
      this.connectionSchema = '';
      this.connectionDialect = '';
      this.connectionHost = '';
      this.connectionPort = '';
      this.connectionUsername = '';
      this.connectionPassword = '';
      this.connectionSqlitePath = '';
    },
    deleteConnection(connection) {
      this.$store.dispatch('settings/deleteConnection', connection);
    },
  },
};
</script>

<template>
  <section>
    <div class="content">
      <h3>Analytics Connection Settings</h3>
      <p v-if="!hasConnections">No Database Connections</p>
      <div class="columns is-multiline is-mobile">
        <div
          class="column is-half"
          v-for="connection in settings.connections"
          :key="connection.host"
        >
          <div class="card">
            <header class="card-header">
              <p class="card-header-title">{{connection.name}}</p>
            </header>
            <div class="card-content">
              <div class="content">
                <p>
                  <strong>Dialect</strong>
                  <span class="is-pulled-right">{{connection.dialect}}</span>
                </p>
                <div v-if="!isConnectionDialectSqlite(connection.dialect)">
                  <p>
                    <strong>Port</strong>
                    <span class="is-pulled-right">{{connection.port}}</span>
                  </p>
                  <p>
                    <strong>Username</strong>
                    <span class="is-pulled-right">{{connection.username}}</span>
                  </p>
                  <p>
                    <strong>Host</strong>
                    <span
                      class="ellipsis is-pulled-right"
                      :title="connection.host"
                    >{{connection.host}}</span>
                  </p>
                </div>
                <div v-if="isConnectionDialectSqlite(connection.dialect)">
                  <p>
                    <strong>Path</strong>
                    <span
                      class="ellipsis is-pulled-right"
                      :title="connection.path"
                    >{{connection.path}}</span>
                  </p>
                </div>
              </div>
            </div>
            <footer class="card-footer">
              <a
                href="#"
                class="card-footer-item is-danger"
                @click.prevent="deleteConnection(connection)"
              >Delete Connection</a>
            </footer>
          </div>
        </div>
      </div>
    </div>

    <div class="content">
      <h3 class="title">Add Analytics Connection</h3>
      <div class="field is-grouped">
        <div class="control is-expanded">
          <input class="input" type="text" placeholder="Name" v-model="connectionName">
        </div>
        <div class="control">
          <div class="select">
            <select v-model="connectionDialect">
              <option value disabled selected>Dialect</option>
              <option value="postgresql">PostgreSQL</option>
              <option value="mysql">MySQL</option>
              <option value="sqlite">SQLite</option>
            </select>
          </div>
        </div>
      </div>

      <div class="field" v-if="!isConnectionDialectSqlite(connectionDialect)">
        <div class="field is-grouped">
          <p class="control is-expanded">
            <input class="input" type="text" placeholder="Host" v-model="connectionHost">
          </p>
          <p class="control">
            <input class="input" type="text" placeholder="Port" v-model="connectionPort">
          </p>
        </div>

        <div class="field is-grouped">
          <p class="control is-expanded">
            <input class="input" type="text" placeholder="Database" v-model="connectionDatabase">
          </p>
          <p class="control">
            <input class="input" type="text" placeholder="Schema" v-model="connectionSchema">
          </p>
        </div>

        <div class="field is-grouped">
          <p class="control is-expanded">
            <input class="input" type="text" placeholder="Username" v-model="connectionUsername">
          </p>
          <p class="control is-expanded">
            <input
              class="input"
              type="password"
              placeholder="Password"
              v-model="connectionPassword"
            >
          </p>
        </div>
      </div>

      <div class="field" v-if="isConnectionDialectSqlite(connectionDialect)">
        <div class="field is-grouped">
          <p class="control is-expanded">
            <input
              class="input"
              type="text"
              placeholder="Path to SQLite file"
              v-model="connectionSqlitePath"
            >
          </p>
        </div>
      </div>
    </div>

    <div class="buttons is-right">
      <button
        class="button is-interactive-primary"
        :disabled="!isSaveable"
        @click.prevent="saveConnection"
      >Save</button>
    </div>
  </section>
</template>

<style>
</style>
