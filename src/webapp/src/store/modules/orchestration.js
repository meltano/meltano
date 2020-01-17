import Vue from 'vue'

import lodash from 'lodash'

import orchestrationsApi from '../../api/orchestrations'
import poller from '@/utils/poller'
import utils from '@/utils/utils'

const defaultState = utils.deepFreeze({
  extractorInFocusConfiguration: {},
  loaderInFocusConfiguration: {},
  pipelinePollers: [],
  pipelines: [],
  recentELTSelections: {
    extractor: null,
    loader: null
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
  },

  getSuccessfulPipelines(state) {
    return state.pipelines.filter(pipeline => pipeline.hasEverSucceeded)
  }
}

const actions = {
  addConfigurationProfile(_, profile) {
    return orchestrationsApi.addConfigurationProfile(profile).catch(error => {
      Vue.toasted.global.error(error)
    })
  },

  deletePipelineSchedule({ commit }, pipeline) {
    let status = {
      pipeline,
      isRunning: pipeline.isRunning,
      isDeleting: true
    }
    commit('setPipelineStatus', status)
    return orchestrationsApi.deletePipelineSchedule(pipeline).then(() => {
      commit('setPipelineStatus', Object.assign({ isDeleting: false }, status))
      commit('deletePipeline', pipeline)
    })
  },

  getAllPipelineSchedules({ commit, dispatch }) {
    return orchestrationsApi.getAllPipelineSchedules().then(response => {
      commit('setPipelines', response.data)
      dispatch('rehydratePollers')
    })
  },

  getExtractorConfiguration({ commit, dispatch }, extractor) {
    return dispatch('getPluginConfiguration', {
      name: extractor,
      type: 'extractors'
    }).then(response => {
      commit('setInFocusConfiguration', {
        configuration: response.data,
        target: 'extractorInFocusConfiguration'
      })
    })
  },

  getJobLog(_, jobId) {
    return orchestrationsApi.getJobLog({ jobId })
  },

  getLoaderConfiguration({ commit, dispatch }, loader) {
    return dispatch('getPluginConfiguration', {
      name: loader,
      type: 'loaders'
    }).then(response => {
      commit('setInFocusConfiguration', {
        configuration: response.data,
        target: 'loaderInFocusConfiguration'
      })
    })
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

            commit('setPipelineStatus', {
              pipeline: targetPipeline,
              hasError: jobStatus.hasError,
              isRunning: !jobStatus.isComplete,
              startedAt: jobStatus.startedAt,
              endedAt: jobStatus.endedAt,
              hasEverSucceeded: jobStatus.hasEverSucceeded
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
    const pollersUponQueued = getters.getRunningPipelines.map(pipeline => {
      const jobId = pipeline.name
      const isMissingPoller =
        state.pipelinePollers.find(
          pipelinePoller => pipelinePoller.getMetadata().jobId === jobId
        ) === undefined

      if (isMissingPoller) {
        return dispatch('queuePipelinePoller', { jobId })
      }
    })

    return Promise.all(pollersUponQueued)
  },

  resetExtractorInFocusConfiguration: ({ commit }) =>
    commit('reset', 'extractorInFocusConfiguration'),

  resetLoaderInFocusConfiguration: ({ commit }) =>
    commit('reset', 'loaderInFocusConfiguration'),

  run({ commit, dispatch }, pipeline) {
    commit('setPipelineStatus', {
      pipeline,
      isRunning: true,
      hasEverSucceeded: pipeline.hasEverSucceeded
    })

    return orchestrationsApi.run(pipeline).then(response => {
      dispatch('queuePipelinePoller', response.data)
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
    return orchestrationsApi.savePluginConfiguration(configPayload)
  },

  testPluginConfiguration(_, configPayload) {
    return orchestrationsApi.testPluginConfiguration(configPayload)
  },

  updateRecentELTSelections({ commit }, updatePayload) {
    commit('setELTRecentSelection', updatePayload)
  },

  uploadPluginConfigurationFile(_, configPayload) {
    return orchestrationsApi.uploadPluginConfigurationFile(configPayload)
  }
}

const mutations = {
  addPipelinePoller(state, pipelinePoller) {
    state.pipelinePollers.push(pipelinePoller)
  },

  deletePipeline(state, pipeline) {
    const idx = state.pipelines.indexOf(pipeline)
    state.pipelines.splice(idx, 1)
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

  setELTRecentSelection(state, { type, value }) {
    state.recentELTSelections[type] = value
  },

  setInFocusConfiguration(state, { configuration, target }) {
    configuration.settings.forEach(setting => {
      const isIso8601Date = setting.kind && setting.kind === 'date_iso8601'
      configuration.profiles.forEach(profile => {
        const isDefaultNeeded =
          profile.config.hasOwnProperty(setting.name) &&
          profile.config[setting.name] === null
        if (isIso8601Date && isDefaultNeeded) {
          profile.config[setting.name] = utils.getFirstOfMonthAsIso8601()
        }
      })
    })
    state[target] = configuration
  },

  setPipelineStatus(
    _,
    {
      pipeline,
      isRunning,
      isDeleting = false,
      hasError = false,
      hasEverSucceeded = false,
      startedAt = null,
      endedAt = null
    }
  ) {
    Vue.set(pipeline, 'isRunning', isRunning)
    Vue.set(pipeline, 'hasError', hasError)
    Vue.set(pipeline, 'isDeleting', isDeleting)
    Vue.set(pipeline, 'hasEverSucceeded', hasEverSucceeded)
    Vue.set(pipeline, 'startedAt', utils.dateIso8601(startedAt))
    Vue.set(pipeline, 'endedAt', utils.dateIso8601(endedAt))
  },

  setPipelineJobId(_, { pipeline, jobId }) {
    Vue.set(pipeline, 'jobId', jobId)
  },

  setPipelines(state, pipelines) {
    pipelines.forEach(pipeline => {
      pipeline.startDate = utils.dateIso8601(pipeline.startDate)
      if (pipeline.startedAt) {
        pipeline.startedAt = utils.dateIso8601(pipeline.startedAt)
      }
      if (pipeline.endedAt) {
        pipeline.endedAt = utils.dateIso8601(pipeline.endedAt)
      }
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
