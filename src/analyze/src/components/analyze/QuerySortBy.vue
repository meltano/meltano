<script>
import { mapActions, mapGetters, mapState } from 'vuex';

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
    ...mapGetters('designs', [
      'getIsOrderableAttributeAscending',
    ]),
    draggableOptions() {
      return {
        animation: 100,
        emptyInsertThreshold: 30,
        ghostClass: 'drag-ghost',
        group: 'sortBy',
      };
    },
    getIsDashed() {
      return collection => collection.length === 0 ? "dashed" : "";
    }
  },
  methods: {
    ...mapActions('designs', [
      'updateSortAttribute',
    ]),
  },
};
</script>

<template>
  <div>
    <div class="dropdown-item">
      <draggable
        v-model='order.unassigned'
        v-bind='draggableOptions'
        class='drag-list is-flex is-flex-column has-background-white-bis'
        :class='getIsDashed(order.unassigned)'>
        <transition-group>
          <div
            v-for='orderable in order.unassigned'
            :key='`${orderable.sourceName}-${orderable.attributeName}`'
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
        :class='getIsDashed(order.assigned)'>
        <transition-group>
          <div
            v-for='(orderable, idx) in order.assigned'
            :key='`${orderable.sourceName}-${orderable.attributeName}`'
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
              @click="updateSortAttribute(orderable)">
              <span class="icon is-small has-text-interactive-secondary">
                <font-awesome-icon :icon="getIsOrderableAttributeAscending(orderable) ? 'sort-amount-down' : 'sort-amount-up'"></font-awesome-icon>
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
    border: 1px dashed lightgrey;
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
