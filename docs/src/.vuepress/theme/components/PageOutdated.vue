<template>
  <div
    class="theme-default-content content-possibly-outdated"
    v-if="contentPossiblyOutdated"
  >
    <div class="warning custom-block">
      <p class="custom-block-title">
        This page
        {{ lastUpdatedSignificantly ? "received its last significant update" : "was last updated" }}
        on <strong>{{ lastUpdatedSignificantly || lastUpdated }}</strong>
      </p>

      <p>
        Since then, there have been some
        <a
          href="https://meltano.com/blog/2020/05/13/revisiting-the-meltano-strategy-a-return-to-our-roots/"
          target="_blank"
          >significant changes</a
        >
        to our
        <a
          href="https://meltano.com/blog/2020/05/13/why-we-are-building-an-open-source-platform-for-elt-pipelines/"
          target="_blank"
          >strategy, direction, and focus</a
        >, so statements and recommendations may be outdated and not all
        examples may work.
      </p>

      <p v-if="editLink">
        If you encounter any inaccuracies, we welcome you to
        <a :href="editLink" target="_blank" rel="noopener noreferrer"
          >help us improve this page</a
        >

        or

        <a
          href="https://gitlab.com/meltano/meltano/issues/new"
          target="_blank"
          rel="noopener noreferrer"
          >submit an issue</a
        >.
      </p>
    </div>
  </div>
</template>

<script>
import isNil from 'lodash/isNil'
import { endingSlashRE, outboundRE } from '@parent-theme/util'

const POSSIBLY_OUTDATED_IF_LAST_UPDATED_BEFORE = new Date("2020-05-08");

export default {
  computed: {
    possiblyOutdatedIfLastUpdatedBefore() {
      return POSSIBLY_OUTDATED_IF_LAST_UPDATED_BEFORE.toLocaleDateString(
        this.$lang
      );
    },

    lastUpdated() {
      if (this.$page.lastUpdated) {
        return new Date(this.$page.lastUpdated).toLocaleDateString(this.$lang);
      }
    },

    lastUpdatedSignificantly() {
      const lastUpdatedSignificantly = this.$frontmatter
        .lastUpdatedSignificantly;
      if (lastUpdatedSignificantly) {
        return new Date(lastUpdatedSignificantly).toLocaleDateString(
          this.$lang
        );
      }
    },

    contentPossiblyOutdated() {
      if (this.$frontmatter.contentOutdated === false) {
        return false;
      }

      const lastUpdated = this.lastUpdatedSignificantly || this.lastUpdated;
      return (
        lastUpdated &&
        new Date(lastUpdated) < POSSIBLY_OUTDATED_IF_LAST_UPDATED_BEFORE
      );
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
};
</script>

<style lang="stylus">
.theme-default-content.content-possibly-outdated
  padding-bottom 0 !important

.theme-default-content.content-possibly-outdated + .theme-default-content
  > :first-child
    margin-top 0 !important

  > h1:first-child
    margin-top 0 !important
    padding-top 0 !important
</style>
