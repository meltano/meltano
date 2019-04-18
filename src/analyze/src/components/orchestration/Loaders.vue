<script>
import { mapState, mapGetters } from 'vuex';

import BaseCard from '@/components/generic/BaseCard';
import ConnectorCard from '@/components/orchestration/ConnectorCard';
import ConnectorSettings from '@/components/orchestration/ConnectorSettings';

import orchestrationsApi from '@/api/orchestrations';

export default {
  name: 'Loaders',
  components: {
    BaseCard,
    ConnectorCard,
    ConnectorSettings,
  },
  data() {
    return {
      filterLoadersText: '',
      installingLoader: false,
    };
  },
  created() {
    this.$store.dispatch('orchestrations/getAll');
    this.$store.dispatch('orchestrations/getInstalledPlugins');
  },
  computed: {
    ...mapState('orchestrations', [
      'installedPlugins',
      'loaders',
    ]),
    ...mapGetters('orchestrations', [
      'remainingLoaders',
    ]),
    filteredInstalledLoaders() {
      if (this.installedPlugins && this.installedPlugins.loaders) {
        if (this.filterLoadersText) {
          return this.installedPlugins.loaders
            .filter(item => item.name.indexOf(this.filterLoadersText) > -1);
        }
        return this.installedPlugins.loaders;
      }
      return [];
    },
    filteredLoaders() {
      if (this.filterLoadersText) {
        return this.remainingLoaders.filter(item => item.indexOf(this.filterLoadersText) > -1);
      }
      return this.remainingLoaders;
    },
  },
  methods: {
    installLoader(loader) {
      this.installingLoader = true;

      orchestrationsApi.addLoaders({
        name: loader,
      }).then((response) => {
        if (response.status === 200) {
          this.$store.dispatch('orchestrations/getInstalledPlugins')
            .then(() => {
              this.installingLoader = false;
            });
        }
      });
    },
  },
}
</script>

<template>
  <div>

    <input
      type="text"
      v-model="filterLoadersText"
      placeholder="Filter loaders..."
      class="input connector-input">
    <h2 class="title is-3">Installed</h2>
    <p v-if="filteredInstalledLoaders.length === 0">No loaders currently installed</p>
    <div v-else class="installed-connectors">
      <ConnectorCard v-for="(loader, index) in filteredInstalledLoaders"
        :connector="loader.name"
        :key="`${loader.name}-${index}`"
      >
      </ConnectorCard>
    </div>
    <h2 class="title is-3">Available</h2>
    <p v-if="installingLoader">Installing...</p>
    <progress v-if="installingLoader" class="progress is-small is-info"></progress>
    <p v-if="filteredLoaders.length === 0">All available loaders have been installed.</p>
    <div v-else class="card-grid">
      <ConnectorCard v-for="(loader, index) in filteredLoaders"
        :connector="loader"
        :key="`${loader}-${index}`"
      >
        <template v-slot:callToAction>
          <button @click="installLoader(loader)" class="card-button">Install</button>
        </template>
      </ConnectorCard>
    </div>

  </div>
</template>

<style lang="scss">
.card-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  grid-column-gap: 15px;
  grid-row-gap: 15px;
}

.installed-connectors {
  display: grid;
  grid-row-gap: 15px;
}

.card-button {
  width: 100%;
  background-color: hsl(210, 100%, 42%);
  color: #fff;
  text-align: center;
  padding: 10px 0;
  font-size: 1rem;
  transition: background 0.2s ease-in;
  cursor: pointer;

  &:hover {
    background-color: hsl(210, 74%, 22%);
  }
}

.connector-input {
  margin-top: 15px;
}
</style>
