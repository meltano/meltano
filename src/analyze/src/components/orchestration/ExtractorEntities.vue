<template>
  <div>

    <!-- Loading -->
    <div v-if='isLoading'>
      <progress v-if="true" class="progress is-small is-info"></progress>
    </div>

    <!-- Loaded -->
    <div v-else>
      <div class="columns">
        <div class="column">
          <h3>Entities for {{extractorEntities.extractorName}}</h3>
        </div>
        <div class="column">
          <div class="buttons is-pulled-right">
            <a class='button is-success' @click='selectEntities'>Collect</a>
          </div>
        </div>
      </div>
      <div
        class='is-unselectable'
        v-for='entityGroup in orderedEntityGroups'
        :key='`${entityGroup.name}`'>
        <a
          class='button is-rounded'
          :class="{'is-primary': entityGroup.selected}"
          @click.stop="entityGroupSelected(entityGroup)">{{entityGroup.name}}</a>
        <div
          v-for='attribute in orderedAttributes(entityGroup.attributes)'
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
import _ from 'lodash';

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
    orderedEntityGroups() {
      return _.orderBy(this.extractorEntities.entityGroups, 'name');
    },
    orderedAttributes() { return (attributes) => {
        return _.orderBy(attributes, 'name');
      }
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
