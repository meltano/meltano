<template>

  <div class="modal is-active">
    <div class="modal-background" @click="close"></div>
    <div class="modal-card">
      <header class="modal-card-head">
        <div class="modal-card-head-image image is-64x64 level-item">
          <img
            :src='getLoaderImageUrl(loaderNameFromRoute)'
            :alt="`${getLoaderNameWithoutPrefixedTargetDash(loaderNameFromRoute)} logo`">
        </div>
        <p class="modal-card-title">Loader Settings</p>
        <button class="delete" aria-label="close" @click="close"></button>
      </header>
      <section class="modal-card-body">

        <div class="columns">
          <div class="column">
            Todo
          </div>
        </div>

      </section>
      <footer class="modal-card-foot buttons is-right">
        <button
          class="button"
          @click="close">Cancel</button>
        <button
          class='button is-interactive-primary'
          :disabled='!isSavable'
          @click.prevent="saveConnectionAndBeginRun">Save</button>
      </footer>
    </div>
  </div>

</template>
<script>
import { mapState, mapGetters } from 'vuex';

export default {
  name: 'LoaderSettingsModal',
  created() {
    this.loaderNameFromRoute = this.$route.params.loader;
    this.$store.dispatch('configuration/getInstalledPlugins');
  },
  computed: {
    ...mapState('configuration', [
      'installedPlugins', // Leverage installed plugins approach vs getSettings old way?
    ]),
    ...mapGetters('configuration', [
      'getLoaderImageUrl',
      'getLoaderNameWithoutPrefixedTargetDash',
    ]),
    isSavable() {
      return true; // TODO mirror ExtractorSettingsModal approach
    },
    loader() {
      return this.installedPlugins.loaders
        ? this.installedPlugins.loaders.find(item => item.name === this.loaderNameFromRoute)
        : {};
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
  },
};
</script>
