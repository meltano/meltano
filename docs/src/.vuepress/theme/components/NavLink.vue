<template>
  <a
    v-if="item.twitter"
    :href="item.link"
    target="_blank"
    class="nav-link nav-link--icon"
  >
    <TwitterIcon />
    <span>{{item.text}}</span>
  </a>
  <a v-else-if="item.cta" :href="item.link" class="nav-link nav-link--cta">
    {{item.text}}
  </a>
  <ParentNavLink v-else :item="item" />
</template>

<script>
import ParentNavLink from '@parent-theme/components/NavLink.vue'
import TwitterIcon from '@theme/components/TwitterIcon'

export default {
  name: 'NavLink',
  components: {
    ParentNavLink,
    TwitterIcon
  },
  props: {
    item: {
      required: true
    }
  },
}
</script>
<style lang="stylus">
.nav-links
  .nav-item > a
    transition: background-color .2s ease;

    &:hover, &.router-link-active
      margin-bottom -2px
      border-bottom 2px solid lighten($accentColor, 8%)

    &.nav-link--icon
      svg
        vertical-align top
      span
        display none

    &.nav-link--cta
      display inline-block
      background-color $accentColor
      color white
      padding 0 0.75rem
      border-radius 5px
      margin-right 1rem
      line-height: 2.2rem;

      &:hover, &.router-link-active
        margin-bottom 0
        border-bottom none

        background-color: lighten($accentColor, 10%);

@media (max-width: $MQMobile)
  .nav-links
    .nav-item > a.nav-link--icon span
      display: inline
</style>
