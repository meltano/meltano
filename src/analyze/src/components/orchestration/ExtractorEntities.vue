<template>
  <div>

    <!-- Loading -->
    <div v-if='isLoading'>
      <progress v-if="true" class="progress is-small is-info" max="100">0%</progress>
    </div>

    <!-- Loaded -->
    <div v-else>
      <h2>Entities for {{extractorEntities.extractorName}}</h2>
      <a
        class='button'
        @click='selectEntities'>Collect</a>
      <div
        class='is-unselectable'
        v-for='entityGroup in extractorEntities.entityGroups'
        :key='`${entityGroup.name}`'>
        <a
          class='button is-rounded'
          :class="{'is-primary': entityGroup.selected}"
          @click.stop="entityGroupSelected(entityGroup)">{{entityGroup.name}}</a>
        <div
          v-for='attribute in entityGroup.attributes'
          :key='`${attribute.name}`'>
          <a
            class="button is-rounded is-small"
            :class="{'is-primary': attribute.selected}"
            @click.stop="entityAttributeSelected({entityGroup, attribute})">
            {{attribute.name}}
          </a>
        </div>
      </div>
    </div>

  </div>
</template>

<script>
export default {
  name: 'ExtractorEntities',
  props: {
    extractor: {
      type: Object,
      default() {
        return {};
      },
    },
    extractorEntities: {
      type: Object,
      default() {
        return {};
      },
    },
  },
  created() {
    this.$store.dispatch('orchestrations/getExtractorEntities', this.extractor.name);
  },
  computed: {
    isLoading() {
      return !this.extractorEntities.hasOwnProperty('entityGroups');
    },
  },
  methods: {
    entityAttributeSelected(payload) {
      this.$store.dispatch('orchestrations/toggleEntityAttribute', payload);
    },
    entityGroupSelected(entityGroup) {
      this.$store.dispatch('orchestrations/toggleEntityGroup', entityGroup);
    },
    selectEntities() {
      this.$store.dispatch('orchestrations/selectEntities');
    },
  },
};
</script>
