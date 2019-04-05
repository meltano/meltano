<template>
  <div>
    <h2>Entities for {{extractorEntities.extractorName}}</h2>
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
    // TODO pull out and place in Ben's tap card implementation
    this.$store.dispatch('orchestrations/getExtractorEntities', 'tap-salesforce');
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
