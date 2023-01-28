import Vue from 'vue'

import lodash from 'lodash'

import orchestrationsApi from '@/api/orchestrations'
import poller from '@/utils/poller'
import utils from '@/utils/utils'

const defaultState = utils.deepFreeze({
  pluginInFocusConfiguration: {},
  pipelinePollers: [],
  pipelines: [],
})

const getters = {
  getHasPipelines(state) {
    return state.pipelines.length > 0
  },

  getHasPipelineWithPlugin(_, getters) {
    return (pluginType, pluginName) =>
      Boolean(getters.getPipelineWithPlugin(pluginType, pluginName))
  },

  getHasValidConfigSettings(_, getters) {
    return (configSettings, settingsGroupValidation = null) => {
      return settingsGroupValidation && settingsGroupValidation.length
        ? getters.getHasGroupValidationConfigSettings(
            configSettings,
            settingsGroupValidation
          )
        : getters.getHasDefaultValidationConfigSettings(configSettings)
    }
  },

  getHasDefaultValidationConfigSettings() {
    return (configSettings) => {
      const isKindBoolean = (setting) =>
        setting.kind && setting.kind === 'boolean'
      const isValid = (setting) =>
        isKindBoolean(setting) || Boolean(configSettings.config[setting.name])
      return (
        configSettings.settings &&
        lodash.every(configSettings.settings, isValid)
      )
    }
  },

  getHasGroupValidationConfigSettings() {
    return (configSettings, settingsGroupValidation) => {
      const matchGroup = settingsGroupValidation.find((group) => {
        if (configSettings.settings) {
          const groupedSettings = configSettings.settings.filter((setting) =>
            group.includes(setting.name)
          )
          const isValid = (setting) =>
            Boolean(configSettings.config[setting.name])
          return lodash.every(groupedSettings, isValid)
        }
      })
      return configSettings.settings && Boolean(matchGroup)
    }
  },

  getPipelineWithPlugin(state) {
    return (pluginType, pluginName) =>
      state.pipelines.find((pipeline) => pipeline[pluginType] === pluginName)
  },

  getPipelinesWithPlugin(state) {
    return (pluginType, pluginName) =>
      state.pipelines.filter((pipeline) => pipeline[pluginType] === pluginName)
  },

  getRunningPipelines(state) {
    return state.pipelines.filter((pipeline) => pipeline.isRunning)
  },

  getRunningPipelinestateIds(state) {
    return state.pipelinePollers.map(
      (pipelinePoller) => pipelinePoller.getMetadata().stateId
    )
  },

  getSortedPipelines(state) {
    return lodash.orderBy(state.pipelines, 'extractor')
  },

  getSuccessfulPipelines(state) {
    return state.pipelines.filter((pipeline) => pipeline.hasEverSucceeded)
  },

  lastUpdatedDate(_, getters) {
    return (extractor) => {
      const pipelineExtractor = getters.getPipelineWithPlugin(
        'extractor',
        extractor
      )

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
    return (extractor) => {
      const pipelineExtractor = getters.getPipelineWithPlugin(
        'extractor',
        extractor
      )

      return pipelineExtractor ? pipelineExtractor.startDate : ''
    }
  },
}

const actions = {
  createSubscription(_, subscription) {
    return orchestrationsApi.createSubscription(subscription)
  },

  deletePipelineSchedule({ commit }, pipeline) {
    let status = {
      pipeline,
      ...pipeline,
      isDeleting: true,
    }
    commit('setPipelineStatus', status)
    return orchestrationsApi.deletePipelineSchedule(pipeline).then(() => {
      commit('deletePipeline', pipeline)
    })
  },

  getJobLog(_, stateId) {
    return orchestrationsApi.getJobLog({ stateId })
  },

  getLoaderConfiguration({ commit, dispatch }, loader) {
    return dispatch('getPluginConfiguration', {
      name: loader,
      type: 'loaders',
    }).then((response) => {
      commit('setInFocusConfiguration', {
        configuration: response.data,
        target: 'loaderInFocusConfiguration',
      })
    })
  },

  getPipelineSchedules({ commit, dispatch }) {
    return orchestrationsApi.getPipelineSchedules().then((response) => {
      commit('setPipelines', response.data)
      dispatch('rehydratePollers')
    })
  },

  getPluginConfiguration(_, pluginPayload) {
    return orchestrationsApi.getPluginConfiguration(pluginPayload)
  },

  getAndFocusOnPluginConfiguration({ commit, dispatch, state }, payload) {
    return dispatch('getPluginConfiguration', payload).then((response) => {
      commit('setInFocusConfiguration', {
        configuration: response.data,
        target: 'pluginInFocusConfiguration',
      })
      return state.pluginInFocusConfiguration
    })
  },

  getPolledPipelineJobStatus({ commit, getters, state }) {
    return orchestrationsApi
      .getPolledPipelineJobStatus({
        stateIds: getters.getRunningPipelinestateIds,
      })
      .then((response) => {
        response.data.jobs.forEach((jobStatus) => {
          const targetPoller = state.pipelinePollers.find(
            (pipelinePoller) =>
              pipelinePoller.getMetadata().stateId === jobStatus.stateId
          )
          if (jobStatus.isComplete) {
            commit('removePipelinePoller', targetPoller)
          }

          const targetPipeline = state.pipelines.find(
            (pipeline) => pipeline.name === jobStatus.stateId
          )

          commit('setPipelineStatus', {
            pipeline: targetPipeline,
            ...targetPipeline,
            hasError: jobStatus.hasError,
            hasEverSucceeded: jobStatus.hasEverSucceeded,
            isRunning: !jobStatus.isComplete,
            startedAt: jobStatus.startedAt,
            endedAt: jobStatus.endedAt,
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
    const pollersUponQueued = getters.getRunningPipelines.map((pipeline) => {
      const stateId = pipeline.name
      const isMissingPoller =
        state.pipelinePollers.find(
          (pipelinePoller) => pipelinePoller.getMetadata().stateId === stateId
        ) === undefined

      if (isMissingPoller) {
        return dispatch('queuePipelinePoller', { stateId })
      }
    })

    return Promise.all(pollersUponQueued)
  },

  resetPluginInFocusConfiguration: ({ commit }) =>
    commit('reset', 'pluginInFocusConfiguration'),

  run({ commit, dispatch }, pipeline) {
    commit('setPipelineStatus', {
      pipeline,
      ...pipeline,
      isRunning: true,
    })

    return orchestrationsApi.run({ name: pipeline.name }).then((response) => {
      dispatch('queuePipelinePoller', response.data)
    })
  },

  savePipelineSchedule({ commit }, { pipeline }) {
    return orchestrationsApi.savePipelineSchedule(pipeline).then((response) => {
      const newPipeline = Object.assign(pipeline, response.data)
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
      isSaving: true,
    })
    return orchestrationsApi
      .updatePipelineSchedule(payload)
      .then((response) => {
        const editableItems = {
          interval: response.data.interval,
          transform: response.data.transform,
        }
        const updatedPipeline = Object.assign(
          {},
          payload.pipeline,
          editableItems
        )
        commit('setPipelineStatus', {
          pipeline: updatedPipeline,
          ...updatedPipeline,
          isSaving: false,
        })
        commit('setPipeline', updatedPipeline)
      })
  },

  uploadPluginConfigurationFile(_, payload) {
    return orchestrationsApi.uploadPluginConfigurationFile(payload)
  },

  deleteUploadedPluginConfigurationFile(_, payload) {
    return orchestrationsApi.deleteUploadedPluginConfigurationFile(payload)
  },
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
    configuration.settings.forEach((setting) => {
      const isIso8601Date = setting.kind && setting.kind === 'date_iso8601'
      const isDefaultNeeded =
        configuration.config.hasOwnProperty(setting.name) &&
        configuration.config[setting.name] === null &&
        requiredSettingsKeys.includes(setting.name)
      if (isIso8601Date && isDefaultNeeded) {
        configuration.config[setting.name] = utils.getFirstOfMonthAsYYYYMMDD()
      }
    })
    state[target] = configuration
  },

  setPipeline(state, pipeline) {
    const target = state.pipelines.find((p) => p.name === pipeline.name)
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
      endedAt = null,
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
    pipelines.forEach((pipeline) => {
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
  },
}

export default {
  namespaced: true,
  state: lodash.cloneDeep(defaultState),
  getters,
  actions,
  mutations,
}
