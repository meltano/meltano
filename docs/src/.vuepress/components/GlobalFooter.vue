<script>
export default {
  name: "GlobalFooter"
};
</script>

<template>
  <footer class="footer">
    <p>
      <a
        href="https://meltano.com/docs/contributor-guide.html"
        target="_blank"
      >
        Meltano is open source. Contribute to the project! <OutboundLink />
      </a>
    </p>
    <p>
      Copyright 2021 Meltano &mdash; All rights reserved
    </p>
  </footer>
</template>

<style lang="stylus">
.footer
  display flex
  flex-direction column
  padding 2rem 1.5rem
  text-align center
  color white
  background-color #3e3c8e

  p
    margin 0.5rem

  a
    color white
    font-weight 500

    &:hover
      text-decoration underline
</style>
