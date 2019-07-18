import lodash from 'lodash';

import settingsApi from '../../api/settings';

const defaultState = Object.freeze({
  settings: {
    connections: [],
  },
  acl: {
    users: [],
    roles: [],
    permissions: [],
  },
});

const getters = {
  hasConnections(state) {
    return state.settings.connections && state.settings.connections.length;
  },
  isConnectionDialectSqlite() {
    return connectionDialect => connectionDialect === 'sqlite';
  },
  rolesName(state) {
    return lodash.map(state.acl.roles, lodash.property('name'));
  },
  rolesContexts(state) {
    return type => lodash.map(state.acl.roles, (r) => {
      // filter out other permission types
      const perms = lodash(r.permissions).groupBy('type').get(type);
      return {
        name: r.name,
        contexts: lodash.map(perms, 'context'),
      };
    });
  },
};

const actions = {
  getSettings({ commit }) {
    return settingsApi.index()
      .then((response) => {
        commit('setSettings', response.data.settings);
      });
  },
  saveConnection({ commit }, connection) {
    settingsApi.saveConnection(connection)
      .then((response) => {
        commit('setSettings', response.data.settings);
      });
  },
  deleteConnection({ commit, state }, connection) {
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
  deleteRole({ commit, state }, { role }) {
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
  setSettings(state, settings) {
    state.settings = settings;
  },
  setACL(state, acl) {
    state.acl = acl;
  },
  addRole(state, role) {
    if (lodash.find(state.acl.roles, ['name', role.name])) {
      return;
    }

    state.acl.roles = lodash.concat(state.acl.roles, role);
  },
  removeRole(state, role) {
    state.acl.roles = lodash.filter(state.acl.roles, r => r.name !== role);
  },
  unassignUserRole(state, { user, role }) {
    const assignedUser = lodash.find(state.acl.users, ['username', user]);
    assignedUser.roles = lodash.without(assignedUser.roles, role);
  },
  assignUserRoles(state, { user, role }) {
    const assignedUser = lodash.find(state.acl.users, ['username', user]);

    if (assignedUser && !assignedUser.roles.includes(role)) {
      assignedUser.roles = lodash.concat(assignedUser.roles, role);
    }
  },
  addRolePermission(state, { permissionType, role, context }) {
    const assignedRole = lodash.find(state.acl.roles, ['name', role]);
    const perms = assignedRole.permissions[permissionType];

    if (assignedRole && !perms.includes(context)) {
      assignedRole.permissions[permissionType] = lodash.concat(perms, context);
    }
  },
  removeRolePermission(state, { permissionType, role, context }) {
    const assignedRole = lodash.find(state.acl.roles, ['name', role]);
    const perms = assignedRole.permissions[permissionType];

    assignedRole.permissions[permissionType] = lodash.without(perms, context);
  },
  updateRole(state, role) {
    const update = r => (r.name === role.name ? role : r);
    state.acl.roles = lodash.map(state.acl.roles, update);
  },
};

export default {
  namespaced: true,
  state: lodash.cloneDeep(defaultState),
  getters,
  actions,
  mutations,
};
