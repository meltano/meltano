import axios from 'axios'
import utils from '@/utils/utils'

export default {
  extract(extractor) {
    return axios.post(utils.apiUrl('orchestrations', `extract/${extractor}`))
  },

  getAllPipelineSchedules() {
    return axios.get(utils.apiUrl('orchestrations', 'pipeline_schedules'))
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

  testPluginConfiguration({ type, name, config }) {
    return axios.get(
      utils.apiUrl('orchestrations', `${type}/${name}/configuration/test`),
      config
    )
  }
}
