import Vue from 'vue'

import lodash from 'lodash'

import poller from '@/utils/poller'
import utils from '@/utils/utils'

import orchestrationsApi from '../../api/orchestrations'

const defaultState = utils.deepFreeze({
  connectionInFocusConfiguration: {},
  extractorInFocusConfiguration: {},
  extractorInFocusEntities: {},
  hasExtractorLoadingError: false,
  loaderInFocusConfiguration: {},
  pipelinePollers: [],
  pipelines: []
})

const getters = {
  getHasPipelines(state) {
    return state.pipelines.length > 0
  },

  // eslint-disable-next-line
  getHasValidConfigSettings(_, getters) {
    return configSettings => {
      const isValid = setting =>
        getters.getIsConfigSettingValid(configSettings.config[setting.name])
      return (
        configSettings.settings &&
        lodash.every(configSettings.settings, isValid)
      )
    }
  },

  getIsConfigSettingValid() {
    return value => value !== null && value !== undefined && value !== ''
  },

  getRunningPipelineJobsCount(state) {
    return state.pipelinePollers.length
  },

  getRunningPipelineJobIds(state) {
    return state.pipelinePollers.map(
      pipelinePoller => pipelinePoller.getMetadata().jobId
    )
  }
}

const actions = {
  clearConnectionInFocusConfiguration: ({ commit }) =>
    commit('reset', 'connectionInFocusConfiguration'),

  clearExtractorInFocusConfiguration: ({ commit }) =>
    commit('reset', 'extractorInFocusConfiguration'),

  clearExtractorInFocusEntities: ({ commit }) =>
    commit('reset', 'extractorInFocusEntities'),

  clearLoaderInFocusConfiguration: ({ commit }) =>
    commit('reset', 'loaderInFocusConfiguration'),

  getAllPipelineSchedules({ commit, dispatch }) {
    orchestrationsApi.getAllPipelineSchedules().then(response => {
      commit('setPipelines', response.data)
      dispatch('rehydratePollers')
    })
  },

  // eslint-disable-next-line no-shadow
  getConnectionConfiguration({ commit, dispatch }, connection) {
    dispatch('getPluginConfiguration', {
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
    commit('setHasExtractorLoadingError', false)

    return orchestrationsApi
      .getExtractorInFocusEntities(extractorName)
      .then(response => {
        commit('setAllExtractorInFocusEntities', response.data)
      })
      .catch(() => {
        commit('setHasExtractorLoadingError', true)
      })
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

  // eslint-disable-next-line no-shadow
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
              pipeline => pipeline.name === jobStatus.jobId.replace('job_', '')
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

  rehydratePollers({ dispatch, state }) {
    // Handle page refresh condition resulting in jobs running but no pollers
    const runningPipelines = state.pipelines.filter(
      pipeline => pipeline.isRunning
    )
    runningPipelines.forEach(pipeline => {
      const jobId = `job_${pipeline.name}`
      const isMissingPoller =
        state.pipelinePollers.find(
          pipelinePoller => pipelinePoller.getMetadata().jobId === jobId
        ) === undefined
      if (isMissingPoller) {
        dispatch('queuePipelinePoller', { jobId })
      }
    })
  },

  run({ commit, dispatch }, pipeline) {
    return orchestrationsApi.run(pipeline).then(response => {
      dispatch('queuePipelinePoller', response.data)
      commit('setPipelineIsRunning', { pipeline, value: true })
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

  setHasExtractorLoadingError(state, value) {
    state.hasExtractorLoadingError = value
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

  setPipelines(state, pipelines) {
    pipelines.forEach(pipeline => {
      pipeline.startDate = utils.getDateStringAsIso8601OrNull(
        pipeline.startDate
      )
    })
    state.pipelines = pipelines
  },

  toggleSelected(state, selectable) {
    Vue.set(selectable, 'selected', !selectable.selected)
  },

  updatePipelines(state, pipeline) {
    pipeline.startDate = utils.getDateStringAsIso8601OrNull(pipeline.startDate)
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
