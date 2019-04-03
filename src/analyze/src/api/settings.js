import axios from 'axios';
import utils from '@/utils/utils';

export default {
  index(slug) {
    return axios.get(utils.apiUrl(`projects/${slug}/settings`));
  },

  saveConnection(connection, slug) {
    return axios.post(utils.apiUrl(`projects/${slug}/settings`, 'save'), connection);
  },

  deleteConnection(connection, slug) {
    return axios.post(utils.apiUrl(`projects/${slug}/settings`, 'delete'), connection);
  },

  fetchACL(slug) {
    return axios.get(utils.apiUrl(`projects/${slug}/settings`, 'acl'));
  },

  createRole(role, user, slug) {
    const payload = { role, user };
    return axios.post(utils.apiUrl(`projects/${slug}/settings`, 'acl/roles'), payload);
  },

  deleteRole(role, user, slug) {
    const payload = { role, user };

    return axios.delete(utils.apiUrl(`projects/${slug}/settings`, 'acl/roles'), { data: payload });
  },

  addRolePermission(role, permissionType, context, slug) {
    const payload = { permissionType, role, context };
    return axios.post(utils.apiUrl(`projects/${slug}/settings`, 'acl/roles/permissions'), payload);
  },

  removeRolePermission(role, permissionType, context, slug) {
    const payload = { permissionType, role, context };

    return axios.delete(utils.apiUrl(`projects/${slug}/settings`, 'acl/roles/permissions'), { data: payload });
  },
};
