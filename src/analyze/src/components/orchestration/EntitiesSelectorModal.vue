<script>
import { mapGetters, mapState } from 'vuex';

export default {
  name: 'EntitiesSelectorModal',
  created() {
    this.selectionModes = [
      this.selectionModeAll,
      this.selectionModeRecommended,
      this.selectionModeCustom,
    ];
    this.extractorNameFromRoute = this.$route.params.extractor;
    this.$store.dispatch('configuration/getExtractorInFocusEntities', this.extractorNameFromRoute);
  },
  destroyed() {
    this.$store.dispatch('configuration/clearExtractorInFocusEntities');
  },
  data() {
    return {
      isExpanded: false,
      selectionModeAll: { label: 'All' },
      selectionModeRecommended: { label: 'Recommended' },
      selectionModeCustom: { label: 'Custom' },
      selectionModes: [],
    };
  },
  computed: {
    ...mapGetters('configuration', [
      'getExtractorImageUrl',
      'getExtractorNameWithoutPrefixedTapDash',
    ]),
    ...mapState('configuration', [
      'extractorInFocusEntities',
    ]),
    expandableToggleLabel() {
      const prefix = this.isExpanded
        ? 'Hide'
        : `Show all ${this.extractorInFocusEntities.entityGroups.length}`;
      return `${prefix} entities`;
    },
    getIsSelectedMode() {
      return mode => mode === this.selectedMode;
    },
    getSelectedAttributeCount() {
      let count = 0;
      this.extractorInFocusEntities.entityGroups.forEach((group) => {
        count += group.attributes.filter(attibute => attibute.selected).length;
      });
      return count;
    },
    getSelectedEntityCount() {
      let count = 0;
      this.extractorInFocusEntities.entityGroups.forEach((group) => {
        const hasSelectedAttribute = group.attributes.find(attribute => attribute.selected);
        if (group.selected || hasSelectedAttribute) {
          count += 1;
        }
      });
      return count;
    },
    getTotalAttributeCount() {
      return this.extractorInFocusEntities.entityGroups
        .reduce((acc, curr) => acc + curr.attributes.length, 0);
    },
    getTotalEntityCount() {
      return this.extractorInFocusEntities.entityGroups.length;
    },
    getAreAllSelected() {
      return this.getTotalAttributeCount === this.getSelectedAttributeCount;
    },
    hasEntities() {
      return this.getTotalEntityCount > 0;
    },
    hasSelectedAttributes() {
      return this.getSelectedAttributeCount > 0;
    },
    isLoading() {
      return !Object.prototype.hasOwnProperty.call(this.extractorInFocusEntities, 'entityGroups');
    },
    isSaveable() {
      return this.hasEntities && this.hasSelectedAttributes;
    },
    selectedMode() {
      // Custom by default until/if we implement Default selections
      let mode = this.selectionModeCustom;
      if (this.getAreAllSelected) {
        mode = this.selectionModeAll;
      }
      return mode;
    },
    selectionSummary() {
      let summary = 'Make at least one selection below to save.';
      if (this.hasSelectedAttributes) {
        summary = `${this.getSelectedAttributeCount} attributes from ${this.getSelectedEntityCount} entities selected`;
      }
      return summary;
    },
  },
  methods: {
    clearSelections() {
      this.$store.dispatch('configuration/toggleAllEntityGroupsOff');
    },
    close() {
      if (this.prevRoute) {
        this.$router.go(-1);
      } else {
        this.$router.push({ name: 'entities' });
      }
    },
    entityAttributeSelected(payload) {
      this.$store.dispatch('configuration/toggleEntityAttribute', payload);
    },
    entityGroupSelected(entityGroup) {
      this.$store.dispatch('configuration/toggleEntityGroup', entityGroup);
    },
    toggleExpandable() {
      this.isExpanded = !this.isExpanded;
    },
    selectEntitiesAndBeginLoaderInstall() {
      this.$store.dispatch('configuration/selectEntities');
      this.$router.push({ name: 'loaders' });
    },
    updateSelectionsBasedOnTargetSelectionMode(targetMode) {
      if (targetMode === this.selectionModeAll) {
        this.$store.dispatch('configuration/toggleAllEntityGroupsOn');
      } else if (targetMode === this.selectionModeCustom && this.getAreAllSelected) {
        this.$store.dispatch('configuration/toggleAllEntityGroupsOff');
      }
    },
  },
};
</script>

<template>

  <div class="modal is-active">
    <div class="modal-background" @click="close"></div>
    <div class="modal-card is-wide">
      <header class="modal-card-head">
        <div class="modal-card-head-image image is-64x64 level-item">
          <img
            :src='getExtractorImageUrl(extractorNameFromRoute)'
            :alt="`${getExtractorNameWithoutPrefixedTapDash(extractorNameFromRoute)} logo`">
        </div>
        <p class="modal-card-title">Entity Selection</p>
        <button class="delete" aria-label="close" @click="close"></button>
      </header>
      <section class="modal-card-body">

        <div
          class="columns"
          :class="{ 'is-vcentered': isLoading }">

          <div v-if='isLoading' class="column">
            <div class="content has-text-centered">
              <p>It may take up to a minute or more if this is the first time accessing this extractor's entities.</p>
            </div>
            <progress class="progress is-small is-info"></progress>
          </div>
        </div>

        <template v-if='!isLoading && hasEntities'>
          <div class="columns is-vcentered">
            <div class="column">
              <div class="buttons are-small has-addons">
                <!-- TODO remove :disabled attribute when/if we implement a 'Default' feature -->
                <button
                  class='button is-outlined'
                  v-for='mode in selectionModes'
                  :disabled='mode === selectionModes[1]'
                  :key='mode.label'
                  :class="{ 'is-selected is-interactive-secondary': getIsSelectedMode(mode) }"
                  @click='updateSelectionsBasedOnTargetSelectionMode(mode);'>
                  {{mode.label}}
                </button>
                <button
                  class='button is-text'
                  v-if='hasSelectedAttributes'
                  @click='clearSelections'>
                  Clear Selection
                </button>
              </div>
            </div>
            <div class="column">
              <div class="content is-small">
                <p
                  class='has-text-right is-italic'
                  :class="{ 'has-text-interactive-secondary': hasSelectedAttributes }">
                  {{selectionSummary}}
                </p>
              </div>
            </div>
          </div>

          <div
            class="columns"
            v-if='this.selectedMode === this.selectionModeAll'>
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
              v-for='entityGroup in extractorInFocusEntities.entityGroups'
              :key='`${entityGroup.name}`'>
              <a
                class='chip button is-rounded is-outlined entity'
                :class="{'is-interactive-secondary is-outlined': entityGroup.selected}"
                @click.stop="entityGroupSelected(entityGroup)">{{entityGroup.name}}</a>
              <div class='entity-group'>
                <a
                  v-for='attribute in entityGroup.attributes'
                  :key='`${attribute.name}`'
                  :class="{'is-interactive-secondary is-outlined': attribute.selected}"
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

        <template v-if='!isLoading && !hasEntities'>
          <div class="content">
            <p>There are no entities for this extractor.</p>
          </div>
        </template>

      </section>
      <footer class="modal-card-foot buttons is-right">
        <button
          class="button"
          @click="close">Cancel</button>
        <button
          v-if='!isLoading'
          class='button is-interactive-primary'
          :disabled="!isSaveable"
          @click='selectEntitiesAndBeginLoaderInstall'>Save</button>
      </footer>
    </div>
  </div>

</template>

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
  margin: .75rem .75rem 0 .75rem;
  justify-content: center;
}

</style>
