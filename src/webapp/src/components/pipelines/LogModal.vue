<script>
export default {
  name: 'LogModal',
  created() {
    this.jobIdFromRoute = this.$route.params.jobId
  },
  methods: {
    close() {
      if (this.prevRoute) {
        this.$router.go(-1)
      } else {
        this.$router.push({ name: 'schedules' })
      }
    }
  }
}
</script>

<template>
  <div class="modal is-active">
    <div class="modal-background" @click="close"></div>
    <div class="modal-card is-wide">
      <header class="modal-card-head">
        <p class="modal-card-title">Run Log</p>
        <button class="delete" aria-label="close" @click="close"></button>
      </header>
      <section class="modal-card-body">
        <div class="content">
          <p>{{ jobIdFromRoute }}</p>
        </div>
      </section>
      <footer class="modal-card-foot buttons is-right">
        <button class="button" @click="close">Close</button>
      </footer>
    </div>
  </div>
</template>

<style lang="scss"></style>
