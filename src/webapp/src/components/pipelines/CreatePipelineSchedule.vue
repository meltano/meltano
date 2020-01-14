<script>
import { mapGetters, mapState } from 'vuex'
import Vue from 'vue'

import Dropdown from '@/components/generic/Dropdown'
import ExtractorList from '@/components/pipelines/ExtractorList'

export default {
  name: 'CreatePipelineSchedule',
  components: {
    Dropdown,
    ExtractorList
  },
  data() {
    return {
      intervalOptions: [
        '@once',
        '@hourly',
        '@daily',
        '@weekly',
        '@monthly',
        '@yearly'
      ],
      isSaving: false,
      pipeline: {
        name: '',
        extractor: '',
        loader: 'target-postgres', // Refactor vs. hard code when we again want to display in the UI
        transform: 'run', // Refactor vs. hard code when we again want to display in the UI
        interval: '',
        isRunning: false
      }
    }
  },
  computed: {
    getDataSourceLabel() {
      return this.pipeline.extractor || 'None'
    },
    isSaveable() {
      return false
    }
  },
  created() {
    this.$store.dispatch('plugins/getInstalledPlugins').then(this.prefillForm)
  },
  methods: {
    prefillForm() {
      this.pipeline.name = `pipeline-${new Date().getTime()}`

      // const defaultExtractor =
      //   this.recentELTSelections.extractor ||
      //   (!_.isEmpty(this.installedPlugins.extractors) &&
      //     this.installedPlugins.extractors[0])
      // this.pipeline.extractor = defaultExtractor ? defaultExtractor.name : ''

      // const defaultLoader =
      //   this.recentELTSelections.loader ||
      //   (!_.isEmpty(this.installedPlugins.loaders) &&
      //     this.installedPlugins.loaders[0])
      // this.pipeline.loader = defaultLoader ? defaultLoader.name : ''

      // this.updateDefaultTransforms(defaultExtractor.namespace)

      this.pipeline.interval = !_.isEmpty(this.intervalOptions)
        ? this.intervalOptions[0]
        : ''
    },
    save() {
      this.isSaving = true
    }
  }
}
</script>

<template>
  <div class="box">
    <table class="table is-fullwidth is-narrow is-hoverable">
      <thead>
        <tr>
          <th>
            <span>Data Source</span>
            <span
              class="icon has-text-grey-light tooltip is-tooltip-right"
              data-tooltip="The integration or custom data source to connect to"
            >
              <font-awesome-icon icon="info-circle"></font-awesome-icon>
            </span>
          </th>
          <th>
            <span>Update Interval</span>
            <span
              class="icon has-text-grey-light tooltip is-tooltip-right"
              data-tooltip="How frequently this dataset should be updated"
            >
              <font-awesome-icon icon="info-circle"></font-awesome-icon>
            </span>
          </th>
          <th>
            <span>Name</span>
            <span
              class="icon has-text-grey-light tooltip is-tooltip-right"
              data-tooltip="The name of this data pipeline"
            >
              <font-awesome-icon icon="info-circle"></font-awesome-icon>
            </span>
          </th>
          <th></th>
        </tr>
      </thead>
      <tbody>
        <tr>
          <td>
            <Dropdown
              :label="getDataSourceLabel"
              button-classes="is-outlined"
              :tooltip="{
                classes: 'is-tooltip-right',
                message:
                  'Select an integration or custom data source to connect to'
              }"
              menu-classes="dropdown-menu-600"
              is-full-width
            >
              <div class="dropdown-content is-unselectable">
                <ExtractorList />
              </div>
            </Dropdown>
          </td>
          <td>
            <div class="control is-expanded">
              <span
                class="select is-fullwidth"
                :class="{ 'is-loading': !pipeline.interval }"
              >
                <select
                  v-model="pipeline.interval"
                  :class="{ 'has-text-success': pipeline.interval }"
                >
                  <option v-for="interval in intervalOptions" :key="interval">{{
                    interval
                  }}</option>
                </select>
              </span>
            </div>
          </td>
          <td>
            <div class="control is-expanded">
              <input
                ref="name"
                v-model="pipeline.name"
                class="input"
                :class="{
                  'has-text-success': pipeline.name
                }"
                type="text"
                placeholder="Name"
                @focus="$event.target.select()"
              />
            </div>
          </td>
          <td>
            <div class="buttons is-right">
              <a
                class="button is-interactive-primary tooltip is-tooltip-left"
                data-tooltip="Create integration or custom data connection."
                :class="{ 'is-loading': isSaving }"
                :disabled="!isSaveable"
                >Create</a
              >
            </div>
          </td>
        </tr>
      </tbody>
    </table>
  </div>
</template>

<style lang="scss"></style>
