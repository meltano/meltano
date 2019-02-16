<template>
  <div class="container">
    <section class="section">
      <h1 class="title is-2">Roles</h1>

      <div class="segment">
        <h2 class="subtitle is-4">Create a new role</h2>
        <form>
          <div class="field is-grouped">
            <div class="control">
              <input v-model="model.role"
                     type="text"
                     class="input"
                     placeholder="Role name" />
            </div>
            <div class="control">
              <button class="button is-success"
                      @click.prevent="createRole">
                Create
              </button>
            </div>
            <div class="control">
              <button class="button is-danger"
                      @click.prevent="deleteRole">
                Delete
              </button>
            </div>
          </div>
        </form>
      </div>

      <div class="segment">
        <h2 class="subtitle is-4">Members</h2>
        <roles-members :users="acl.users"
                       :roles="rolesName"
                       v-on:assignRole="assignRole"
                       v-on:unassignRole="unassignRole"
                       inline-template>
          <table class="table is-fullwidth">
            <thead>
              <tr>
                <th>User</th>
                <th>Roles</th>
              </tr>
            </thead>
            <tbody>
              <template v-for="user in users">
                <tr :key="user.username">
                  <td>{{ user.username }}</td>
                  <td>
                    <div class="field is-grouped is-grouped-multiline">
                      <role-pill v-for="role in user.roles"
                                 v-on:unassign="unassignRole(user, role)"
                                 :key="role"
                                 :name="role"
                      />
                    </div>
                  </td>
                </tr>
              </template>
            </tbody>
            <tfoot>
              <tr>
                <td>
                  <div class="field">
                    <div class="control">
                      <div class="select">
                        <select v-model="model.user">
                          <option :value="null">Select a user</option>
                          <option v-for="user in users"
                                  :key="user.username"
                          >{{user.username}}</option>
                        </select>
                      </div>
                    </div>
                  </div>
                </td>
                <td>
                  <div class="field is-grouped">
                    <div class="control">
                      <div class="select">
                        <select v-model="model.role">
                          <option :value="null">Select a role</option>
                          <option v-for="role in roles"
                                  :key="role"
                          >{{role}}</option>
                        </select>
                      </div>
                    </div>
                    <div class="control">
                      <button class="button is-primary"
                              v-on:click="$emit('assignRole', model)">
                        Assign
                      </button>
                    </div>
                  </div>
                </td>
              </tr>
            </tfoot>
          </table>
        </roles-members>
      </div>

      <h1 class="title is-2">Permissions</h1>

      <div class="segment">
        <roles-perms v-for="perm in permissions"
                     :key="perm.type"
                     :permission_type="perm.type"
                     :roles="rolesContexts(perm.type)"
                     @addPermission="addRolePermission(perm.type, $event)"
                     @removePermission="removeRolePermission(perm.type, $event)"
                     inline-template>
          <div style="margin-bottom: 2em;">
            <h2 class="subtitle is-4">{{perm.name}}</h2>
          <table class="table is-fullwidth">
              <thead>
                <tr>
                  <th>Role</th>
                <th>Context</th>
              </tr>
            </thead>
            <tbody>
              <template v-for="role in roles">
                  <tr :key="role.name">
                    <td>{{role.name}}</td>
                  <td>
                    <div class="field is-grouped is-grouped-multiline">
                      <role-pill v-for="context in role.contexts"
                                 :key="context"
                                 :name="context"
                                 @unassign="removePermission(role, context)"
                      />
                    </div>
                  </td>
                </tr>
              </template>
            </tbody>
            <tfoot>
                <tr>
                  <td>
                    <div class="field">
                      <div class="control">
                        <div class="select">
                          <select v-model="model.role">
                            <option :value="null">Select a role</option>
                            <option v-for="role in roles"
                                    :key="role.name"
                            >{{role.name}}</option>
                        </select>
                      </div>
                    </div>
                  </div>
                </td>

                <td>
                    <div class="field is-grouped">
                      <div class="control">
                        <input v-model="model.context"
                             type="text"
                             class="input"
                             placeholder="Design filter" />
                    </div>
                    <div class="control">
                        <button @click="$emit('addPermission', model)"
                                class="button is-primary">
                          Assign
                      </button>
                    </div>
                  </div>
                </td>
              </tr>
            </tfoot>
          </table>
          </div>
        </roles-perms>
      </div>
    </section>
  </div>
</template>
<script>
import { mapState, mapGetters } from 'vuex';

const RolePill = {
  props: ['user', 'name'],
  template: `
     <div class="control">
       <div class="tags has-addons">
         <span class="tag">{{name}}</span>
         <a class="tag is-delete" @click.prevent="$emit('unassign')"></a>
       </div>
     </div>`,
};

const RolesMembers = {
  props: ['users', 'roles'],
  data() {
    return {
      model: {
        user: null,
        role: null,
      },
    };
  },

  components: {
    RolePill,
  },

  methods: {
    unassignRole(user, role) {
      this.$emit('unassignRole', { role, user: user.username });
    },
  },
};

const RolesPerms = {
  props: ['roles', 'permission_type', 'contexts'],
  data() {
    return {
      model: {
        role: null,
        context: null,
      },
    };
  },

  components: {
    RolePill,
  },

  methods: {
    removePermission(role, context) {
      this.$emit('removePermission', { role: role.name, context });
    },
  },
};

export default {
  name: 'Roles',

  data() {
    return {
      permissions: [
        { name: 'View designs', type: 'view:design' },
        { name: 'View reports', type: 'view:reports' },
      ],
      model: {
        role: null,
      },
    };
  },

  components: {
    RolesMembers,
    RolesPerms,
  },

  created() {
    this.$store.dispatch('settings/fetchACL');
  },

  computed: {
    ...mapState('settings', [
      'acl',
    ]),
    ...mapGetters('settings', [
      'rolesName',
      'rolesContexts',
    ]),
  },

  methods: {
    saveConnection() {
      this.$store.dispatch('settings/saveConnection', {
        name: this.connectionName,
        database: this.connectionDatabase,
        schema: this.connectionSchema,
        dialect: this.connectionDialect,
        host: this.connectionHost,
        port: this.connectionPort,
        username: this.connectionUsername,
        password: this.connectionPassword,
        path: this.connectionSqlitePath,
      });
      this.connectionName = '';
      this.connectionDatabase = '';
      this.connectionSchema = '';
      this.connectionDialect = '';
      this.connectionHost = '';
      this.connectionPort = '';
      this.connectionUsername = '';
      this.connectionPassword = '';
      this.connectionSqlitePath = '';
    },
    deleteConnection(connection) {
      this.$store.dispatch('settings/deleteConnection', connection);
    },
    createRole() {
      this.$store.dispatch('settings/createRole', this.model);
    },
    deleteRole() {
      this.$store.dispatch('settings/deleteRole', this.model);
    },
    unassignRole({ role, user }) {
      this.$store.dispatch('settings/unassignRoleUser', { role, user });
    },
    assignRole({ role, user }) {
      this.$store.dispatch('settings/assignRoleUser', { role, user });
    },
    addRolePermission(permissionType, { role, context }) {
      this.$store.dispatch('settings/addRolePermission', { permissionType, role, context });
    },
    removeRolePermission(permissionType, { role, context }) {
      this.$store.dispatch('settings/removeRolePermission', { permissionType, role, context });
    },
  },
};
</script>
<style scoped>
 .segment {
   margin-bottom: 2em;
 }
</style>
