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
        <p class="subtitle mb-1r">
          Oops... Seems like this page is missing...
        </p>
        <p class="mb-1r">
          If you think this is a bug,
          <a
            href="https://gitlab.com/meltano/meltano/issues/new?issue"
            target="_blank"
          >
            open a new issue
          </a>
          and include the URL you are trying to access.
        </p>
        <a class="button" @click="$router.back()">Go back to the last page</a>
      </div>
    </div>
  </section>
</template>

<style lang="scss" scoped>
.mb-1r {
  margin-bottom: 1rem;
}
</style>
