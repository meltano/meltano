<template>
  <div class="container">
    <section class="section">
      <h1 class="title is-2">Users</h1>

      <div class="segment">
        <h2 class="subtitle is-5">Assign roles</h2>
        <role-members :users="acl.users"
                      :roles="rolesName"
                      @add="assignRoleUser($event)"
                      @remove="unassignRoleUser($event)"
        />
      </div>
      <hr/>

      <h1 class="title is-2">Roles</h1>
      <div class="segment">
        <h2 class="subtitle is-5">Create a new role</h2>
        <form>
          <div class="field is-grouped">
            <div class="control">
              <input v-model="model.role"
                     @keyup.enter="createRole(model)"
                     type="text"
                     class="input"
                     placeholder="Role name" />
            </div>
            <div class="control">
              <button class="button is-success"
                      :disabled="!has(model.role)"
                      @click.prevent="createRole(model)">
                Create
              </button>
            </div>
            <div class="control">
              <button class="button is-danger"
                      :disabled="!has(model.role)"
                      @click.prevent="deleteRole(model)">
                Delete
              </button>
            </div>
          </div>
        </form>
      </div>
      <hr/>

      <h1 class="title is-4">Permissions</h1>
      <div class="segment">
        <role-permissions v-for="perm in permissions"
                          :key="perm.type"
                          :permission="perm"
                          :roles="rolesContexts(perm.type)"
                          @add="addRolePermission($event)"
                          @remove="removeRolePermission($event)"
        />
      </div>
    </section>
  </div>
</template>
<script>
import _ from 'lodash';
import { mapState, mapGetters, mapActions } from 'vuex';
import RoleMembers from './RoleMembers';
import RolePermissions from './RolePermissions';


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
    RoleMembers,
    RolePermissions,
  },

  created() {
    this.$store.dispatch('settings/fetchACL');
  },

  computed: {
    has() {
      return _.negate(_.isEmpty);
    },
    ...mapState('settings', [
      'acl',
    ]),
    ...mapGetters('settings', [
      'rolesName',
      'rolesContexts',
    ]),
  },

  methods: {
    ...mapActions('settings', [
      'createRole',
      'deleteRole',
      'unassignRoleUser',
      'assignRoleUser',
      'addRolePermission',
      'removeRolePermission',
    ]),
  },
};
</script>
<style scoped>
 .segment {
   margin-bottom: 2rem;
 }
</style>
