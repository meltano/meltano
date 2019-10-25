<script>
import { mapState } from 'vuex'
import Vue from 'vue'

export default {
  name: 'Transforms',
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
      <div class="column">
        <div class="box">
          <div class="columns">
            <div class="column">
              <h2 class="title is-5">Documentation</h2>
              <div class="content">
                <p>
                  Below, you'll find the documentation for transformations in
                  this Meltano project. The documentation includes:
                </p>
                <ol>
                  <li>
                    <a
                      class="has-text-underlined"
                      target="_blank"
                      href="https://www.meltano.com/tutorials/create-custom-transforms-and-models.html#adding-custom-transforms"
                      >Custom transformations</a
                    >
                  </li>
                  <li>
                    <a
                      class="has-text-underlined"
                      target="_blank"
                      href="https://www.meltano.com/docs/transforms.html#transform"
                      >Default transformations</a
                    >
                    that ship with Meltano
                  </li>
                </ol>
              </div>
            </div>

            <div class="column">
              <h2 class="title is-5">Options</h2>
              <div class="content">
                <p>Transformation options:</p>
                <ul>
                  <li
                    :class="{
                      'has-text-weight-bold': getIsSelectedTransformOption(
                        transformOptions[0]
                      )
                    }"
                  >
                    Skip (EL): do not run the default transforms with extract
                    and load
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
                    Only (T): only run default transforms, do not extract and
                    load
                  </li>
                </ul>
              </div>

              <div class="field is-grouped is-pulled-right">
                <div class="control buttons has-addons">
                  <button
                    v-for="transformOption in transformOptions"
                    :key="transformOption.label"
                    class="button"
                    :class="{
                      'is-selected is-interactive-secondary':
                        transformOption === selectedTransformOption
                    }"
                    @click="updateTransformTypeSelection(transformOption)"
                  >
                    {{ transformOption.label }}
                  </button>
                </div>
                <div class="control">
                  <a
                    data-test-id="save-transform"
                    class="button is-interactive-primary"
                    @click="saveTransformAndGoToSchedules"
                    >Save</a
                  >
                </div>
              </div>
            </div>
          </div>

          <div class="is-flex">
            <iframe
              class="dbt-docs-iframe"
              src="http://localhost:5000/-/dbt/"
            />
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<style lang="scss">
.dbt-docs-iframe {
  flex-grow: 1;
  min-height: 100vh;
}
</style>
