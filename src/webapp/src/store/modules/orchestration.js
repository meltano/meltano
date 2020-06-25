import Vue from 'vue'

import lodash from 'lodash'

import orchestrationsApi from '@/api/orchestrations'
import poller from '@/utils/poller'
import utils from '@/utils/utils'

const defaultState = utils.deepFreeze({
  extractorInFocusConfiguration: {},
  loaderInFocusConfiguration: {},
  pipelinePollers: [],
  pipelines: [],
  intervalOptions: {
    '@once': 'Once (Manual)',
    '@hourly': 'Hourly',
    '@daily': 'Daily',
    '@weekly': 'Weekly',
    '@monthly': 'Monthly',
    '@yearly': 'Yearly'
  }
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
    return lodash.orderBy(state.pipelines, 'extractor')
  },

  getSuccessfulPipelines(state) {
    return state.pipelines.filter(pipeline => pipeline.hasEverSucceeded)
  },

  lastUpdatedDate(_, getters) {
    return extractor => {
      const pipelineExtractor = getters.getPipelineWithExtractor(extractor)

      if (!pipelineExtractor) {
        return ''
      }

      return pipelineExtractor.endedAt
        ? utils.formatDateStringYYYYMMDD(pipelineExtractor.endedAt)
        : pipelineExtractor.isRunning
          ? 'Updating...'
          : ''
    }
  },

  startDate(_, getters) {
    return extractor => {
      const pipelineExtractor = getters.getPipelineWithExtractor(extractor)

      return pipelineExtractor ? pipelineExtractor.startDate : ''
    }
  }
}

const actions = {
  addConfigurationProfile(_, profile) {
    return orchestrationsApi.addConfigurationProfile(profile).catch(error => {
      Vue.toasted.global.error(error)
    })
  },

  createSubscription(_, subscription) {
    return orchestrationsApi.createSubscription(subscription)
  },

  deletePipelineSchedule({ commit }, pipeline) {
    let status = {
      pipeline,
      ...pipeline,
      isDeleting: true
    }
    commit('setPipelineStatus', status)
    return orchestrationsApi.deletePipelineSchedule(pipeline).then(() => {
      commit('deletePipeline', pipeline)
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

  getPipelineSchedules({ commit, dispatch }) {
    return orchestrationsApi.getPipelineSchedules().then(response => {
      commit('setPipelines', response.data)
      dispatch('rehydratePollers')
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
          const targetPoller = state.pipelinePollers.find(
            pipelinePoller =>
              pipelinePoller.getMetadata().jobId === jobStatus.jobId
          )
          if (jobStatus.isComplete) {
            commit('removePipelinePoller', targetPoller)
          }

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
      isRunning: true
    })

    return orchestrationsApi.run(pipeline).then(response => {
      dispatch('queuePipelinePoller', response.data)
      const pipelineWithJobId = Object.assign(pipeline, {
        jobId: response.data.jobId
      })
      commit('setPipeline', pipelineWithJobId)
    })
  },

  savePipelineSchedule({ commit }, { hasDefaultTransforms, extractorName, pipeline }) {
    let newPipeline = {}
    if (!pipeline) {
      Object.assign(newPipeline, {
        name: `pipeline-${new Date().getTime()}`,
        extractor: extractorName,
        loader: 'target-postgres', // Refactor vs. hard code when we again want to display in the UI
        transform: hasDefaultTransforms ? 'run' : 'skip',
        interval: '@daily', // Refactor vs. hard code when we again want to display in the UI
        isRunning: false
      })
    } else {
      Object.assign(newPipeline, pipeline)
    }
    return orchestrationsApi.savePipelineSchedule(newPipeline).then(response => {
      newPipeline = Object.assign(newPipeline, response.data)
      commit('updatePipelines', newPipeline)
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

  uploadPluginConfigurationFile(_, payload) {
    return orchestrationsApi.uploadPluginConfigurationFile(payload)
  },

  deleteUploadedPluginConfigurationFile(_, payload) {
    return orchestrationsApi.deleteUploadedPluginConfigurationFile(payload)
  }
}

const mutations = {
  addPipelinePoller(state, pipelinePoller) {
    state.pipelinePollers.push(pipelinePoller)
  },

  deletePipeline(state, pipeline) {
    const idx = state.pipelines.indexOf(pipeline)
    Vue.delete(state.pipelines, idx)
  },

  removePipelinePoller(state, pipelinePoller) {
    pipelinePoller.dispose()
    const idx = state.pipelinePollers.indexOf(pipelinePoller)
    Vue.delete(state.pipelinePollers, idx)
  },

  reset(state, attr) {
    if (defaultState.hasOwnProperty(attr)) {
      state[attr] = lodash.cloneDeep(defaultState[attr])
    }
  },

  setInFocusConfiguration(state, { configuration, target }) {
    const requiredSettingsKeys = utils.requiredConnectorSettingsKeys(
      configuration.settings,
      configuration.settingsGroupValidation
    )
    configuration.settings.forEach(setting => {
      const isIso8601Date = setting.kind && setting.kind === 'date_iso8601'
      configuration.profiles.forEach(profile => {
        const isDefaultNeeded =
          profile.config.hasOwnProperty(setting.name) &&
          profile.config[setting.name] === null &&
          requiredSettingsKeys.includes(setting.name)
        if (isIso8601Date && isDefaultNeeded) {
          profile.config[setting.name] = utils.getFirstOfMonthAsYYYYMMDD()
        }
      })
    })
    state[target] = configuration
  },

  setPipeline(state, pipeline) {
    const target = state.pipelines.find(p => p.name === pipeline.name)
    const idx = state.pipelines.indexOf(target)
    Vue.set(state.pipelines, idx, pipeline)
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
    Vue.set(pipeline, 'startedAt', utils.dateIso8601Nullable(startedAt))
    Vue.set(pipeline, 'endedAt', utils.dateIso8601Nullable(endedAt))
  },

  setPipelines(state, pipelines) {
    pipelines.forEach(pipeline => {
      if (pipeline.startedAt) {
        pipeline.startedAt = utils.dateIso8601Nullable(pipeline.startedAt)
      }
      if (pipeline.endedAt) {
        pipeline.endedAt = utils.dateIso8601Nullable(pipeline.endedAt)
      }
    })
    state.pipelines = pipelines
  },

  toggleSelected(state, selectable) {
    Vue.set(selectable, 'selected', !selectable.selected)
  },

  updatePipelines(state, pipeline) {
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
