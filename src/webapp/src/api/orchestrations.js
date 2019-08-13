import axios from 'axios'
import utils from '@/utils/utils'

export default {
  extract(extractor) {
    return axios.post(utils.apiUrl('orchestrations', `extract/${extractor}`))
  },

  getPluginConfiguration(pluginPayload) {
    return axios.post(
      utils.apiUrl('orchestrations', 'get/configuration'),
      pluginPayload
    )
  },

  savePluginConfiguration(configPayload) {
    return axios.post(
      utils.apiUrl('orchestrations', 'save/configuration'),
      configPayload
    )
  },

  getAllPipelineSchedules() {
    return axios.get(utils.apiUrl('orchestrations', 'get/pipeline_schedules'))
  },

  savePipelineSchedule(schedulePayload) {
    return axios.post(
      utils.apiUrl('orchestrations', 'save/pipeline_schedule'),
      schedulePayload
    )
  },

  selectEntities(extractorEntities) {
    return axios.post(
      utils.apiUrl('orchestrations', 'select-entities'),
      extractorEntities
    )
  },

  getExtractorInFocusEntities(extractor) {
    return axios.post(utils.apiUrl('orchestrations', `entities/${extractor}`))
  },

  connectionNames() {
    return axios.get(utils.apiUrl('orchestrations', 'connection_names'))
  }
}
