<template>
  <footer class="page-edit">
    <div class="inner">
      <div v-if="editLink" class="edit-link">
        <a
          :href="editLink"
          target="_blank"
          rel="noopener noreferrer"
          >{{ editLinkText }}</a
        >
        <OutboundLink />
      </div>

      <div v-if="lastUpdated" class="last-updated">
        <span class="prefix">{{ lastUpdatedText }}:</span>
        <span class="time">{{ lastUpdated }}</span>
      </div>

      <div class="edit-link">
        <a
          href="https://gitlab.com/meltano/meltano/issues/new"
          target="_blank"
          rel="noopener noreferrer"
          >Submit an issue</a
        >
        <OutboundLink />
      </div>
    </div>
  </footer>
</template>

<script>
import ParentPageEdit from '@parent-theme/components/PageEdit.vue'

import isNil from 'lodash/isNil'
import { endingSlashRE, outboundRE } from '@parent-theme/util'

export default {
  name: 'PageEdit',

  computed: {
    lastUpdated () {
      return this.$page.lastUpdated
    },

    lastUpdatedText () {
      if (typeof this.$themeLocaleConfig.lastUpdated === 'string') {
        return this.$themeLocaleConfig.lastUpdated
      }
      if (typeof this.$site.themeConfig.lastUpdated === 'string') {
        return this.$site.themeConfig.lastUpdated
      }
      return 'Last Updated'
    },

    editLink () {
      const showEditLink = isNil(this.$page.frontmatter.editLink)
        ? this.$site.themeConfig.editLinks
        : this.$page.frontmatter.editLink

      const {
        repo,
        docsDir = '',
        docsBranch = 'master',
        docsRepo = repo
      } = this.$site.themeConfig

      if (showEditLink && docsRepo && this.$page.relativePath) {
        return this.createEditLink(
          repo,
          docsRepo,
          docsDir,
          docsBranch,
          this.$page.relativePath
        )
      }
      return null
    },

    editLinkText () {
      return (
        this.$themeLocaleConfig.editLinkText
        || this.$site.themeConfig.editLinkText
        || `Edit this page`
      )
    }
  },

  methods: {
    createEditLink (repo, docsRepo, docsDir, docsBranch, path) {
      const bitbucket = /bitbucket.org/
      if (bitbucket.test(docsRepo)) {
        const base = docsRepo
        return (
          base.replace(endingSlashRE, '')
          + `/src`
          + `/${docsBranch}/`
          + (docsDir ? docsDir.replace(endingSlashRE, '') + '/' : '')
          + path
          + `?mode=edit&spa=0&at=${docsBranch}&fileviewer=file-view-default`
        )
      }

      const gitlab = /gitlab.com/
      if (gitlab.test(docsRepo)) {
        const base = docsRepo
        return (
          base.replace(endingSlashRE, '')
          + `/-/edit`
          + `/${docsBranch}/`
          + (docsDir ? docsDir.replace(endingSlashRE, '') + '/' : '')
          + path
        )
      }

      const base = outboundRE.test(docsRepo)
        ? docsRepo
        : `https://github.com/${docsRepo}`
      return (
        base.replace(endingSlashRE, '')
        + '/edit'
        + `/${docsBranch}/`
        + (docsDir ? docsDir.replace(endingSlashRE, '') + '/' : '')
        + path
      )
    }
  }
}
</script>

<style lang="stylus">
.page-edit
  padding-top 0
  padding-bottom 0
  margin-bottom: 1rem;

  .inner
    line-height 2rem
    border-top 1px solid $borderColor
    padding-top 1rem
    display flex
    justify-content space-between

  .last-updated
    color #888
    font-style italic

    .prefix
      color #888

.page-nav
  padding-top 0 !important
  margin-top 1rem !important

@media (max-width: $MQMobile)
  .page-edit
    .inner
      display flex
      flex-direction column

    .last-updated
      order 1
</style>
