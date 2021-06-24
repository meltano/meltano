<template>
  <div>
    <header class="banner">
      <p>
        <a href="https://meltano.com/blog/2021/06/30/meltano-spins-out-of-gitlab-raises-seed-round">
          Meltano spins out of GitLab, raises $4.2M in Seed funding led by GV to bring data integration into the DataOps era
        </a>
      </p>
    </header>

    <ParentNavbar @toggle-sidebar="$emit('toggle-sidebar')" />
  </div>
</template>

<script>
import ParentNavbar from '@parent-theme/components/Navbar.vue'

export default {
  components: { ParentNavbar }
}
</script>

<style lang="stylus">
.navbar
  top $bannerHeight
  .logo
    height 2.3rem !important
    margin-top -0.1em

  .site-name
    display none

.theme-container.no-navbar
  .navbar
    display none

.navbar
  line-height $origNavbarHeight - 1.4rem
  height $origNavbarHeight

.banner
  position fixed
  z-index 20
  top 0
  left 0
  right 0
  height $bannerHeight
  background-color $accentColor
  color white

  p
    line-height $bannerHeight
    padding 0
    margin 0
    text-align center
    font-weight bold

    a
      color inherit
      font-weight inherit

      &:hover
        text-decoration underline
</style>
