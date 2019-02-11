<template>
<div class="container">
  <div class="columns">
    <aside class="menu column is-one-quarter section has-background-light">
      <p class="menu-label">
        Database
      </p>
      <ul class="menu-list">
        <li><a>Connections</a></li>
      </ul>
    </aside>
    <div class="column section">
      <section class="section">
        <p v-if="!hasConnections">No Database Connections</p>
        <div class="columns is-multiline is-mobile">
          <div class="column is-half"
                v-for="connection in settings.connections"
                :key="connection.host">
            <div class="card">
              <header class="card-header">
                <p class="card-header-title">
                  {{connection.name}}
                </p>
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
                      <span class="ellipsis is-pulled-right"
                              :title="connection.host">
                        {{connection.host}}
                      </span>
                    </p>
                  </div>
                  <div v-if="isConnectionDialectSqlite(connection.dialect)">
                    <p>
                      <strong>Path</strong>
                      <span class="ellipsis is-pulled-right"
                              :title="connection.path">
                        {{connection.path}}
                      </span>
                    </p>
                  </div>
                </div>
              </div>
              <footer class="card-footer">
                <a href="#" class="card-footer-item is-danger"
                    @click.prevent="deleteConnection(connection)">
                  Delete Connection
                </a>
              </footer>
            </div>
          </div>
        </div>
      </section>
      <section class="section">
        <h2 class="title">New Database Connection</h2>
        <div class="field is-grouped">
          <div class="control is-expanded">
            <input class="input" type="text" placeholder="Name" v-model="connectionName">
          </div>
          <div class="control">
            <div class="select">
              <select v-model="connectionDialect">
                <option value="" disabled selected>Dialect</option>
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

        <div class="field">
          <div class="control">
            <button class="button is-link"
                      @click.prevent="saveConnection">
              Save Connection
            </button>
          </div>
        </div>
      </section>
    </div>
  </div>
</div>
</template>
<script>
import { mapState, mapGetters } from 'vuex';

export default {
  name: 'Settings',

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

  created() {
    this.$store.dispatch('settings/getSettings');
  },

  computed: {
    ...mapState('settings', [
      'settings',
    ]),
    ...mapGetters('settings', [
      'hasConnections',
      'isConnectionDialectSqlite',
    ]),
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
