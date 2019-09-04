<script>
import { mapState } from 'vuex'
import Vue from 'vue'

import Message from '@/components/generic/Message'

export default {
  name: 'Transforms',
  components: {
    Message
  },
  data() {
    return {
      selectedTransformOption: null
    }
  },
  computed: {
    ...mapState('configuration', ['recentELTSelections', 'transformOptions']),
    getIsSelectedTransformOption() {
      return transformOption => transformOption === this.selectedTransformOption
    }
  },
  created() {
    const defaultTransform =
      this.recentELTSelections.transform || this.transformOptions[0]
    this.selectedTransformOption = defaultTransform
  },
  methods: {
    saveTransformAndGoToSchedules() {
      this.$store
        .dispatch('configuration/updateRecentELTSelections', {
          type: 'transform',
          value: this.selectedTransformOption
        })
        .then(() => {
          this.$router.push({ name: 'schedules' })
          Vue.toasted.global.success(
            `Transform Saved - ${this.selectedTransformOption.label}`
          )
        })
    },
    updateTransformTypeSelection(transformType) {
      this.selectedTransformOption = transformType
    }
  }
}
</script>

<template>
  <div>
    <div class="columns">
      <div class="column is-three-fifths is-offset-one-fifth">
        <div class="content has-text-centered">
          <p class="level-item buttons">
            <a class="button is-small is-static is-marginless is-borderless">
              <span>Tell us the type of transformation you want</span>
            </a>
            <span class="step-spacer">then</span>
            <a class="button is-small is-static is-marginless is-borderless">
              <span>Schedule a run</span>
            </a>
          </p>
        </div>
      </div>
    </div>

    <div class="columns">
      <div class="column is-three-fifths is-offset-one-fifth">
        <div class="box">
          <Message>
            <p>
              Currently, for the UI, we only support the
              <em>default transforms</em> that ship with Meltano. The CLI
              however
              <a
                href="https://www.meltano.com/docs/tutorial.html#advanced-adding-custom-transformations-and-models"
                >provides more options</a
              >. Longer term we ancipate this view to support transform
              creation, editing, and selection.
            </p>
            <p>Current Options:</p>
            <ul>
              <li
                :class="{
                  'has-text-weight-bold': getIsSelectedTransformOption(
                    transformOptions[0]
                  )
                }"
              >
                Skip (EL): do not run the default transforms with extract and
                load
              </li>
              <li
                :class="{
                  'has-text-weight-bold': getIsSelectedTransformOption(
                    transformOptions[1]
                  )
                }"
              >
                Run (ELT): run the default transforms with extract and load
              </li>
              <li
                :class="{
                  'has-text-weight-bold': getIsSelectedTransformOption(
                    transformOptions[2]
                  )
                }"
              >
                Only (T): only run default transforms, do not extract and load
              </li>
            </ul>
          </Message>

          <div class="level">
            <div class="level-left">
              <div class="buttons has-addons">
                <button
                  v-for="transformOption in transformOptions"
                  :key="transformOption.label"
                  class="button is-outlined"
                  :class="{
                    'is-selected is-interactive-secondary':
                      transformOption === selectedTransformOption
                  }"
                  @click="updateTransformTypeSelection(transformOption)"
                >
                  {{ transformOption.label }}
                </button>
              </div>
            </div>

            <div class="level-right">
              <a
                class="button is-interactive-primary"
                @click="saveTransformAndGoToSchedules"
                >Save</a
              >
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<style lang="scss"></style>
