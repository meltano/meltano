
<template>
  <div style="margin-bottom: 2em;">
    <h2 class="subtitle is-4">{{permission.name}}</h2>
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
                <context-pill v-for="context in role.contexts"
                              :key="context"
                              :name="context"
                              @delete="remove(role, context)"
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
                       placeholder="Design filter"
                       @keyup.enter="add"
                />
              </div>
              <div class="control">
                <button @click="add"
                        class="button is-primary"
                        :disabled="!enabled">
                  Add
                </button>
              </div>
            </div>
          </td>
        </tr>
      </tfoot>
    </table>
  </div>
</template>

<script>
import _ from 'lodash';
import Pill from './Pill';

export default {
  name: 'RolePermissions',
  props: ['permission', 'roles'],
  data() {
    return {
      model: {
        permissionType: this.permission.type,
        role: null,
        context: null,
      },
    };
  },

  components: {
    'context-pill': Pill,
  },

  computed: {
    enabled() {
      return !(_.isEmpty(this.model.role) ||
               _.isEmpty(this.model.context));
    },
  },

  methods: {
    add() {
      this.$emit('add', this.model);
      this.model.context = null;
    },
    remove(role, context) {
      this.$emit('remove', {
        permissionType: this.permission.type,
        role: role.name,
        context,
      });
    },
  },
};
</script>
