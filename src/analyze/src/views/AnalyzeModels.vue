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
    this.$store.dispatch('repos/getModels');
  },
  computed: {
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
      <div class="column is-one-quarter panel" v-for="(v, model) in models" :key="`${model}-panel`">
        <h3 class="panel-heading is-marginless">{{model | capitalize | underscoreToSpace}}</h3>
        <router-link
          v-for="design in v['designs']" :key="design"
          :to="urlForModelDesign(model, design)"
          class="panel-block"
        >
          <span class="panel-icon">
            <font-awesome-icon icon="pencil-ruler" />
          </span> {{design | capitalize | underscoreToSpace}}
        </router-link>
      </div>
      <div class="column is-one-quarter panel" v-for="(v, model) in models" :key="`${model}-panel`">
        <h3 class="panel-heading is-marginless">{{model | capitalize | underscoreToSpace}}</h3>
        <router-link
          v-for="design in v['designs']" :key="design"
          :to="urlForModelDesign(model, design)"
          class="panel-block"
        >
          <span class="panel-icon">
            <font-awesome-icon icon="pencil-ruler" />
          </span> {{design | capitalize | underscoreToSpace}}
        </router-link>
      </div>
      <div class="column is-one-quarter panel" v-for="(v, model) in models" :key="`${model}-panel`">
        <h3 class="panel-heading is-marginless">{{model | capitalize | underscoreToSpace}}</h3>
        <router-link
          v-for="design in v['designs']" :key="design"
          :to="urlForModelDesign(model, design)"
          class="panel-block"
        >
          <span class="panel-icon">
            <font-awesome-icon icon="pencil-ruler" />
          </span> {{design | capitalize | underscoreToSpace}}
        </router-link>
      </div>
      <div class="column is-one-quarter panel" v-for="(v, model) in models" :key="`${model}-panel`">
        <h3 class="panel-heading is-marginless">{{model | capitalize | underscoreToSpace}}</h3>
        <router-link
          v-for="design in v['designs']" :key="design"
          :to="urlForModelDesign(model, design)"
          class="panel-block"
        >
          <span class="panel-icon">
            <font-awesome-icon icon="pencil-ruler" />
          </span> {{design | capitalize | underscoreToSpace}}
        </router-link>
        <router-link
          v-for="design in v['designs']" :key="design"
          :to="urlForModelDesign(model, design)"
          class="panel-block"
        >
          <span class="panel-icon">
            <font-awesome-icon icon="pencil-ruler" />
          </span> {{design | capitalize | underscoreToSpace}}
        </router-link>
        <router-link
          v-for="design in v['designs']" :key="design"
          :to="urlForModelDesign(model, design)"
          class="panel-block"
        >
          <span class="panel-icon">
            <font-awesome-icon icon="pencil-ruler" />
          </span> {{design | capitalize | underscoreToSpace}}
        </router-link>
      </div>
    </div>
  </section>
</template>

<style>
</style>
