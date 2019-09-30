import axios from 'axios'
import utils from '@/utils/utils'

export default {
  extract(extractor) {
    return axios.post(utils.apiUrl('orchestrations', `extract/${extractor}`))
  },

  getAllPipelineSchedules() {
    return axios.get(utils.apiUrl('orchestrations', 'get/pipeline_schedules'))
  },

  getExtractorInFocusEntities(extractor) {
    return axios.post(utils.apiUrl('orchestrations', `entities/${extractor}`))
  },

  getJobLog(jobId) {
    return axios.post(utils.apiUrl('orchestrations', 'job/log'), jobId)
  },

  getPluginConfiguration(pluginPayload) {
    return axios.post(
      utils.apiUrl('orchestrations', 'get/configuration'),
      pluginPayload
    )
  },

  getPolledPipelineJobStatus(pollPayload) {
    return axios.post(utils.apiUrl('orchestrations', 'job/state'), pollPayload)
  },

  run(eltPayload) {
    return axios.post(utils.apiUrl('orchestrations', 'run'), eltPayload)
  },

  savePipelineSchedule(schedulePayload) {
    return axios.post(
      utils.apiUrl('orchestrations', 'save/pipeline_schedule'),
      schedulePayload
    )
  },

  savePluginConfiguration(configPayload) {
    return axios.post(
      utils.apiUrl('orchestrations', 'save/configuration'),
      configPayload
    )
  },

  selectEntities(extractorEntities) {
    return axios.post(
      utils.apiUrl('orchestrations', 'select-entities'),
      extractorEntities
    )
  }
}
