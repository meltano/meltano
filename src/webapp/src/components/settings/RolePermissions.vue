<script>
import _ from 'lodash'
import Pill from './Pill'

export default {
  name: 'RolePermissions',
  components: {
    'context-pill': Pill,
  },
  props: {
    permission: {
      type: Object,
      required: true,
    },
    roles: {
      type: Array,
      default: () => [],
    },
  },
  data() {
    return {
      model: {
        permissionType: this.permission.type,
        role: null,
        context: null,
      },
    }
  },

  computed: {
    enabled() {
      return !(_.isEmpty(this.model.role) || _.isEmpty(this.model.context))
    },
  },

  methods: {
    add() {
      this.$emit('add', this.model)
      this.model.context = null
    },
    remove(role, context) {
      this.$emit('remove', {
        permissionType: this.permission.type,
        role: role.name,
        context,
      })
    },
  },
}
</script>

<template>
  <div class="box table-container" style="margin-bottom: 2em">
    <p class="is-italic">{{ permission.name }}</p>
    <table class="table is-fullwidth">
      <thead>
        <tr>
          <th>Roles</th>
          <th>Context</th>
        </tr>
      </thead>
      <tbody>
        <template v-for="role in roles">
          <tr :key="role.name">
            <td>{{ role.name }}</td>
            <td>
              <div class="field is-grouped is-grouped-multiline">
                <context-pill
                  v-for="context in role.contexts"
                  :key="context"
                  :name="context"
                  @delete="remove(role, context)"
                />
              </div>
            </td>
          </tr>
        </template>
      </tbody>
    </table>
    <label class="action">Assign filter</label>
    <div class="controls field is-grouped">
      <div class="control">
        <div class="select">
          <select v-model="model.role">
            <option :value="null">Select a role</option>
            <option v-for="role in roles" :key="role.name">
              {{ role.name }}
            </option>
          </select>
        </div>
      </div>
      <div class="control is-expanded">
        <input
          v-model="model.context"
          type="text"
          class="input"
          placeholder="Design filter"
          @keyup.enter="enabled && add"
        />
      </div>
      <div class="control">
        <button class="button is-primary" :disabled="!enabled" @click="add">
          Add
        </button>
      </div>
    </div>
  </div>
</template>

<style scoped>
.action {
  font-weight: bold;
}
.controls {
  margin-top: 0.5rem;
}
</style>
