import axios from 'axios'
import utils from '@/utils/utils'

export default {
  addConfigurationProfile({ type, name, profile }) {
    return axios.put(
      utils.apiUrl('orchestrations', `${type}/${name}/configuration/profile`),
      profile
    )
  },

  extract(extractor) {
    return axios.post(utils.apiUrl('orchestrations', `extract/${extractor}`))
  },

  getAllPipelineSchedules() {
    return axios.get(utils.apiUrl('orchestrations', 'pipeline_schedules'))
  },

  getExtractorInFocusEntities(extractor) {
    return axios.post(utils.apiUrl('orchestrations', `entities/${extractor}`))
  },

  getJobLog({ jobId }) {
    return axios.get(utils.apiUrl('orchestrations', `jobs/${jobId}/log`))
  },

  getPluginConfiguration({ type, name }) {
    return axios.get(
      utils.apiUrl('orchestrations', `${type}/${name}/configuration`)
    )
  },

  getPolledPipelineJobStatus(pollPayload) {
    return axios.post(utils.apiUrl('orchestrations', 'jobs/state'), pollPayload)
  },

  run(eltPayload) {
    return axios.post(utils.apiUrl('orchestrations', 'run'), eltPayload)
  },

  savePipelineSchedule(schedulePayload) {
    return axios.post(
      utils.apiUrl('orchestrations', 'pipeline_schedules'),
      schedulePayload
    )
  },

  savePluginConfiguration({ type, name, config }) {
    return axios.put(
      utils.apiUrl('orchestrations', `${type}/${name}/configuration`),
      config
    )
  },

  selectEntities(extractorEntities) {
    return axios.post(
      utils.apiUrl('orchestrations', 'select-entities'),
      extractorEntities
    )
  }
}
