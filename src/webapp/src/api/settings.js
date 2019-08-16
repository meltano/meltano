import axios from 'axios'
import utils from '@/utils/utils'

export default {
  index() {
    return axios.get(utils.apiUrl('settings'))
  },

  saveConnection(connection) {
    return axios.post(utils.apiUrl('settings', 'save'), connection)
  },

  deleteConnection(connection) {
    return axios.post(utils.apiUrl('settings', 'delete'), connection)
  },

  fetchACL() {
    return axios.get(utils.apiUrl('settings', 'acl'))
  },

  createRole(role, user) {
    const payload = { role, user }
    return axios.post(utils.apiUrl('settings', 'acl/roles'), payload)
  },

  deleteRole(role, user) {
    const payload = { role, user }

    return axios.delete(utils.apiUrl('settings', 'acl/roles'), {
      data: payload
    })
  },

  addRolePermission(role, permissionType, context) {
    const payload = { permissionType, role, context }
    return axios.post(
      utils.apiUrl('settings', 'acl/roles/permissions'),
      payload
    )
  },

  removeRolePermission(role, permissionType, context) {
    const payload = { permissionType, role, context }

    return axios.delete(utils.apiUrl('settings', 'acl/roles/permissions'), {
      data: payload
    })
  }
}
