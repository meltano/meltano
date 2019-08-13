<script>
export default {
  name: 'ClosableMessage',
  data() {
    return {
      isShowNote: true
    }
  },
  props: {
    title: String
  },
  methods: {
    closeNote() {
      this.isShowNote = false
    }
  }
}
</script>

<template>
  <div v-if="isShowNote" class="columns">
    <div class="column">
      <div class="content">
        <article class="message is-small">
          <div class="message-header">
            {{ title }}
            <button
              class="delete is-small"
              aria-label="delete"
              @click="closeNote"
            ></button>
          </div>
          <div class="message-body has-text-centered">
            <slot></slot>
          </div>
        </article>
      </div>
    </div>
  </div>
</template>

<style lang="scss"></style>
