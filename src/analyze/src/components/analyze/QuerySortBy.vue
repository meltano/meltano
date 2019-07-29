<script>
import { mapState } from 'vuex';

import draggable from 'vuedraggable';

export default {
  name: 'QuerySortBy',
  components: {
    draggable,
  },
  computed: {
    ...mapState('designs', [
      'order',
    ]),
    // TODO draggable props vs computed
    dragOptions() {
      return {
        animation: 200,
        group: 'sortBy',
        disabled: false,
        ghostClass: 'ghost',
      };
    },
  },
};
</script>

<template>
  <div>
    <div class="dropdown-item">
      <h4>Unassigned</h4>
      <draggable
        v-model='order.unassigned'
        v-bind='dragOptions'
        class='drag-list is-flex is-flex-column'
        group='sortBy'>
        <transition-group>
          <div
            v-for='orderable in order.unassigned'
            :key='`${orderable.attributeName}-${orderable.id}`'
            class='drag-list-item'>
            {{orderable.attributeName}}
          </div>
        </transition-group>
      </draggable>
    </div>
    <hr class='dropdown-divider'>
    <div class='dropdown-item'>
      <h4>Assigned</h4>
      <draggable
        v-model='order.assigned'
        v-bind='dragOptions'
        class='drag-list is-flex is-flex-column'
        group='sortBy'>
        <transition-group>
          <div
            v-for='orderable in order.assigned'
            :key='`${orderable.attributeName}-${orderable.id}`'
            class='drag-list-item'>
            {{orderable.attributeName}}
          </div>
        </transition-group>
      </draggable>
    </div>
  </div>
</template>

<style lang="scss">
.drag-list {
  min-height: 30px;
}
.drag-list-item {
  cursor: grab;
}
.ghost {
  opacity: 0.5;
}
</style>
