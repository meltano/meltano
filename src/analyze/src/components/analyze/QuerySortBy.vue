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
    draggableOptions() {
      return {
        animation: 100,
        delay: -1,
        disabled: false,
        emptyInsertThreshold: 30,
        ghostClass: 'drag-ghost',
        group: 'sortBy',
        swapThreshold: 1,
      };
    },
  },
  methods: {
    toggleDirection: (orderable) => {
      console.log('toggleDirection', orderable);
    }
  }
};
</script>

<template>
  <div>
    <div class="dropdown-item">
      <draggable
        v-model='order.unassigned'
        v-bind='draggableOptions'
        class='drag-list is-flex is-flex-column has-background-white-bis'
        :class='order.unassigned.length === 0 ? "dashed" : ""'>
        <transition-group>
          <div
            v-for='orderable in order.unassigned'
            :key='`${orderable.attributeName}-${orderable.id}`'
            class='drag-list-item has-background-white'>
            <div class="drag-handle">
              <span class="icon is-small">
                <font-awesome-icon icon="arrows-alt-v"></font-awesome-icon>
              </span>
              <span>{{orderable.attributeLabel}}</span>
            </div>
          </div>
        </transition-group>
      </draggable>
    </div>
    <hr class='dropdown-divider'>
    <div class='dropdown-item'>
      <draggable
        v-model='order.assigned'
        v-bind='draggableOptions'
        class='drag-list is-flex is-flex-column has-background-white-bis'
        :class='order.assigned.length === 0 ? "dashed" : ""'>
        <transition-group>
          <div
            v-for='(orderable, idx) in order.assigned'
            :key='`${orderable.attributeName}-${orderable.id}`'
            class='drag-list-item has-background-white has-text-interactive-secondary'>
            <div class="drag-handle">
              <span class="icon is-small">
                <font-awesome-icon icon="arrows-alt-v"></font-awesome-icon>
              </span>
              <span>{{idx + 1}}.</span>
              <span>{{orderable.attributeLabel}}</span>
            </div>
            <button
              class="button is-small"
              @click="toggleDirection">
              <span class="icon is-small has-text-interactive-secondary">
                <!-- TODO toggle icon based on asc/desc -->
                <font-awesome-icon icon="sort-amount-down"></font-awesome-icon>
              </span>
            </button>
          </div>
        </transition-group>
      </draggable>
    </div>
  </div>
</template>

<style lang="scss">
.drag-list {
  min-height: 30px;
  font-weight: normal;

  &.dashed {
    border: 2px dashed lightgrey;
  }
}
.drag-list-item {
  display: flex;
  flex-direction: row;
  justify-content: space-between;
  padding: 4px;

  .drag-handle {
    flex-grow: 1;
    cursor: grab;

    .icon {
      margin-right: .25rem;
    }
  }
}
.drag-ghost {
  opacity: 0.5;
}
</style>
