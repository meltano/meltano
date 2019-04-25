<template>
  <div>

    <!-- Loading -->
    <div v-if="isLoading" class="columns">
      <div class="column is-8 is-offset-2 box">
        <progress class="progress is-small is-info"></progress>
      </div>
    </div>

    <!-- Loaded -->
    <div v-else>
      <div class="columns">
        <div class="column is-8 is-offset-2 box">
          <template v-if='hasEntities'>

            <div class="columns">
              <div class="column">
                <h3>Entities for {{extractorEntities.extractorName}}</h3>
              </div>
              <div class="column">
                <div class="buttons is-pulled-right">
                  <button
                    class="button"
                    @click="clearExtractorInFocus()">Cancel</button>
                  <button
                    class='button is-success'
                    :disabled="!isSavable"
                    @click='selectEntities'>Save</button>
                </div>
              </div>
            </div>

            <div class="columns is-vcentered">
              <div class="column">
                <div class="buttons are-small has-addons">
                  <!-- TODO remove :disabled attribute when/if we implement a 'Default' feature -->
                  <button
                    class="button"
                    v-for='mode in selectionModes'
                    :disabled='mode === selectionModes[1]'
                    :key='mode.label'
                    :class="{ 'is-selected is-success': getIsSelectedMode(mode) }"
                    @click='setSelectedMode(mode); updateSelectionsBasedOnSelectionMode();'>
                    {{mode.label}}
                  </button>
                </div>
              </div>
              <div class="column">
                <div class="content is-small">
                  <p class='has-text-right is-italic'>
                    {{selectionSummary}}
                  </p>
                </div>
              </div>
            </div>

            <div
              class="columns"
              v-if='this.selectedMode === this.selectionModes[0]'>
              <div class="column">
                <article class="message is-warning is-small">
                  <div class="message-header">
                    <p>Performance Warning</p>
                  </div>
                  <div class="message-body">
                    <p>Selecting <span class='is-italic'>all</span> may negatively impact extraction performance. Consider a custom selection before saving.</p>
                  </div>
                </article>
              </div>
            </div>

            <div
              class="expandable"
              :class="{ 'is-expanded': isExpanded }">
              <div
                class='is-unselectable'
                v-for='entityGroup in extractorEntities.entityGroups'
                :key='`${entityGroup.name}`'>
                <a
                  class='chip button is-rounded is-outlined entity'
                  :class="{'is-success is-outlined': entityGroup.selected}"
                  @click.stop="entityGroupSelected(entityGroup)">{{entityGroup.name}}</a>
                <div class='entity-group'>
                  <a
                    v-for='attribute in entityGroup.attributes'
                    :key='`${attribute.name}`'
                    :class="{'is-success is-outlined': attribute.selected}"
                    class="chip button is-rounded is-outlined is-small attribute"
                    @click.stop="entityAttributeSelected({entityGroup, attribute})">
                    {{attribute.name}}
                  </a>
                </div>
              </div>

              <div class='expandable-footer is-flex'></div>
            </div>

            <div class='expandable-toggle is-flex'>
              <a
                class="button is-small"
                @click="toggleExpandable">{{expandableToggleLabel}}</a>
            </div>

          </template>
          <template v-else>
            <p>No entities for this extractor.</p>
          </template>
        </div>
      </div>

    </div>
  </div>
</template>

<script>
import { mapState } from 'vuex';

export default {
  name: 'EntitiesSelector',
  props: {
    extractor: {
      type: Object,
      default() {
        return {};
      },
    },
  },
  created() {
    //  Set to default mode. Later update based on persisted state and preselect matching entities
    this.setSelectedMode(this.selectionModes[2]);
    this.$store.dispatch('orchestrations/getExtractorEntities', this.extractor.name);
  },
  destroyed() {
    this.$store.dispatch('orchestrations/clearExtractorEntities');
  },
  data() {
    return {
      isExpanded: false,
      selectedMode: null,
      selectionModes: [
        { label: 'All' },
        { label: 'Default' },
        { label: 'Custom' },
      ],
    };
  },
  computed: {
    ...mapState('orchestrations', [
      'extractorEntities',
    ]),
    expandableToggleLabel() {
      const prefix = this.isExpanded
        ? 'Hide majority of'
        : `Show all ${this.extractorEntities.entityGroups.length}`;
      return `${prefix} entities`;
    },
    getIsSelectedMode() {
      return mode => mode === this.selectedMode;
    },
    getSelectedAttributeCount() {
      let count = 0;
      this.extractorEntities.entityGroups.forEach((group) => {
        count += group.attributes.filter(attibute => attibute.selected).length;
      });
      return count;
    },
    getSelectedEntityCount() {
      let count = 0;
      this.extractorEntities.entityGroups.forEach((group) => {
        const hasSelectedAttribute = group.attributes.find(attribute => attribute.selected);
        if (group.selected || hasSelectedAttribute) {
          count += 1;
        }
      });
      return count;
    },
    hasEntities() {
      return this.extractorEntities.entityGroups.length > 0;
    },
    isLoading() {
      return !Object.prototype.hasOwnProperty.call(this.extractorEntities, 'entityGroups');
    },
    isSavable() {
      return this.hasEntities && this.getSelectedAttributeCount > 0;
    },
    selectionSummary() {
      let summary = 'Make at least one selection below to save.';
      if (this.getSelectedAttributeCount > 0) {
        summary = `${this.getSelectedAttributeCount} attributes from ${this.getSelectedEntityCount} entities selected`
      }
      return summary;
    },
  },
  methods: {
    clearExtractorInFocus() {
      this.$emit('clearExtractorInFocus');
    },
    entityAttributeSelected(payload, shouldUpdateSelectedMode = false) {
      this.$store.dispatch('orchestrations/toggleEntityAttribute', payload);
      if (shouldUpdateSelectedMode) {
        this.setSelectedMode(this.selectionModes[2]);
      }
    },
    entityGroupSelected(entityGroup, shouldUpdateSelectedMode = false) {
      this.$store.dispatch('orchestrations/toggleEntityGroup', entityGroup);
      if (shouldUpdateSelectedMode) {
        this.setSelectedMode(this.selectionModes[2]);
      }
    },
    toggleExpandable() {
      this.isExpanded = !this.isExpanded;
    },
    selectEntities() {
      this.$store.dispatch('orchestrations/selectEntities');
    },
    setSelectedMode(mode) {
      this.selectedMode = mode;
    },
    updateSelectionsBasedOnSelectionMode() {
      if (this.selectedMode === this.selectionModes[0]) {
        this.extractorEntities.entityGroups.forEach((group) => {
          if (!group.selected) {
            this.entityGroupSelected(group, true);
          }
        });
      } else if (this.selectedMode === this.selectionModes[2]) {
        this.extractorEntities.entityGroups.forEach((group) => {
          const hasSelectedAttribute = group.attributes.find(attribute => attribute.selected);
          if (group.selected || hasSelectedAttribute) {
            this.entityGroupSelected(group, true);
          }
        });
      }
    },
  },
};
</script>

<style lang="scss">
@import '@/scss/utils.scss';

.chip {
  background-color: transparent;
}

.entity-group {
  margin: .25rem .75rem 1.25rem;
}

.attribute {
  margin: .15rem;
}

.expandable {
  max-height: 210px;
  overflow: hidden;
  position: relative;

  &.is-expanded {
    max-height: none;
    overflow: initial;

    .expandable-footer {
      box-shadow: none;
    }
  }

  .expandable-footer {
    position: absolute;
    bottom: 0;
    height: 8px;
    width: 100%;

    @extend .inset-overflow-shadow;
  }
}

.expandable-toggle {
  margin: .75rem;
  justify-content: center;
}

</style>
