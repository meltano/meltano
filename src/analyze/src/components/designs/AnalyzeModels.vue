<script>
import { mapActions, mapGetters, mapState } from 'vuex';
import capitalize from '@/filters/capitalize';
import underscoreToSpace from '@/filters/underscoreToSpace';
import DocsLink from '@/components/generic/DocsLink';

export default {
  components: {
    DocsLink,
  },
  created() {
    this.$store.dispatch('configuration/getAllPlugins');
    this.$store.dispatch('configuration/getInstalledPlugins');
    this.$store.dispatch('repos/getModels');
  },
  computed: {
    ...mapState('configuration', ['installedPlugins', 'plugins']),
    ...mapGetters('repos', ['hasModels', 'urlForModelDesign']),
    ...mapGetters('configuration', [
      'getIsPluginInstalled',
      'getIsInstallingPlugin',
    ]),
    ...mapState('repos', ['models']),
  },
  filters: {
    capitalize,
    underscoreToSpace,
  },
  methods: {
    ...mapActions('configuration', [
      'installPlugin',
    ]),
    installModel(model) {
      this.installPlugin({ collectionType: 'models', name: model });
    },
  },
};
</script>

<template>
  <section>
    <aside v-if="!hasModels" class="message is-info">
      <div class="message-header">
        <p>No model found in this project</p>
      </div>
      <div class="message-body">
        <p class="content">
          Use <code>meltano add model</code> to add models to your current project.

          See the <docs-link page="tutorial" fragment="initialize-your-project">documentation</docs-link> for more details.
        </p>
        <p>
          The work for replacing this temporary UI is in this
          <a
            href="https://gitlab.com/meltano/meltano/issues/651"
          >issue</a>.
        </p>
      </div>
    </aside>

    <div class="columns" v-if="!!hasModels">
      <div class="column is-one-quarter">
        <h2 class='title is-5'>Available</h2>
        <div class="content">
            <div
              v-for='(modelPlugin, index) in plugins.models'
              :key="`${modelPlugin}-${index}`">
              <span>
                {{modelPlugin}}
              </span>
              <button
                v-if='!getIsPluginInstalled("models", modelPlugin)'
                :class='{ "is-loading": getIsInstallingPlugin("models", modelPlugin) }'
                class='button is-interactive-primary is-outlined is-block is-small'
                @click="installModel(modelPlugin)">Install</button>
              <span
                v-else
                class='is-italic'>Installed</span>
            </div>
        </div>
      </div>
      <div class="column is-three-quarter">
        <h2 class='title is-5'>Analyzable</h2>
        <div
          class="box"
          v-for="(v, model) in models" :key="`${model}-panel`">
          <div class="content">
            <h3 class='is-size-6'>{{model | capitalize | underscoreToSpace}}</h3>
            <hr class='hr-tight'>
            <div class="level level-tight" v-for="design in v['designs']" :key="design">
              <div class='level-left'>{{design | capitalize | underscoreToSpace}}</div>
              <div class="level-right">
                <router-link
                  class="button is-small is-interactive-primary"
                  :to='urlForModelDesign(model, design)'>Analyze</router-link>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </section>
</template>

<style>
.level:not(:last-child),
.level-tight:not(:last-child) {
  margin-bottom: .5rem;
}
</style>
