import Vue from 'vue'

import lodash from 'lodash'

import orchestrationsApi from '@/api/orchestrations'
import poller from '@/utils/poller'
import utils from '@/utils/utils'

const defaultState = utils.deepFreeze({
  extractorInFocusConfiguration: {},
  loaderInFocusConfiguration: {},
  pipelinePollers: [],
  pipelines: []
})

const getters = {
  getHasPipelines(state) {
    return state.pipelines.length > 0
  },

  getHasPipelineWithExtractor(_, getters) {
    return extractorName => {
      return Boolean(getters.getPipelineWithExtractor(extractorName))
    }
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

  getPipelineWithExtractor(state) {
    return extractor => {
      return state.pipelines.find(pipeline => pipeline.extractor === extractor)
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

  getSortedPipelines(state) {
    return [...state.pipelines].sort((p1, p2) => {
      return p1.extractor > p2.extractor ? 1 : -1
    })
  },

  getSuccessfulPipelines(state) {
    return state.pipelines.filter(pipeline => pipeline.hasEverSucceeded)
  },

  lastUpdatedDate(_, getters) {
    return extractor => {
      const pipelineExtractor = getters.getPipelineWithExtractor(extractor)

      return pipelineExtractor
        ? utils.formatDateStringYYYYMMDD(pipelineExtractor.endedAt)
        : ''
    }
  },

  startDate(_, getters) {
    return extractor => {
      const pipelineExtractor = getters.getPipelineWithExtractor(extractor)

      return pipelineExtractor
        ? utils.formatDateStringYYYYMMDD(pipelineExtractor.startDate)
        : ''
    }
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
      ...pipeline,
      isRunning: pipeline.isRunning,
      isDeleting: true
    }
    commit('setPipelineStatus', status)
    return orchestrationsApi.deletePipelineSchedule(pipeline).then(() => {
      commit('deletePipeline', pipeline)
    })
  },

  getAllPipelineSchedules({ commit, dispatch }) {
    return orchestrationsApi.getAllPipelineSchedules().then(response => {
      commit('setPipelines', response.data)
      dispatch('rehydratePollers')
    })
  },

  getExtractorConfiguration({ commit, dispatch, state }, extractor) {
    return dispatch('getPluginConfiguration', {
      name: extractor,
      type: 'extractors'
    }).then(response => {
      commit('setInFocusConfiguration', {
        configuration: response.data,
        target: 'extractorInFocusConfiguration'
      })
      return state.extractorInFocusConfiguration
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
              ...targetPipeline,
              hasError: jobStatus.hasError,
              hasEverSucceeded: jobStatus.hasEverSucceeded,
              isRunning: !jobStatus.isComplete,
              startedAt: jobStatus.startedAt,
              endedAt: jobStatus.endedAt
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
      ...pipeline,
      isRunning: true,
      hasEverSucceeded: pipeline.hasEverSucceeded
    })

    return orchestrationsApi.run(pipeline).then(response => {
      dispatch('queuePipelinePoller', response.data)
      commit('setPipelineJobId', { pipeline, jobId: response.data.jobId })
    })
  },

  savePipelineSchedule({ commit }, extractor) {
    let pipeline = {
      name: `pipeline-${new Date().getTime()}`,
      extractor,
      loader: 'target-postgres', // Refactor vs. hard code when we again want to display in the UI
      transform: 'run', // Refactor vs. hard code when we again want to display in the UI
      interval: '@once', // Refactor vs. hard code when we again want to display in the UI
      isRunning: false
    }
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

  updatePipelineSchedule({ commit }, payload) {
    commit('setPipelineStatus', {
      pipeline: payload.pipeline,
      ...payload.pipeline,
      isSaving: true
    })
    return orchestrationsApi.updatePipelineSchedule(payload).then(response => {
      const updatedPipeline = Object.assign({}, payload.pipeline, response.data)
      commit('setPipelineStatus', {
        pipeline: updatedPipeline,
        ...updatedPipeline,
        isSaving: false
      })
      commit('setPipeline', updatedPipeline)
    })
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

  setPipeline(state, pipeline) {
    const target = state.pipelines.find(p => p.name === pipeline.name)
    const idx = state.pipelines.indexOf(target)
    state.pipelines.splice(idx, 1, pipeline)
  },

  setPipelineStatus(
    _,
    {
      pipeline,
      hasError,
      hasEverSucceeded,
      isDeleting,
      isRunning,
      isSaving,
      startedAt = null,
      endedAt = null
    }
  ) {
    Vue.set(pipeline, 'hasError', hasError || false)
    Vue.set(pipeline, 'hasEverSucceeded', hasEverSucceeded || false)
    Vue.set(pipeline, 'isDeleting', isDeleting || false)
    Vue.set(pipeline, 'isRunning', isRunning || false)
    Vue.set(pipeline, 'isSaving', isSaving || false)
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
