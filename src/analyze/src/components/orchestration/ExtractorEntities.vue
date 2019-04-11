<template>
  <div>

    <!-- Loading -->
    <progress v-if="isLoading" class="progress is-small is-info"></progress>

    <!-- Loaded -->
    <div v-else>
      <div class="columns">
        <div class="column is-10">
          <h3>Entities for {{extractorEntities.extractorName}}</h3>
        </div>
        <div class="column is-2">
          <div class="buttons is-pulled-right">
            <button
              class='button is-success'
              :disabled="!hasEntities"
              @click='selectEntities'>Collect</button>
          </div>
        </div>
      </div>

      <template v-if='hasEntities'>
        <div
          class='is-unselectable'
          v-for='entityGroup in orderedEntityGroups'
          :key='`${entityGroup.name}`'>
          <a
            class='chip button is-rounded is-outlined entity'
            :class="{'is-success is-outlined': entityGroup.selected}"
            @click.stop="entityGroupSelected(entityGroup)">{{entityGroup.name}}</a>
          <div class='entity-group'>
            <a
              v-for='attribute in orderedAttributes(entityGroup.attributes)'
              :key='`${attribute.name}`'
              :class="{'is-success is-outlined': attribute.selected}"
              class="chip button is-rounded is-outlined is-small attribute"
              @click.stop="entityAttributeSelected({entityGroup, attribute})">
              {{attribute.name}}
            </a>
          </div>
        </div>
      </template>
      <template v-else>
        <p>No entities for this extractor.</p>
      </template>
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
  destroyed() {
    this.$store.dispatch('orchestrations/clearExtractorEntities');
  },
  computed: {
    hasEntities() {
      return this.orderedEntityGroups.length > 0;
    },
    isLoading() {
      return !Object.prototype.hasOwnProperty.call(this.extractorEntities, 'entityGroups');
    },
    orderedEntityGroups() {
      return _.orderBy(this.extractorEntities.entityGroups, 'name');
    },
    orderedAttributes() {
      return attributes => _.orderBy(attributes, 'name');
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

<style lang="scss">
.chip {
  background-color: transparent;
}

.entity-group {
  margin: .25rem .75rem 1.25rem;
}

.attribute {
  margin: .15rem;
}
</style>
