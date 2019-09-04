<script>
import { mapState } from 'vuex'

import ConnectorLogo from '@/components/generic/ConnectorLogo'
import Message from '@/components/generic/Message'

export default {
  name: 'Connections',
  components: {
    ConnectorLogo,
    Message
  },
  computed: {
    ...mapState('plugins', ['plugins']),
  },
  created() {
    this.$store.dispatch('plugins/getAllPlugins')
    this.$store.dispatch('plugins/getInstalledPlugins')
  },
  methods: {
    updateConnectionSettings(connectionName) {
      this.$router.push({
        name: 'analyzeConnectionSettings',
        params: { connector: connectionName }
      })
    }
  }
}
</script>

<template>
  <div>
    <div class="columns">
      <div class="column">
        <div class="content">
          <Message>
            <p>This manual connection requirement will soon be automated :)</p>
            <p>
              After successfully setting up a
              <router-link :to="{ name: 'schedules' }"
                >data pipeline</router-link
              >
              Meltano has:
            </p>
            <ol>
              <li>
                <em>Extracted</em> data <em>from</em> a database or API (data
                source)
              </li>
              <li>
                <em>Loaded</em> the extracted data <em>to</em> a database
                (warehouse)
              </li>
              <li>
                <em>Transformed</em> the loaded data <em>to</em> the warehouse
                under a special <em>analytics schema</em>
              </li>
            </ol>
            <p>
              Now Meltano needs a connection to that
              <em>analytics schema</em> so Meltano Analyze can connect and
              query. Use the options below to setup the connection.
            </p>
          </Message>
        </div>
      </div>
    </div>

    <div class="tile is-ancestor is-flex is-flex-wrap">
      <div
        v-for="(pluginConnection, index) in plugins.connections"
        :key="`${pluginConnection}-${index}`"
        class="tile is-parent is-3 is-relative"
      >
        <div class="tile level is-child box">
          <div class="image level-item is-64x64 container">
            <ConnectorLogo :connector="pluginConnection" />
          </div>
          <div class="content is-small">
            <p class="has-text-centered">
              {{ pluginConnection }}
            </p>
            <a
              class="button is-interactive-primary is-small is-block"
              @click="updateConnectionSettings(pluginConnection)"
              >Configure
            </a>
          </div>
        </div>
      </div>
    </div>
    <progress
      v-if="!plugins.connections"
      class="progress is-small is-info"
    ></progress>
  </div>
</template>

<style lang="scss"></style>
