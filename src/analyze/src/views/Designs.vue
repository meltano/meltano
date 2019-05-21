<script>
import { mapGetters, mapState } from 'vuex';
import capitalize from '@/filters/capitalize';
import underscoreToSpace from '@/filters/underscoreToSpace';
import RouterViewLayout from '@/views/RouterViewLayout';

export default {
  name: 'Designs',
  components: {
    RouterViewLayout,
  },
  filters: {
    capitalize,
    underscoreToSpace,
  },
  created() {
    this.$store.dispatch('repos/getModels');
  },
  computed: {
    ...mapState('repos', [
      'models',
    ]),
    ...mapGetters('repos', [
      'urlForModelDesign',
    ]),
  },
};
</script>

<template>
  <router-view-layout>
    <div class='columns'>
      <div class="column">
        Designs view is in development. <a target="_blank" href="https://gitlab.com/meltano/meltano/issues/new?issue%5Bassignee_id%5D=&issue%5Bmilestone_id%5D=&issuable_template=feature_proposal">Get in touch if you have opinions about what should live here</a>.
      </div>
      <div class="column">
        <template v-for="(v, model) in models">
          <div class="navbar-item navbar-title has-text-grey-light" :key="model">
            {{model | capitalize | underscoreToSpace}}
          </div>
          <router-link
            :to="urlForModelDesign(model, design)"
            class="navbar-item navbar-child"
            v-for="design in v['designs']"
            :key="design">
            {{design | capitalize | underscoreToSpace}}
          </router-link>
        </template>
      </div>
    </div>
  </router-view-layout>
</template>

<style lang="scss">
</style>
