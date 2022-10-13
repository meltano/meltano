import axios from 'axios'
import utils from '@/utils/utils'

export default {
  addRolePermission(role, permissionType, context) {
    const payload = { permissionType, role, context }
    return axios.post(
      utils.apiUrl('settings', 'acl/roles/permissions'),
      payload
    )
  },

  createRole(role, user) {
    const payload = { role, user }
    return axios.post(utils.apiUrl('settings', 'acl/roles'), payload)
  },

  deleteConnection(connection) {
    return axios.post(utils.apiUrl('settings', 'delete'), connection)
  },

  deleteRole(role, user) {
    const payload = { role, user }

    return axios.delete(utils.apiUrl('settings', 'acl/roles'), {
      data: payload,
    })
  },

  fetchACL() {
    return axios.get(utils.apiUrl('settings', 'acl'))
  },

  index() {
    return axios.get(utils.apiUrl('settings'))
  },

  removeRolePermission(role, permissionType, context) {
    const payload = { permissionType, role, context }

    return axios.delete(utils.apiUrl('settings', 'acl/roles/permissions'), {
      data: payload,
    })
  },

  saveConnection(connection) {
    return axios.post(utils.apiUrl('settings', 'save'), connection)
  },
}
