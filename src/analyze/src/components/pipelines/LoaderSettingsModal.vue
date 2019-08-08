<script>
import { mapState, mapGetters } from 'vuex';
import ConnectorLogo from '@/components/generic/ConnectorLogo';
import ConnectorSettings from '@/components/pipelines/ConnectorSettings';

export default {
  name: 'LoaderSettingsModal',
  components: {
    ConnectorLogo,
    ConnectorSettings,
  },
  created() {
    this.loaderNameFromRoute = this.$route.params.loader;
    this.$store.dispatch(
      'configuration/getLoaderConfiguration',
      this.loaderNameFromRoute,
    );
    this.$store.dispatch('plugins/getInstalledPlugins');
  },
  beforeDestroy() {
    this.$store.dispatch('configuration/clearLoaderInFocusConfiguration');
  },
  computed: {
    ...mapGetters('plugins', ['getIsPluginInstalled', 'getIsInstallingPlugin']),
    ...mapGetters('configuration', ['getHasValidConfigSettings']),
    ...mapState('configuration', ['loaderInFocusConfiguration']),
    ...mapState('plugins', ['installedPlugins']),
    isInstalled() {
      return this.getIsPluginInstalled('loaders', this.loaderNameFromRoute);
    },
    isInstalling() {
      return this.getIsInstallingPlugin('loaders', this.loaderNameFromRoute);
    },
    isLoadingConfigSettings() {
      return !Object.prototype.hasOwnProperty.call(
        this.loaderInFocusConfiguration,
        'config',
      );
    },
    isSaveable() {
      const isValid = this.getHasValidConfigSettings(this.loaderInFocusConfiguration);
      return !this.isInstalling && this.isInstalled && isValid;
    },
    loader() {
      const targetLoader = this.installedPlugins.loaders
        ? this.installedPlugins.loaders.find(
          item => item.name === this.loaderNameFromRoute,
        )
        : null;
      return targetLoader || {};
    },
  },
  methods: {
    close() {
      if (this.prevRoute) {
        this.$router.go(-1);
      } else {
        this.$router.push({ name: 'loaders' });
      }
    },
    saveConfigAndGoToOrchestration() {
      this.$store
        .dispatch('configuration/savePluginConfiguration', {
          name: this.loader.name,
          type: 'loaders',
          config: this.loaderInFocusConfiguration.config,
        })
        .then(() => {
          this.$router.push({ name: 'schedules' });
        });
    },
  },
};
</script>

<template>
  <div class="modal is-active">
    <div class="modal-background" @click="close"></div>
    <div class="modal-card is-narrow">
      <header class="modal-card-head">
        <div class="modal-card-head-image image is-64x64 level-item">
          <ConnectorLogo :connector="loaderNameFromRoute" />
        </div>
        <p class="modal-card-title">Loader Configuration</p>
        <button class="delete" aria-label="close" @click="close"></button>
      </header>

      <section class="modal-card-body">
        <template v-if="isInstalling">
          <div class="content">
            <div class="level">
              <div class="level-item">
                <p>
                  Installing {{ loaderNameFromRoute }} can take up to a minute.
                </p>
              </div>
            </div>
            <progress class="progress is-small is-info"></progress>
          </div>
        </template>

        <div v-if="loader.signupUrl" class="intro-module">
          <p>This plugin requires an account. If you don't have one, you can <a :href="loader.signupUrl" target="_blank">sign up here</a>.</p>
        </div>

        <ConnectorSettings
          v-if="!isLoadingConfigSettings"
          fieldClass="is-small"
          :config-settings="loaderInFocusConfiguration"
        />

        <div v-if="loader.docs" class="footnote-module">
          <p>Need help finding this information? We got you covered with our <a :href="loader.docs" target="_blank">docs here</a>.</p>
        </div>

        <progress
          v-if="isLoadingConfigSettings && !isInstalling"
          class="progress is-small is-info"
        ></progress>
      </section>

      <footer class="modal-card-foot buttons is-right">
        <button class="button" @click="close">Cancel</button>
        <button
          class="button is-interactive-primary"
          :disabled="!isSaveable"
          @click.prevent="saveConfigAndGoToOrchestration"
        >
          Save
        </button>
      </footer>
    </div>
  </div>
</template>

<style lang="scss" scoped>
.intro-module {
  margin-bottom: 1rem;
}

.footnote-module {
  margin-top: 1rem;
}
</style>
