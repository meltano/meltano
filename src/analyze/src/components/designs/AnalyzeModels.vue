<script>
import { mapGetters, mapState } from 'vuex';
import capitalize from '@/filters/capitalize';
import underscoreToSpace from '@/filters/underscoreToSpace';
import DocsLink from '@/components/generic/DocsLink';

export default {
  components: {
    DocsLink,
  },
  created() {
    this.$store.dispatch('configuration/getAll');
    this.$store.dispatch('configuration/getInstalledPlugins');
    this.$store.dispatch('repos/getModels');
  },
  computed: {
    ...mapState('configuration', ['allModels']),
    ...mapState('repos', ['models']),
    ...mapGetters('repos', ['hasModels', 'urlForModelDesign']),
  },
  filters: {
    capitalize,
    underscoreToSpace,
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
          <ul>
            <li
              v-for='model in allModels'
              :key='model'>{{model}}</li>
          </ul>
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
