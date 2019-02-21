<template>
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
                         @delete="$emit('remove', { role, user: user.username })"
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
                      @click="$emit('add', model)"
                      :disabled="!enabled">
                Assign
              </button>
            </div>
          </div>
        </td>
      </tr>
    </tfoot>
  </table>
</template>
<script>
import _ from 'lodash';
import Pill from './Pill';

export default {
  name: 'RoleMember',
  props: ['users', 'roles'],
  data() {
    return {
      model: {
        user: null,
        role: null,
      },
    };
  },

  computed: {
    enabled() {
      return !(_.isEmpty(this.model.role) ||
               _.isEmpty(this.model.user));
    },
  },

  components: {
    'role-pill': Pill,
  },
};
</script>
