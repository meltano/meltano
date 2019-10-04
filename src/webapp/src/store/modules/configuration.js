import Vue from 'vue'

import lodash from 'lodash'

import orchestrationsApi from '../../api/orchestrations'
import poller from '@/utils/poller'
import utils from '@/utils/utils'

const defaultState = utils.deepFreeze({
  connectionInFocusConfiguration: {},
  extractorInFocusConfiguration: {},
  extractorInFocusEntities: {},
  loaderInFocusConfiguration: {},
  pipelinePollers: [],
  pipelines: [],
  recentELTSelections: {
    extractor: null,
    loader: null,
    transform: null
  },
  transformOptions: [
    { label: 'Skip', name: 'skip' },
    { label: 'Run', name: 'run' },
    { label: 'Only', name: 'only' }
  ]
})

const getters = {
  getHasPipelines(state) {
    return state.pipelines.length > 0
  },

  getHasValidConfigSettings(_, getters) {
    return (configSettings, settingsGroupValidation = null) => {
      return settingsGroupValidation
        ? getters.getHasGroupValidationConfigSettings(
            configSettings,
            settingsGroupValidation
          )
        : getters.getHasDefaultValidationConfigSettings(configSettings)
    }
  },

  getHasDefaultValidationConfigSettings() {
    return configSettings => {
      const isKindBoolean = setting =>
        setting.kind && setting.kind === 'boolean'
      const isValid = setting =>
        isKindBoolean(setting) || Boolean(configSettings.config[setting.name])
      return (
        configSettings.settings &&
        lodash.every(configSettings.settings, isValid)
      )
    }
  },

  getHasGroupValidationConfigSettings() {
    return (configSettings, settingsGroupValidation) => {
      const matchGroup = settingsGroupValidation.find(group => {
        if (configSettings.settings) {
          const groupedSettings = configSettings.settings.filter(setting =>
            group.includes(setting.name)
          )
          const isValid = setting =>
            Boolean(configSettings.config[setting.name])
          return lodash.every(groupedSettings, isValid)
        }
      })
      return configSettings.settings && Boolean(matchGroup)
    }
  },

  getRunningPipelines(state) {
    return state.pipelines.filter(pipeline => pipeline.isRunning)
  },

  getRunningPipelineJobIds(state) {
    return state.pipelinePollers.map(
      pipelinePoller => pipelinePoller.getMetadata().jobId
    )
  }
}

const actions = {
  getAllPipelineSchedules({ commit, dispatch }) {
    orchestrationsApi.getAllPipelineSchedules().then(response => {
      commit('setPipelines', response.data)
      dispatch('rehydratePollers')
    })
  },

  // eslint-disable-next-line no-shadow
  getConnectionConfiguration({ commit, dispatch }, connection) {
    return dispatch('getPluginConfiguration', {
      name: connection,
      type: 'connections'
    }).then(response => {
      commit('setInFocusConfiguration', {
        configuration: response.data,
        target: 'connectionInFocusConfiguration'
      })
    })
  },

  getExtractorConfiguration({ commit, dispatch }, extractor) {
    dispatch('getPluginConfiguration', {
      name: extractor,
      type: 'extractors'
    }).then(response => {
      commit('setInFocusConfiguration', {
        configuration: response.data,
        target: 'extractorInFocusConfiguration'
      })
    })
  },

  getExtractorInFocusEntities({ commit }, extractorName) {
    return orchestrationsApi
      .getExtractorInFocusEntities(extractorName)
      .then(response => {
        commit('setAllExtractorInFocusEntities', response.data)
      })
  },

  getJobLog(_, jobId) {
    return orchestrationsApi.getJobLog({ jobId })
  },

  getLoaderConfiguration({ commit, dispatch }, loader) {
    dispatch('getPluginConfiguration', { name: loader, type: 'loaders' }).then(
      response => {
        commit('setInFocusConfiguration', {
          configuration: response.data,
          target: 'loaderInFocusConfiguration'
        })
      }
    )
  },

  getPluginConfiguration(_, pluginPayload) {
    return orchestrationsApi.getPluginConfiguration(pluginPayload)
  },

  getPolledPipelineJobStatus({ commit, getters, state }) {
    return orchestrationsApi
      .getPolledPipelineJobStatus({ jobIds: getters.getRunningPipelineJobIds })
      .then(response => {
        response.data.jobs.forEach(jobStatus => {
          if (jobStatus.isComplete) {
            const targetPoller = state.pipelinePollers.find(
              pipelinePoller =>
                pipelinePoller.getMetadata().jobId === jobStatus.jobId
            )
            commit('removePipelinePoller', targetPoller)

            const targetPipeline = state.pipelines.find(
              pipeline => pipeline.name === jobStatus.jobId
            )
            commit('setPipelineIsRunning', {
              pipeline: targetPipeline,
              value: false
            })
          }
        })
      })
  },

  queuePipelinePoller({ commit, dispatch }, pollMetadata) {
    const pollFn = () => dispatch('getPolledPipelineJobStatus')
    const pipelinePoller = poller.create(pollFn, pollMetadata, 8000)
    pipelinePoller.init()
    commit('addPipelinePoller', pipelinePoller)
  },

  rehydratePollers({ dispatch, getters, state }) {
    // Handle page refresh condition resulting in jobs running but no pollers
    getters.getRunningPipelines.forEach(pipeline => {
      const jobId = pipeline.name
      const isMissingPoller =
        state.pipelinePollers.find(
          pipelinePoller => pipelinePoller.getMetadata().jobId === jobId
        ) === undefined
      if (isMissingPoller) {
        dispatch('queuePipelinePoller', { jobId })
      }
    })
  },

  resetConnectionInFocusConfiguration: ({ commit }) =>
    commit('reset', 'connectionInFocusConfiguration'),

  resetExtractorInFocusConfiguration: ({ commit }) =>
    commit('reset', 'extractorInFocusConfiguration'),

  resetExtractorInFocusEntities: ({ commit }) =>
    commit('reset', 'extractorInFocusEntities'),

  resetLoaderInFocusConfiguration: ({ commit }) =>
    commit('reset', 'loaderInFocusConfiguration'),

  run({ commit, dispatch }, pipeline) {
    return orchestrationsApi.run(pipeline).then(response => {
      dispatch('queuePipelinePoller', response.data)
      commit('setPipelineIsRunning', { pipeline, value: true })
      commit('setPipelineJobId', { pipeline, jobId: response.data.jobId })
    })
  },

  savePipelineSchedule({ commit }, pipeline) {
    return orchestrationsApi.savePipelineSchedule(pipeline).then(response => {
      pipeline = Object.assign(pipeline, response.data)
      commit('updatePipelines', pipeline)
    })
  },

  savePluginConfiguration(_, configPayload) {
    orchestrationsApi.savePluginConfiguration(configPayload)
  },

  selectEntities({ state }) {
    orchestrationsApi
      .selectEntities(state.extractorInFocusEntities)
      .then(() => {
        // TODO confirm success or handle error in UI
      })
  },

  toggleAllEntityGroupsOff({ commit, dispatch, state }) {
    state.extractorInFocusEntities.entityGroups.forEach(entityGroup => {
      if (entityGroup.selected) {
        dispatch('toggleEntityGroup', entityGroup)
      } else {
        const selectedAttributes = entityGroup.attributes.filter(
          attribute => attribute.selected
        )
        if (selectedAttributes.length > 0) {
          selectedAttributes.forEach(attribute =>
            commit('toggleSelected', attribute)
          )
        }
      }
    })
  },

  toggleAllEntityGroupsOn({ dispatch, state }) {
    state.extractorInFocusEntities.entityGroups.forEach(group => {
      if (!group.selected) {
        dispatch('toggleEntityGroup', group)
      }
    })
  },

  toggleEntityAttribute({ commit }, { entityGroup, attribute }) {
    commit('toggleSelected', attribute)
    const hasDeselectedAttribute =
      attribute.selected === false && entityGroup.selected
    const hasAllSelectedAttributes = !entityGroup.attributes.find(
      attr => !attr.selected
    )
    if (hasDeselectedAttribute || hasAllSelectedAttributes) {
      commit('toggleSelected', entityGroup)
    }
  },

  toggleEntityGroup({ commit }, entityGroup) {
    commit('toggleSelected', entityGroup)
    const selected = entityGroup.selected
    entityGroup.attributes.forEach(attribute => {
      if (attribute.selected !== selected) {
        commit('toggleSelected', attribute)
      }
    })
  },

  updateRecentELTSelections({ commit }, updatePayload) {
    commit('setELTRecentSelection', updatePayload)
  }
}

const mutations = {
  addPipelinePoller(state, pipelinePoller) {
    state.pipelinePollers.push(pipelinePoller)
  },

  removePipelinePoller(state, pipelinePoller) {
    pipelinePoller.dispose()
    const idx = state.pipelinePollers.indexOf(pipelinePoller)
    state.pipelinePollers.splice(idx, 1)
  },

  reset(state, attr) {
    if (defaultState.hasOwnProperty(attr)) {
      state[attr] = lodash.cloneDeep(defaultState[attr])
    }
  },

  setAllExtractorInFocusEntities(state, entitiesData) {
    state.extractorInFocusEntities = entitiesData
      ? {
          extractorName: entitiesData.extractorName,
          entityGroups: entitiesData.entityGroups
        }
      : {}
  },

  setELTRecentSelection(state, { type, value }) {
    state.recentELTSelections[type] = value
  },

  setInFocusConfiguration(state, { configuration, target }) {
    configuration.settings.forEach(setting => {
      const isIso8601Date = setting.kind && setting.kind === 'date_iso8601'
      const isDefaultNeeded =
        configuration.config.hasOwnProperty(setting.name) &&
        configuration.config[setting.name] === null
      if (isIso8601Date && isDefaultNeeded) {
        configuration.config[setting.name] = utils.getFirstOfMonthAsIso8601()
      }
    })
    state[target] = configuration
  },

  setPipelineIsRunning(_, { pipeline, value }) {
    Vue.set(pipeline, 'isRunning', value)
  },

  setPipelineJobId(_, { pipeline, jobId }) {
    Vue.set(pipeline, 'jobId', jobId)
  },

  setPipelines(state, pipelines) {
    pipelines.forEach(pipeline => {
      pipeline.startDate = utils.dateIso8601(pipeline.startDate)
    })
    state.pipelines = pipelines
  },

  toggleSelected(state, selectable) {
    Vue.set(selectable, 'selected', !selectable.selected)
  },

  updatePipelines(state, pipeline) {
    pipeline.startDate = utils.dateIso8601(pipeline.startDate)
    state.pipelines.push(pipeline)
  }
}

export default {
  namespaced: true,
  state: lodash.cloneDeep(defaultState),
  getters,
  actions,
  mutations
}
