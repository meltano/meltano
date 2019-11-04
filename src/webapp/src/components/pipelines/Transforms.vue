<script>
import { mapActions, mapGetters, mapState } from 'vuex'
import Vue from 'vue'

export default {
  name: 'Transforms',
  data() {
    return {
      selectedTransformOption: null
    }
  },
  computed: {
    ...mapGetters('system', ['hasDbtDocs']),
    ...mapState('configuration', ['recentELTSelections', 'transformOptions']),
    dbtDocsUrl() {
      return this.$flask.dbtDocsUrl
    },
    getIsSelectedTransformOption() {
      return transformOption => transformOption === this.selectedTransformOption
    }
  },
  created() {
    const defaultTransform =
      this.recentELTSelections.transform || this.transformOptions[0]
    this.selectedTransformOption = defaultTransform
    this.checkHasDbtDocs()
  },
  methods: {
    ...mapActions('system', ['checkHasDbtDocs']),
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
                  Meltano uses
                  <a
                    class="has-text-underlined"
                    href="https://www.meltano.com/docs/architecture.html#transformation-methodology-dbt"
                    target="_blank"
                    >dbt</a
                  >
                  to transform the data extracted from the data sources into a
                  consistent representation called <strong>Model</strong>, but
                  Meltano will <strong>never</strong> manipulate the source data
                  file.
                </p>
                <p v-if="hasDbtDocs">
                  An ELT run is <em>required before</em> you can view the
                  <a
                    class="has-text-underlined"
                    :href="dbtDocsUrl"
                    target="_blank"
                    >dbt generated transform model documentation</a
                  >.
                </p>
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

                <p>
                  Current transform limititations:
                </p>
                <ul>
                  <li>"Run" requires <code>target-postgres</code></li>
                  <li>
                    "Skip" is required for <code>target-snowflake</code> and
                    <code>target-csv</code>
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
