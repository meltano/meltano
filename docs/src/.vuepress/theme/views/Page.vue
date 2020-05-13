<template>
  <div class="page">
    <slot name="top"/>

    <div
      class="content content-possibly-outdated"
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
          >significant changes</a> to our
          <a href="https://meltano.com/blog/2020/05/13/why-we-are-building-an-open-source-platform-for-elt-pipelines/" target="_blank">strategy, direction, and focus</a>,
          so statements and recommendations may be outdated and not all examples may work.
        </p>

        <p>
          The most up to date information can be found on the
          <router-link to="/">homepage</router-link>,
          as well as any pages that don't show this warning.
        </p>

        <p v-if="editLink">
          If you encounter any inaccuracies,
          we welcome you to
          <a
            :href="editLink"
            target="_blank"
            rel="noopener noreferrer"
          >help us improve this page</a>

          or

          <a
            href="https://gitlab.com/meltano/meltano/issues/new"
            target="_blank"
            rel="noopener noreferrer"
          >submit an issue</a>.
        </p>
      </div>
    </div>

    <Content :class="{'after-content-possibly-outdated': contentPossiblyOutdated}" :custom="false"/>

    <div class="page-nav" v-if="prev || next">
      <p class="inner">
        <span
          v-if="prev"
          class="prev"
        >
          ←
          <router-link
            v-if="prev"
            class="prev"
            :to="prev.path"
          >
            {{ prev.title || prev.path }}
          </router-link>
        </span>

        <span
          v-if="next"
          class="next"
        >
          <router-link
            v-if="next"
            :to="next.path"
          >
            {{ next.title || next.path }}
          </router-link>
          →
        </span>
      </p>
    </div>

    <div class="page-edit">
      <div class="page-edit__inner">
        <div
          class="edit-link"
          v-if="editLink"
        >
          <a
            :href="editLink"
            target="_blank"
            rel="noopener noreferrer"
          >{{ editLinkText }}</a>
          <OutboundLink/>
        </div>

        <div
          class="last-updated"
          v-if="lastUpdated"
        >
          {{ lastUpdatedText }}: {{ lastUpdated }}</span>
        </div>

        <div class="edit-link">
          <a
            href="https://gitlab.com/meltano/meltano/issues/new"
            target="_blank"
            rel="noopener noreferrer"
          >Submit an issue</a>
          <OutboundLink/>
        </div>
      </div>
    </div>

    <slot name="bottom"/>

    <GlobalFooter />
  </div>
</template>

<script>
const POSSIBLY_OUTDATED_IF_LAST_UPDATED_BEFORE = new Date("2020-05-08");

import { resolvePage, normalize, outboundRE, endingSlashRE } from "../util";

export default {
  props: ["sidebarItems"],

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

    lastUpdatedText() {
      if (typeof this.$themeLocaleConfig.lastUpdated === "string") {
        return this.$themeLocaleConfig.lastUpdated;
      }
      if (typeof this.$site.themeConfig.lastUpdated === "string") {
        return this.$site.themeConfig.lastUpdated;
      }
      return "Last Updated";
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

    prev() {
      const prev = this.$page.frontmatter.prev;
      if (prev === false) {
        return;
      } else if (prev) {
        return resolvePage(this.$site.pages, prev, this.$route.path);
      } else {
        return resolvePrev(this.$page, this.sidebarItems);
      }
    },

    next() {
      const next = this.$page.frontmatter.next;
      if (next === false) {
        return;
      } else if (next) {
        return resolvePage(this.$site.pages, next, this.$route.path);
      } else {
        return resolveNext(this.$page, this.sidebarItems);
      }
    },

    editLink() {
      if (this.$page.frontmatter.editLink === false) {
        return;
      }
      const {
        repo,
        editLinks,
        docsDir = "",
        docsBranch = "master",
        docsRepo = repo,
      } = this.$site.themeConfig;

      let path = normalize(this.$page.path);
      if (endingSlashRE.test(path)) {
        path += "README.md";
      } else {
        path += ".md";
      }
      if (docsRepo && editLinks) {
        return this.createEditLink(repo, docsRepo, docsDir, docsBranch, path);
      }
    },

    editLinkText() {
      return (
        this.$themeLocaleConfig.editLinkText ||
        this.$site.themeConfig.editLinkText ||
        `Edit this page`
      );
    },
  },

  methods: {
    createEditLink(repo, docsRepo, docsDir, docsBranch, path) {
      const bitbucket = /bitbucket.org/;
      if (bitbucket.test(repo)) {
        const base = outboundRE.test(docsRepo) ? docsRepo : repo;
        return (
          base.replace(endingSlashRE, "") +
          `/${docsBranch}` +
          (docsDir ? "/" + docsDir.replace(endingSlashRE, "") : "") +
          path +
          `?mode=edit&spa=0&at=${docsBranch}&fileviewer=file-view-default`
        );
      }

      const base = outboundRE.test(docsRepo)
        ? docsRepo
        : `https://github.com/${docsRepo}`;

      return (
        base.replace(endingSlashRE, "") +
        `/edit/${docsBranch}/docs` +
        (docsDir ? "/" + docsDir.replace(endingSlashRE, "") : "") +
        path
      );
    },
  },
};

function resolvePrev(page, items) {
  return find(page, items, -1);
}

function resolveNext(page, items) {
  return find(page, items, 1);
}

function find(page, items, offset) {
  const res = [];
  items.forEach((item) => {
    if (item.type === "group") {
      res.push(...(item.children || []));
    } else {
      res.push(item);
    }
  });
  for (let i = 0; i < res.length; i++) {
    const cur = res[i];
    if (cur.type === "page" && cur.path === page.path) {
      return res[i + offset];
    }
  }
}
</script>

<style lang="stylus">
@import '../styles/config.styl'
@require '../styles/wrapper.styl'

.page-edit
  @extend $wrapper
  padding-top 0
  overflow auto
  .edit-link
    display inline-block
    a
      color lighten($textColor, 25%)
      margin-right 0.25rem
  .last-updated
    float right
    font-size 0.9em
    color #888
    font-style italic
    .prefix
      font-weight 500
      color lighten($textColor, 25%)
    .time
      font-weight 400
      color #aaa

.page-edit__inner {
  border-top: 1px solid $borderColor;
  padding-top: 1.5rem;
  display: flex;
  justify-content: space-between;
}

.page-nav
  @extend $wrapper
  padding-top 1rem
  padding-bottom 0
  .inner
    border-top 1px solid $borderColor
    min-height 2rem
    margin-top 0
    padding-top 1rem
    overflow auto // clear float
  .next
    float right
    line-height 2
  .prev
    line-height 2

@media (max-width: $MQMobile)
  .page-edit
    padding 0 2rem
    .edit-link
      margin-bottom .8rem
    .last-updated
      font-size 1rem
      float none
      text-align left
  .page-edit__inner
    display flex
    flex-direction column
  .last-updated
    order 1

.content.content-possibly-outdated {
  padding-bottom: 0 !important;
}

.content.after-content-possibly-outdated {
  > :first-child {
    margin-top: 0 !important;
  }

  > h1:first-child {
    margin-top: 0 !important;
    padding-top: 0 !important;
  }
}
</style>
