<script>
export default {
  name: 'PromoBanner',
}
</script>

<template>
  <div
    class="promo-meltano has-text-centered has-background-primary has-text-white"
  >
    <span class="promo-message"
      >See Your Company's Data in Meltano For Free!</span
    >
    <a
      href="https://meltano.typeform.com/to/NJPwxv"
      target="_blank"
      class="button is-small"
    >
      <span>Create Meltano Account</span>
      <span class="icon">
        <font-awesome-icon icon="external-link-square-alt"></font-awesome-icon>
      </span>
    </a>
  </div>
</template>

<style lang="scss">
.promo-meltano {
  padding: 0.75rem;

  .promo-message {
    display: block;
    margin-bottom: 0.5rem;

    @media screen and (min-width: $tablet) {
      display: inline-block;
      margin-bottom: 0;
      margin-right: 0.75rem;
    }
  }
}
</style>
