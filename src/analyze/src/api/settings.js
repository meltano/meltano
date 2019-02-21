import axios from 'axios';
import utils from './utils';

export default {
  index() {
    return axios.get(utils.buildUrl('settings'));
  },
  saveConnection(connection) {
    return axios.post(utils.buildUrl('settings', 'save'), connection);
  },
  deleteConnection(connection) {
    return axios.post(utils.buildUrl('settings', 'delete'), connection);
  },
  fetchACL() {
    return axios.get(utils.buildUrl('settings', 'acl'));
  },
  createRole(role, user) {
    const payload = { role, user };
    return axios.post(utils.buildUrl('settings', 'acl/roles'), payload);
  },
  deleteRole(role, user) {
    const payload = { role, user };

    return axios.delete(utils.buildUrl('settings', 'acl/roles'), { data: payload });
  },
  addRolePermission(role, permissionType, context) {
    const payload = { permissionType, role, context };
    return axios.post(utils.buildUrl('settings', 'acl/roles/permissions'), payload);
  },
  removeRolePermission(role, permissionType, context) {
    const payload = { permissionType, role, context };

    return axios.delete(utils.buildUrl('settings', 'acl/roles/permissions'), { data: payload });
  },
};
