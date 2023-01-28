<script>
import _ from 'lodash'
import store from '@/store'
import { mapActions, mapGetters, mapState } from 'vuex'
import RoleMembers from './RoleMembers'
import RolePermissions from './RolePermissions'

export default {
  name: 'Roles',

  components: {
    RoleMembers,
    RolePermissions,
  },

  beforeRouteEnter(to, from, next) {
    store
      .dispatch('settings/fetchACL')
      .then(next)
      .catch(() => {
        next(from.path)
      })
  },

  data() {
    return {
      permissions: [
        { name: 'View designs', type: 'view:design' },
        { name: 'View reports', type: 'view:reports' },
      ],
      model: {
        role: null,
      },
    }
  },

  computed: {
    has() {
      return _.negate(_.isEmpty)
    },
    ...mapState('settings', ['acl']),
    ...mapGetters('settings', ['rolesName', 'rolesContexts']),
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
}
</script>

<template>
  <section class="section">
    <h1 class="title is-2">Roles</h1>
    <div class="segment">
      <h2 class="title is-4">Manage roles</h2>
      <form>
        <div class="field is-grouped">
          <div class="control">
            <input
              v-model="model.role"
              type="text"
              class="input"
              placeholder="Role name"
              @keyup.enter="has(model.role) && createRole(model)"
            />
          </div>
          <div class="control">
            <button
              class="button is-interactive-primary"
              :disabled="!has(model.role)"
              @click.prevent="createRole(model)"
            >
              Create
            </button>
          </div>
          <div class="control">
            <button
              class="button is-danger"
              :disabled="!has(model.role)"
              @click.prevent="deleteRole(model)"
            >
              Delete
            </button>
          </div>
        </div>
      </form>
    </div>

    <h2 class="title is-4">Permissions</h2>
    <div class="segment">
      <role-permissions
        v-for="perm in permissions"
        :key="perm.type"
        :permission="perm"
        :roles="rolesContexts(perm.type)"
        @add="addRolePermission($event)"
        @remove="removeRolePermission($event)"
      />
    </div>

    <h2 class="title is-4">Users</h2>
    <div class="segment">
      <role-members
        :users="acl.users"
        :roles="rolesName"
        @add="assignRoleUser($event)"
        @remove="unassignRoleUser($event)"
      />
    </div>
  </section>
</template>

<style scoped>
.segment {
  margin-bottom: 2rem;
}

.action {
  margin-bottom: 0.33rem;
}
</style>
