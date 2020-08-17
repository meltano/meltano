<template>
  <a
    v-if="item.icon"
    :href="item.link"
    target="_blank"
    class="nav-link nav-link--icon"
    :title="item.text"
  >
    <component :is="item.icon" />
    <span>{{item.text}}</span>
  </a>
  <a v-else-if="item.cta" :href="item.link" class="nav-link nav-link--cta">
    {{item.text}}
  </a>
  <ParentNavLink v-else :item="item" />
</template>

<script>
import ParentNavLink from '@parent-theme/components/NavLink.vue'

export default {
  name: 'NavLink',
  components: {
    ParentNavLink
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
    &:hover, &.router-link-active
      margin-bottom -2px
      border-bottom 2px solid $accentHighlightColor

    &.nav-link--icon
      margin-left -0.25rem
      margin-right -0.25rem

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

      transition background-color .2s ease

      &:hover, &.router-link-active
        margin-bottom 0
        border-bottom none

        background-color $accentHighlightColor

@media (max-width: $MQMobile)
  .nav-links
    .nav-item > a.nav-link--icon span
      display: inline
</style>
