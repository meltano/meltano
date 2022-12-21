import axios from 'axios'
import utils from '@/utils/utils'

export default {
  createSubscription(subscriptionPayload) {
    return axios.post(
      utils.apiUrl('orchestrations', 'subscriptions'),
      subscriptionPayload
    )
  },

  deletePipelineSchedule(schedulePayload) {
    return axios.delete(utils.apiUrl('orchestrations', 'pipeline-schedules'), {
      data: schedulePayload,
    })
  },

  deleteSubscription(id) {
    return axios.delete(utils.apiUrl('orchestrations', `subscriptions/${id}`))
  },

  downloadJobLog({ stateId }) {
    return axios.get(utils.apiUrl('orchestrations', `jobs/${stateId}/download`))
  },

  extract(extractor) {
    return axios.post(utils.apiUrl('orchestrations', `extract/${extractor}`))
  },

  getJobLog({ stateId }) {
    return axios.get(utils.apiUrl('orchestrations', `jobs/${stateId}/log`))
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

  savePluginConfiguration({ type, name, payload }) {
    return axios.put(
      utils.apiUrl('orchestrations', `${type}/${name}/configuration`),
      payload
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

  uploadPluginConfigurationFile({ type, name, payload }) {
    const formData = new FormData()
    for (let key in payload) {
      const value = payload[key]
      formData.append(key, value)
    }

    return axios.post(
      utils.apiUrl(
        'orchestrations',
        `${type}/${name}/configuration/upload-file`
      ),
      formData,
      {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      }
    )
  },

  deleteUploadedPluginConfigurationFile({ type, name, payload }) {
    return axios.post(
      utils.apiUrl(
        'orchestrations',
        `${type}/${name}/configuration/delete-uploaded-file`
      ),
      payload
    )
  },
}
