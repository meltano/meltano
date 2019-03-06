import _ from 'lodash';
import settingsApi from '../../api/settings';

const state = {
  settings: {
    connections: [],
  },
  acl: {
    users: [],
    roles: [],
    permissions: [],
  },
};

const getters = {
  hasConnections() {
    return state.settings.connections && state.settings.connections.length;
  },
  isConnectionDialectSqlite() {
    return connectionDialect => connectionDialect === 'sqlite';
  },

  rolesName() {
    return _.map(state.acl.roles, _.property('name'));
  },
  rolesContexts() {
    return type => _.map(state.acl.roles, (r) => {
      // filter out other permission types
      const perms = _(r.permissions).groupBy('type').get(type);
      return {
        name: r.name,
        contexts: _.map(perms, 'context'),
      };
    });
  },
};

const actions = {
  getSettings({ commit }) {
    return settingsApi.index().then((response) => {
      commit('setSettings', response.data.settings);
    });
  },
  saveConnection({ commit }, connection) {
    settingsApi.saveConnection(connection).then((response) => {
      commit('setSettings', response.data.settings);
    });
  },
  deleteConnection({ commit }, connection) {
    const connectionToRemove = state.settings.connections
      .find(item => item === connection);
    settingsApi.deleteConnection(connectionToRemove)
      .then((response) => {
        commit('setSettings', response.data.settings);
      });
  },
  fetchACL({ commit }) {
    return settingsApi.fetchACL()
      .then((response) => {
        commit('setACL', response.data);
      });
  },
  createRole({ commit }, { role }) {
    settingsApi.createRole({ name: role })
      .then((response) => {
        commit('addRole', response.data);
      });
  },
  assignRoleUser({ commit }, { role, user }) {
    const roleDef = { name: role };

    // create automatically assign the user if set
    settingsApi.createRole(roleDef, user)
      .then(() => {
        commit('assignUserRoles', { user, role });
      });
  },
  deleteRole({ commit }, { role }) {
    settingsApi.deleteRole({ name: role })
      .then(() => {
        commit('removeRole', role);

        state.acl.users.forEach((user) => {
          commit('unassignUserRole', { user: user.username, role });
        });
      });
  },
  unassignRoleUser({ commit }, { role, user }) {
    if (user === undefined) {
      return;
    }

    const roleDef = { name: role };
    settingsApi.deleteRole(roleDef, user)
      .then(() => {
        commit('unassignUserRole', { user, role });
      });
  },
  addRolePermission({ commit }, { permissionType, role, context }) {
    const roleDef = { name: role };

    settingsApi.addRolePermission(roleDef, permissionType, context)
      .then((response) => {
        commit('updateRole', response.data);
      });
  },
  removeRolePermission({ commit }, { permissionType, role, context }) {
    const roleDef = { name: role };

    settingsApi.removeRolePermission(roleDef, permissionType, context)
      .then((response) => {
        commit('updateRole', response.data);
      });
  },
};

const mutations = {
  setSettings(_store, settings) {
    state.settings = settings;
  },
  setACL(_store, acl) {
    state.acl = acl;
  },
  addRole(_store, role) {
    if (_.find(state.acl.roles, ['name', role.name])) {
      return;
    }

    state.acl.roles = _.concat(state.acl.roles, role);
  },
  removeRole(_store, role) {
    state.acl.roles = _.filter(state.acl.roles, r => r.name !== role);
  },
  unassignUserRole(_store, { user, role }) {
    const assignedUser = _.find(state.acl.users, ['username', user]);
    assignedUser.roles = _.without(assignedUser.roles, role);
  },
  assignUserRoles(_store, { user, role }) {
    const assignedUser = _.find(state.acl.users, ['username', user]);

    if (assignedUser && !assignedUser.roles.includes(role)) {
      assignedUser.roles = _.concat(assignedUser.roles, role);
    }
  },
  addRolePermission(_store, { permissionType, role, context }) {
    const assignedRole = _.find(state.acl.roles, ['name', role]);
    const perms = assignedRole.permissions[permissionType];

    if (assignedRole && !perms.includes(context)) {
      assignedRole.permissions[permissionType] = _.concat(perms, context);
    }
  },
  removeRolePermission(_store, { permissionType, role, context }) {
    const assignedRole = _.find(state.acl.roles, ['name', role]);
    const perms = assignedRole.permissions[permissionType];

    assignedRole.permissions[permissionType] = _.without(perms, context);
  },
  updateRole(_store, role) {
    const update = r => (r.name === role.name ? role : r);
    state.acl.roles = _.map(state.acl.roles, update);
  },
};

export default {
  namespaced: true,
  state,
  getters,
  actions,
  mutations,
};
