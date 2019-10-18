<script>
import { mapState } from 'vuex'
import Vue from 'vue'
import ConnectorLogo from '@/components/generic/ConnectorLogo'

export default {
  name: 'EntitiesSelectorModal',
  components: {
    ConnectorLogo
  },
  data() {
    return {
      isExpanded: false,
      selectionModeAll: { label: 'All' },
      selectionModeRecommended: { label: 'Recommended' },
      selectionModeCustom: { label: 'Custom' },
      selectionModes: []
    }
  },
  computed: {
    ...mapState('configuration', { entities: 'extractorInFocusEntities' }),
    expandableToggleLabel() {
      const prefix = this.isExpanded
        ? 'Hide'
        : `Show all ${this.entities.entityGroups.length}`
      return `${prefix} entities`
    },
    getIsSelectedMode() {
      return mode => mode === this.selectedMode
    },
    getSelectedAttributeCount() {
      let count = 0
      this.entities.entityGroups.forEach(group => {
        count += group.attributes.filter(attibute => attibute.selected).length
      })
      return count
    },
    getSelectedEntityCount() {
      let count = 0
      this.entities.entityGroups.forEach(group => {
        const hasSelectedAttribute = group.attributes.find(
          attribute => attribute.selected
        )
        if (group.selected || hasSelectedAttribute) {
          count += 1
        }
      })
      return count
    },
    getTotalAttributeCount() {
      return this.entities.entityGroups.reduce(
        (acc, curr) => acc + curr.attributes.length,
        0
      )
    },
    getTotalEntityCount() {
      return this.entities.entityGroups ? this.entities.entityGroups.length : 0
    },
    getAreAllSelected() {
      return this.getTotalAttributeCount === this.getSelectedAttributeCount
    },
    hasEntities() {
      return this.getTotalEntityCount > 0
    },
    hasSelectedAttributes() {
      return this.getSelectedAttributeCount > 0
    },
    isLoading() {
      return !this.entities
    },
    isSaveable() {
      return !this.isLoading && this.hasEntities && this.hasSelectedAttributes
    },
    selectedMode() {
      return this.getAreAllSelected
        ? this.selectionModeAll
        : this.selectionModeCustom
    },
    selectionSummary() {
      let summary = 'Make at least one selection below to save.'
      if (this.hasSelectedAttributes) {
        const attributeCount = this.getSelectedAttributeCount
        const entityCount = this.getSelectedEntityCount
        summary = `${attributeCount} attributes from ${entityCount} entities selected`
      }
      return summary
    }
  },
  created() {
    this.selectionModes = [
      this.selectionModeAll,
      this.selectionModeRecommended,
      this.selectionModeCustom
    ]
    this.extractorName = this.$route.params.extractor
    this.$store
      .dispatch('configuration/getExtractorInFocusEntities', this.extractorName)
      .then(() => {
        this.updateSelectionsBasedOnTargetSelectionMode(this.selectionModeAll)
        this.tryAutoAdvance()
      })
  },
  destroyed() {
    this.$store.dispatch('configuration/resetExtractorInFocusEntities')
  },
  methods: {
    tryAutoAdvance() {
      if (!this.hasEntities) {
        this.saveAndAdvance()
      }
    },
    close() {
      if (this.prevRoute) {
        this.$router.go(-1)
      } else {
        this.$router.push({ name: 'extractors' })
      }
    },
    entityAttributeSelected(payload) {
      this.$store.dispatch('configuration/toggleEntityAttribute', payload)
    },
    entityGroupSelected(entityGroup) {
      this.$store.dispatch('configuration/toggleEntityGroup', entityGroup)
    },
    resetSelections() {
      this.$store.dispatch('configuration/toggleAllEntityGroupsOff')
    },
    saveAndAdvance() {
      this.$store.dispatch('configuration/selectEntities').then(() => {
        this.$router.push({ name: 'loaders' })
        const message = !this.hasEntities
          ? `Auto Advance - No Entities for ${this.extractorName}`
          : `Entities Saved - ${this.extractorName}`
        Vue.toasted.global.success(message)
      })
    },
    toggleExpandable() {
      this.isExpanded = !this.isExpanded
    },
    updateSelectionsBasedOnTargetSelectionMode(targetMode) {
      if (targetMode === this.selectionModeAll) {
        this.$store.dispatch('configuration/toggleAllEntityGroupsOn')
      } else if (
        targetMode === this.selectionModeCustom &&
        this.getAreAllSelected
      ) {
        this.$store.dispatch('configuration/toggleAllEntityGroupsOff')
      }
    }
  }
}
</script>

<template>
  <div class="modal is-active">
    <div class="modal-background" @click="close"></div>
    <div class="modal-card is-wide">
      <header class="modal-card-head">
        <div class="modal-card-head-image image is-64x64 level-item">
          <ConnectorLogo :connector="extractorName" />
        </div>
        <p class="modal-card-title">Entity Selection</p>
        <button class="delete" aria-label="close" @click="close"></button>
      </header>
      <section
        class="modal-card-body"
        :class="{ 'is-overflow-y-scroll': isExpanded }"
      >
        <div class="columns" :class="{ 'is-vcentered': isLoading }">
          <div v-if="isLoading" class="column">
            <div class="content has-text-centered">
              <p>
                It may take up to a minute or more if this is the first time
                accessing this extractor's entities.
              </p>
            </div>
            <progress class="progress is-small is-info"></progress>
          </div>
        </div>

        <template v-if="!isLoading && hasEntities">
          <div class="columns is-vcentered">
            <div class="column">
              <div class="buttons has-addons">
                <!-- TODO remove :disabled attribute when/if we implement a 'Default' feature -->
                <button
                  v-for="mode in selectionModes"
                  :key="mode.label"
                  class="button"
                  :disabled="mode === selectionModes[1]"
                  :class="{
                    'is-selected is-interactive-secondary': getIsSelectedMode(
                      mode
                    )
                  }"
                  @click="updateSelectionsBasedOnTargetSelectionMode(mode)"
                >
                  {{ mode.label }}
                </button>
                <button
                  v-if="hasSelectedAttributes"
                  class="button is-text"
                  @click="resetSelections"
                >
                  Clear Selection
                </button>
              </div>
            </div>
            <div class="column">
              <div class="content is-small">
                <p
                  class="has-text-right is-italic"
                  :class="{
                    'has-text-interactive-secondary': hasSelectedAttributes
                  }"
                >
                  {{ selectionSummary }}
                </p>
              </div>
            </div>
          </div>

          <div class="expandable" :class="{ 'is-expanded': isExpanded }">
            <div
              v-for="entityGroup in entities.entityGroups"
              :key="`${entityGroup.name}`"
              class="is-unselectable"
            >
              <a
                class="chip button is-rounded is-outlined entity"
                :class="{
                  'is-interactive-secondary is-outlined': entityGroup.selected
                }"
                @click.stop="entityGroupSelected(entityGroup)"
                >{{ entityGroup.name }}</a
              >
              <div class="entity-group">
                <a
                  v-for="attribute in entityGroup.attributes"
                  :key="`${attribute.name}`"
                  :class="{
                    'is-interactive-secondary is-outlined': attribute.selected
                  }"
                  class="chip button is-rounded is-outlined is-small attribute"
                  @click.stop="
                    entityAttributeSelected({ entityGroup, attribute })
                  "
                >
                  {{ attribute.name }}
                </a>
              </div>
            </div>

            <div class="expandable-footer is-flex"></div>
          </div>

          <div class="expandable-toggle is-flex">
            <a class="button is-small" @click="toggleExpandable">{{
              expandableToggleLabel
            }}</a>
          </div>
        </template>
      </section>
      <footer class="modal-card-foot buttons is-right">
        <button class="button" @click="close">Cancel</button>
        <button
          class="button is-interactive-primary"
          :disabled="!isSaveable"
          @click="saveAndAdvance"
        >
          Save
        </button>
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
  margin: 0.25rem 0.75rem 1.25rem;
}

.attribute {
  margin: 0.15rem;
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
  margin: 0.75rem 0.75rem 0 0.75rem;
  justify-content: center;
}
</style>
