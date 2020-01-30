import axios from 'axios'
import utils from '@/utils/utils'

export default {
  addConfigurationProfile({ type, name, profile }) {
    return axios.post(
      utils.apiUrl('orchestrations', `${type}/${name}/configuration/profiles`),
      profile
    )
  },

  deletePipelineSchedule(schedulePayload) {
    return axios.delete(utils.apiUrl('orchestrations', 'pipeline-schedules'), {
      data: schedulePayload
    })
  },

  extract(extractor) {
    return axios.post(utils.apiUrl('orchestrations', `extract/${extractor}`))
  },

  getAllPipelineSchedules() {
    return axios.get(utils.apiUrl('orchestrations', 'pipeline-schedules'))
  },

  getJobLog({ jobId }) {
    return axios.get(utils.apiUrl('orchestrations', `jobs/${jobId}/log`))
  },

  downloadJobLog({ jobId }) {
    return axios.get(utils.apiUrl('orchestrations', `jobs/${jobId}/download`))
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
      utils.apiUrl('orchestrations', 'pipeline-schedules'),
      schedulePayload
    )
  },

  savePluginConfiguration({ type, name, profiles }) {
    return axios.put(
      utils.apiUrl('orchestrations', `${type}/${name}/configuration`),
      profiles
    )
  },

  testPluginConfiguration({ type, name, payload }) {
    return axios.post(
      utils.apiUrl('orchestrations', `${type}/${name}/configuration/test`),
      payload
    )
  },

  updatePipelineSchedule(schedulePayload) {
    return axios.put(
      utils.apiUrl('orchestrations', 'pipeline-schedules'),
      schedulePayload
    )
  },

  uploadPluginConfigurationFile({ type, name, profileName, formData }) {
    return axios.post(
      utils.apiUrl(
        'orchestrations',
        `${type}/${name}@${profileName}/configuration/upload-file`
      ),
      formData,
      {
        headers: {
          'Content-Type': 'multipart/form-data'
        }
      }
    )
  }
}
