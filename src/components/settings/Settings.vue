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
        <h2 class="title">Connections</h2>
        <p v-if="!hasConnections">No Database Connections</p>
        <ul>
          <li v-for="connection in settings.connections" :key="connection.host">{{connection}}</li>
        </ul>
      </section>
      <section class="section">
        <h2 class="title">New Database Connection</h2>
        <div class="field">
          <div class="control">
            <input class="input" type="text" placeholder="Name">
          </div>
        </div>

        <div class="field">
          <div class="control">
            <div class="select">
              <select>
                <option value="postgresql">PostgreSQL</option>
                <option value="mysql">MySQL</option>
              </select>
            </div>
          </div>
        </div>

        <div class="field is-grouped">
          <p class="control is-expanded">
            <input class="input" type="text" placeholder="Host">
          </p>
          <p class="control">
            <input class="input" type="text" placeholder="Port">
          </p>
        </div>

        <div class="field is-grouped">
          <p class="control is-expanded">
            <input class="input" type="text" placeholder="Username">
          </p>
          <p class="control is-expanded">
            <input class="input" type="password" placeholder="Password">
          </p>
        </div>

        <div class="field">
          <div class="control">
            <button class="button is-link">Save Connection</button>
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
  created() {
    this.$store.dispatch('settings/getSettings');
  },
  computed: {
    ...mapState('settings', [
      'settings',
    ]),
    ...mapGetters('settings', [
      'hasConnections',
    ]),
  },
};
</script>
