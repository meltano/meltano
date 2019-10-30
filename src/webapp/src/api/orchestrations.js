import axios from 'axios'
import utils from '@/utils/utils'

export default {
  extract(extractor) {
    return axios.post(utils.apiUrl('orchestrations', `extract/${extractor}`))
  },

  run(eltPayload) {
    return axios.post(utils.apiUrl('orchestrations', 'run'), eltPayload)
  },

  getExtractorInFocusEntities(extractor) {
    return axios.post(utils.apiUrl('orchestrations', `entities/${extractor}`))
  },

  selectEntities(extractorEntities) {
    return axios.post(
      utils.apiUrl('orchestrations', 'select-entities'),
      extractorEntities
    )
  },

  getJobLog({ jobId }) {
    return axios.get(utils.apiUrl('orchestrations', `jobs/${jobId}/log`))
  },

  getPolledPipelineJobStatus(pollPayload) {
    return axios.post(utils.apiUrl('orchestrations', 'jobs/state'), pollPayload)
  },

  getAllPipelineSchedules() {
    return axios.get(utils.apiUrl('orchestrations', 'pipeline_schedules'))
  },

  savePipelineSchedule(schedulePayload) {
    return axios.post(
      utils.apiUrl('orchestrations', 'pipeline_schedules'),
      schedulePayload
    )
  },

  getPluginConfiguration({ type, name }) {
    return axios.get(
      utils.apiUrl('orchestrations', `${type}/${name}/configuration`)
    )
  },

  savePluginConfiguration({ type, name, config }) {
    return axios.put(
      utils.apiUrl('orchestrations', `${type}/${name}/configuration`),
      config
    )
  }
}
