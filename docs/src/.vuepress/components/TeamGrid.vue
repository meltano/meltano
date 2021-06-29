<template>
  <div>
    <Content class="intro" slot-key="intro" />

    <ul class="members">
      <li v-for="member in members" :key="member.name">
        <img :src="`https://secure.gravatar.com/avatar/${member.gravatar_hash}?s=240&d=identicon`" class="avatar" />

        <h2>{{member.name}}</h2>
        <small>{{member.location}}</small>
        <small v-if="member.start_date">Starts {{member.start_date}}</small>

        <strong>{{member.title}}</strong>

        <ul class="social">
          <li v-if="member.social.linkedin" class="linkedin">
            <a :href="`https://linkedin.com/in/${member.social.linkedin}`" target="_blank">
              <LinkedInIcon />
            </a>
          </li>

          <li v-if="member.social.gitlab" class="gitlab">
            <a :href="`https://gitlab.com/${member.social.gitlab}`" target="_blank">
              <GitLabIcon />
            </a>
          </li>

          <li v-if="member.social.twitter" class="twitter">
            <a :href="`https://twitter.com/${member.social.twitter}`" target="_blank">
              <TwitterIcon />
            </a>
          </li>
        </ul>
      </li>

      <!-- TODO: You? -->
    </ul>
  </div>
</template>

<script>
export default {
  name: "TeamGrid",

  props: {
    members: {
      type: Array,
      required: true
    }
  },
};
</script>

<style lang="stylus">
.intro
  text-align center

ul.members
  padding: 1.5rem 0
  line-height inherit
  display grid
  grid-template-columns repeat(auto-fit, minmax(150px, 1fr))
  grid-column-gap 1rem
  grid-row-gap 1.5rem
  align-items top
  justify-content center

  > li
    list-style none
    text-align center

    > *
      margin: 0 auto
      display block

    img.avatar
      width 120px
      height 120px
      border 3px solid $accentColor
      border-radius 120px
      margin-bottom .5rem

    h2
      font-size 1.3em
      padding 0
      margin 0
      border none

    small
      font-size 0.9em

    strong
      margin: 1rem auto

    ul.social
      padding: 0

      > li
        list-style: none
        display: inline-block
</style>
