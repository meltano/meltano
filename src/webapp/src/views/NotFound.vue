<script>
export default {
  name: 'NotFound'
}
</script>

<template>
  <section class="hero is-fullheight">
    <div class="hero-body">
      <div class="container has-text-centered">
        <h1 class="title">
          404
        </h1>
        <h2 class="subtitle">
          Oops... Seems like this page is missing...
        </h2>
        <a class="button" @click="$router.back()">Go back to the last page</a>
      </div>
    </div>
  </section>
</template>

<style lang="scss"></style>
