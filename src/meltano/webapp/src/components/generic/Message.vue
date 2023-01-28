<script>
export default {
  name: 'Message',
}
</script>

<template>
  <div class="content">
    <article class="message is-info is-small">
      <div class="message-header">
        <a
          class="button is-borderless has-background-transparent has-text-white"
        >
          <span class="icon">
            <font-awesome-icon icon="info-circle"></font-awesome-icon>
          </span>
          <span>Info</span>
        </a>
      </div>
      <div class="message-body">
        <slot></slot>
      </div>
    </article>
  </div>
</template>

<style lang="scss"></style>
