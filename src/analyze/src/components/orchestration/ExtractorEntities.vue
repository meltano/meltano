<template>
  <div>
    <h2>Entities for {{extractorEntities.extractorName}}</h2>
    <div
      class='is-unselectable'
      v-for='entityGroup in extractorEntities.entityGroups'
      :key='`${entityGroup.name}`'
      @click.stop="entityGroupSelected(entityGroup)">
      <h3 :class="{'has-text-success': entityGroup.selected}">{{entityGroup.name}}</h3>
      <div
        v-for='attribute in entityGroup.attributes'
        :key='`${attribute.name}`'
        @click.stop="entityAttributeSelected({entityGroup, attribute})">
        <div :class="{'has-text-success': attribute.selected}">
          {{attribute.name}}
        </div>
      </div>
    </div>
    <a
      class='button'
      @click='extractEntities'>Collect</a>
  </div>
</template>

<script>
export default {
  name: 'ExtractorEntities',
  props: ['extractorEntities'],
  created() {
    this.$store.dispatch('orchestrations/getExtractorEntities', 'tap-carbon-intensity');
  },
  methods: {
    extractEntities() {
      this.$store.dispatch('orchestrations/extractEntities');
    },
    entityGroupSelected(entityGroup) {
      this.$store.dispatch('orchestrations/toggleEntityGroup', entityGroup);
    },

    entityAttributeSelected(payload) {
      this.$store.dispatch('orchestrations/toggleEntityAttribute', payload);
    },
  },
};
</script>
