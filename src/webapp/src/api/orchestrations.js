import axios from 'axios'
import utils from '@/utils/utils'

export default {
  addConfigurationProfile({ type, name, profile }) {
    return axios.post(
      utils.apiUrl('orchestrations', `${type}/${name}/configuration/profiles`),
      profile
    )
  },

  createSubscription(subscriptionPayload) {
    return axios.post(
      utils.apiUrl('orchestrations', 'subscriptions'),
      subscriptionPayload
    )
  },

  deletePipelineSchedule(schedulePayload) {
    return axios.delete(utils.apiUrl('orchestrations', 'pipeline-schedules'), {
      data: schedulePayload
    })
  },

  deleteSubscription(id) {
    return axios.delete(utils.apiUrl('orchestrations', `subscriptions/${id}`))
  },

  downloadJobLog({ jobId }) {
    return axios.get(utils.apiUrl('orchestrations', `jobs/${jobId}/download`))
  },

  extract(extractor) {
    return axios.post(utils.apiUrl('orchestrations', `extract/${extractor}`))
  },

  getJobLog({ jobId }) {
    return axios.get(utils.apiUrl('orchestrations', `jobs/${jobId}/log`))
  },

  getPipelineSchedules() {
    return axios.get(utils.apiUrl('orchestrations', 'pipeline-schedules'))
  },

  getPluginConfiguration({ type, name }) {
    return axios.get(
      utils.apiUrl('orchestrations', `${type}/${name}/configuration`)
    )
  },

  getPolledPipelineJobStatus(pollPayload) {
    return axios.post(utils.apiUrl('orchestrations', 'jobs/state'), pollPayload)
  },

  getSubscriptions() {
    return axios.get(utils.apiUrl('orchestrations', 'subscriptions'))
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
