<script>
import { mapActions, mapGetters, mapState } from 'vuex';

export default {
  name: 'Loaders',
  created() {
    this.$store.dispatch('orchestrations/getAll');
    this.$store.dispatch('orchestrations/getInstalledPlugins');
  },
  computed: {
    ...mapGetters('orchestrations', [
      'getLoaderImageUrl',
      'getLoaderNameWithoutPrefixedTargetDash',
      'getIsLoaderPluginInstalled',
      'getIsInstallingLoaderPlugin',
    ]),
    ...mapState('orchestrations', [
      'loaders',
    ]),
  },
  methods: {
    ...mapActions('orchestrations', [
      'installLoader',
    ]),
    installLoaderAndBeginSettings(loader) {
      this.installLoader(loader);
      this.updateLoaderSettings(loader);
    },
    updateLoaderSettings(loader) {
      this.$router.push({ name: 'loaderSettings', params: { loader } });
    },
  },
};
</script>

<template>
  <div>

    <div class="columns">
      <div class="column is-three-fifths is-offset-one-fifth">
        <div class='content has-text-centered'>
          <p class='level-item buttons'>
            <a class="button is-small is-static is-marginless is-borderless">
              <span>Tell us which loader(s) to install</span>
            </a>
            <span class='step-spacer'>then</span>
            <a class="button is-small is-static is-marginless is-borderless">
              <span>Configure and save their settings</span>
            </a>
          </p>
        </div>
      </div>
    </div>

    <div class="tile is-ancestor flex-and-wrap">
      <div
        class="tile is-parent is-3"
        v-for="(loader, index) in loaders"
        :key="`${loader}-${index}`">
        <div class="tile level is-child box">
          <div class="image level-item is-64x64 container">
            <img
              :class='{ "grayscale": !getIsLoaderPluginInstalled(loader) }'
              :src='getLoaderImageUrl(loader)'
              :alt="`${getLoaderNameWithoutPrefixedTargetDash(loader)} logo`">
          </div>
          <div class="content is-small">
            <p class='has-text-centered'>
              {{loader}}
            </p>

            <template v-if='getIsLoaderPluginInstalled(loader)'>
              <div class="buttons are-small">
                <a
                  class='button is-interactive-primary flex-grow-1'
                  @click="updateLoaderSettings(loader)">Account Settings</a>
                <a class='button' disabled>Uninstall</a>
              </div>
            </template>
            <template v-else>
              <a
                :class='{ "is-loading": getIsInstallingLoaderPlugin(loader) }'
                class='button is-interactive-primary is-outlined is-block is-small'
                @click="installLoaderAndBeginSettings(loader)">Install</a>
            </template>

          </div>
        </div>
      </div>
    </div>

  </div>
</template>

<style lang="scss">
.flex-grow-1 {
  flex-grow: 1;
}
</style>
