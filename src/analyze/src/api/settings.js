import axios from 'axios';
import utils from '@/utils/utils';

export default {
  index(slug) {
    return axios.get(utils.apiUrl('settings', `projects/${slug}`));
  },

  saveConnection(connection, slug) {
    return axios.post(utils.apiUrl('settings', `projects/${slug}/save`), connection);
  },

  deleteConnection(connection, slug) {
    return axios.post(utils.apiUrl('settings', `projects/${slug}/delete`), connection);
  },

  fetchACL(slug) {
    return axios.get(utils.apiUrl('settings', `projects/${slug}/acl`));
  },

  createRole(role, user, slug) {
    const payload = { role, user };
    return axios.post(utils.apiUrl('settings', `projects/${slug}/acl/roles`), payload);
  },

  deleteRole(role, user, slug) {
    const payload = { role, user };

    return axios.delete(utils.apiUrl('settings', `projects/${slug}/acl/roles`), { data: payload });
  },

  addRolePermission(role, permissionType, context, slug) {
    const payload = { permissionType, role, context };
    return axios.post(utils.apiUrl('settings', `projects/${slug}/acl/roles/permissions`), payload);
  },

  removeRolePermission(role, permissionType, context, slug) {
    const payload = { permissionType, role, context };

    return axios.delete(utils.apiUrl('settings', `projects/${slug}/acl/roles/permissions`), { data: payload });
  },
};
