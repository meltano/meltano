<template>
  <main class="home">
    <div class="hero homepage-cta feature-section-wrapper" id="installation">
      <div class="hero-left">
        <Content class="theme-default-content" slot-key="installation" />

        <p class="action">
          <a
            :href="$frontmatter.installation.primaryAction.link"
            :title="$frontmatter.installation.primaryAction.text"
            class="nav-link action-button"
          >
            <img
              src="/meltano-logo-white.svg"
              width="25"
              height="25"
              style="vertical-align: text-bottom;"
            />
            {{ $frontmatter.installation.primaryAction.text }}
          </a>
          <SlackChannelLink class="action-button secondary">
            <SlackIcon /> Join us on Slack
          </SlackChannelLink>
          <a
            class="action-button secondary"
            href="https://gitlab.com/meltano/meltano"
            target="_blank"
          >
            <GitLabIcon />
            View code on GitLab
            <OutboundLink />
          </a>
        </p>
      </div>

      <div class="hero-right">
        <Content class="theme-default-content" slot-key="installation-code" />
      </div>
    </div>

    <div class="hero homepage-cta feature-section-wrapper" id="meltano-init">
      <div class="hero-left">
        <Content class="theme-default-content" slot-key="meltano-init" />

        <p class="action">
          <NavLink
            class="action-button"
            :item="$frontmatter.meltanoInit.primaryAction"
          />
        </p>
      </div>

      <div class="hero-right">
        <Content class="theme-default-content" slot-key="meltano-init-code" />
      </div>
    </div>

    <div class="hero homepage-cta feature-section-wrapper" id="integration">
      <div class="hero-left">
        <Content class="theme-default-content" slot-key="integration" />

        <p class="action">
          <NavLink
            class="action-button"
            :item="$frontmatter.integration.primaryAction"
          />
        </p>
      </div>

      <div class="hero-right">
        <Content class="theme-default-content" slot-key="integration-code" />
      </div>
    </div>

    <div class="hero homepage-cta feature-section-wrapper" id="transformation">
      <div class="hero-left">
        <Content class="theme-default-content" slot-key="transformation" />

        <p class="action">
          <NavLink
            class="action-button"
            :item="$frontmatter.transformation.primaryAction"
          />
        </p>
      </div>

      <div class="hero-right">
        <Content class="theme-default-content" slot-key="transformation-code" />
      </div>
    </div>

    <div class="hero homepage-cta feature-section-wrapper" id="orchestration">
      <div class="hero-left">
        <Content class="theme-default-content" slot-key="orchestration" />

        <p class="action">
          <NavLink
            class="action-button"
            :item="$frontmatter.orchestration.primaryAction"
          />
        </p>
      </div>

      <div class="hero-right">
        <Content class="theme-default-content" slot-key="orchestration-code" />

        <a
          href="https://airflow.apache.org/docs/stable/ui.html#dags-view"
          target="_blank"
        >
          <img
            class="screenshot"
            alt="Screenshot of Airflow Webserver"
            src="../assets/airflow-webserver.png"
          />
        </a>
      </div>
    </div>

    <div
      class="hero homepage-cta feature-section-wrapper"
      id="containerization"
    >
      <div class="hero-left">
        <Content class="theme-default-content" slot-key="containerization" />

        <p class="action">
          <NavLink
            class="action-button"
            :item="$frontmatter.containerization.primaryAction"
          />
        </p>
      </div>

      <div class="hero-right">
        <Content
          class="theme-default-content"
          slot-key="containerization-code"
        />
      </div>
    </div>

    <div class="feature-section-wrapper is-shorter is-white">
      <section class="section">
        <h2 class="section__title" style="padding-bottom: 20px;">
          Intrigued?
        </h2>

        <NavLink
          class="button is-filled"
          :item="$frontmatter.installation.primaryAction"
        />

        <p class="description ta-c">
          Or keep scrolling to learn more!
        </p>
      </section>
    </div>

    <div class="hero homepage-cta feature-section-wrapper" id="meltano-select">
      <div class="hero-left">
        <Content class="theme-default-content" slot-key="meltano-select" />

        <p class="action">
          <NavLink
            class="action-button"
            :item="$frontmatter.meltanoSelect.primaryAction"
          />
        </p>
      </div>

      <div class="hero-right">
        <Content class="theme-default-content" slot-key="meltano-select-code" />
      </div>
    </div>

    <div class="feature-section-wrapper is-shorter is-white">
      <section class="section">
        <h2 class="section__title" style="padding-bottom: 20px;">
          Stay up to date and get in touch
        </h2>
        <a
          :href="$site.themeConfig.data.slackChannelUrl"
          class="button"
          target="_blank"
          ><SlackIcon /> Slack</a
        >
        <a href="https://meltano.com/blog/" class="button" target="_blank"
          >Blog</a
        >
        <a href="https://twitter.com/meltanodata" class="button" target="_blank"
          ><TwitterIcon /> Twitter</a
        >
        <a href="https://www.youtube.com/meltano" class="button" target="_blank"
          >YouTube</a
        >
        <a
          href="https://gitlab.com/meltano/meltano"
          class="button"
          target="_blank"
          ><GitLabIcon /> Repo</a
        >

        <p class="description ta-c">
          If you're looking for help with a problem, check out
          <router-link to="/docs/getting-help.html">Getting Help</router-link>
        </p>
      </section>
    </div>

    <div class="feature-section-wrapper is-shorter">
      <section class="section">
        <h2 class="section__title">Subscribe to our newsletter</h2>
        <p class="section__text">
          Get the most significant news about Meltano delivered right to your
          inbox!
        </p>

        <a href="https://meltano.substack.com" class="button" target="_blank"
          >Subscribe</a
        >
      </section>
    </div>

    <GlobalFooter
      ><a
        href="https://gitlab.com/meltano/meltano/edit/master/docs/src/.vuepress/theme/views/Home.vue"
        target="_blank"
        >{{ $site.themeConfig.editLinkText }} <OutboundLink
      /></a>
    </GlobalFooter>
  </main>
</template>

<script>
import NavLink from "@theme/components/NavLink.vue";

export default {
  name: 'Home',

  components: { NavLink },

  computed: {
    data() {
      return this.$page.frontmatter;
    },
  },
};
</script>

<style lang="stylus">
.button {
  display: inline-block;
  font-size: 1.2rem;
  color: $accentColor;
  padding: 0.8rem 1.6rem 0.9rem;
  border-radius: 4px;
  transition: background-color 0.1s ease;
  background-color: white;
  box-sizing: border-box;
  border: 2px solid $accentColor;
  transition: all 0.2s ease-in;

  l, &:hover, &:focus, &.is-filled {
    color: #fff;
    background-color: $accentColor;
  }

  svg {
    vertical-align: text-top
  }
}

.quote {
  border-top: 1px solid #ddd;
  border-bottom: 0;
  text-align: center;
  padding-top: 5rem;
  display: block;
  margin-bottom: 1rem;
  font-weight: 400;
  font-size: 36px;
}

.description {
  margin-bottom: 0;
  font-size: 1.25rem;
  padding-left: 10%;
  padding-right: 10%;
  text-align: center;
  padding-top: 10px;
}

.meltano-stages-table {
  display: block;
  margin: 1rem auto 0rem;
  font-size: 14px;
  overflow: scroll;
  width: 100%;

  tr:nth-child(2n) {
    background-color: white;
  }
}

.meltano-header-row {
  height: 75px;
  background: #f6f6f6;

  th:first-child {
    background: #eee;
    text-align: left;
  }
}

.meltano-uses {
  background-color: #3e3c8e;
  width: 10%;
}

.meltano-uses-secondary {
  background-color: #5959a7;
}

.meltano-use-row {
  background-color: #3915c0;
  color: white;
  font-weight: bold;
  padding: 10px 0;
  height: 200px;
  text-align: center;

  a {
    color: white;
    font-weight: bold;

    &:hover {
      text-decoration: underline;
    }
  }

  td:first-child {
    background: #2A0F8D;
    text-align: left;
  }
}

.meltano-replace-row {
  font-size: 11px;

  td:first-child {
    background: #eee;
    font-weight: bold;
  }
}

.section {
  padding: 2rem 0;
  text-align: center;

  &__text {
    font-size: 1.4rem;
    margin-bottom: 1rem;
  }

  &__title {
    margin-top: 0;
    margin-bottom: 0;
    padding-bottom: 0;
    border-bottom: 0;
    font-size: 2rem;
  }

  .button {
    margin-bottom: 0.25rem;
  }
}

@media (min-width: $MQNarrow) {
  .section__text {
    max-width: 60%;
    margin: 1.5rem auto;
  }
}

.homepage-cta {
  display: flex;
  justify-content: center;
  flex-direction: column;
  align-items: center;
}

@media (min-width: $MQNarrow) {
  .homepage-cta {
    flex-direction: row;
    align-items: start;

    &:first-child {
      align-items: center;
    }
  }
}

.hero .theme-default-content {
  max-width: none !important;
  margin: 0 !important;
  padding: 0 !important;
}

.hero-left {
  max-width: 80%;
  text-align: left;
}

.hero-right {
  width: 100%;
}

.feature-section {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 0 30px;
}

.feature-section-wrapper {
  background-color: white;
  padding-top: 0rem;
  padding-bottom: 4rem;

  &.is-shorter {
    padding: 2rem 0;
  }

  &.is-white {
    background-color: #fff;
  }
}

.feature-left {
  max-width: 60%;
}

.feature-right {
  max-width: 60%;
}

@media (min-width: $MQNarrow) {
  .feature-section {
    display: flex;
    flex-direction: row;
    justify-content: center;
    align-items: center;
    max-width: $contentWidthWide;
    margin: 0 auto;
  }

  .feature-right {
    margin-left: 30px;
    text-align: left;
    max-width: 40%;
  }
}

.hero .theme-default-content {
  > :first-child {
    margin-top: 0 !important;
    margin-bottom: 0 !important;
  }

  div[class*='language-'] {
    margin-left: 0;
    margin-right: 0;
  }

  p, ul, ol {
    font-size: 1.2rem !important;
    color: #474C4F !important;
  }

  h1 {
    padding-top: 0 !important;
    padding-right: 40px !important;
    font-weight: 400 !important;
    font-size: 36px !important;
    color: #1D1D1D !important;
    margin: 0 !important;
  }

  h2 {
    margin: 0 !important;
    padding: 0 !important;
    border: none !important;
  }
}

.hero-right .theme-default-content ol {
  text-align: left;
  padding-left: 1.5rem;
}

@media (min-width: $MQNarrow) {
  .hero .theme-default-content h1 {
    font-size: 54px !important;
    text-align: left !important;
    padding-top: 0 !important;
    line-height: 1.2em !important;
  }

  .hero .theme-default-content h2 {
    font-size: 2rem !important;
  }

  .hero-left {
    width: 55%;
  }

  .hero-right {
    min-width: 400px;
    width: 35%;
  }

  .hero-left .theme-default-content {
    p, ul, ol {
      padding-right: 80px !important;
      padding-bottom: 10px;
    }
  }
}

.section-title {
  font-weight: bold;
  font-size: 32px;
  margin-top: 0;
}

.home {
  padding: $navbarHeight 0 0;
  margin: 0px auto;

  .hero {
    width: 100%;
    text-align: center;
    padding: 3rem 0;

    img {
      max-width: 100%;
    }

    img.screenshot {
      border: 3px solid #282c34;
      border-radius: 6px;
      max-width: calc(100% - 6px);
    }

    h1 {
      font-size: 3rem;
    }

    h1, .description, .action {
      margin: 1.8rem auto 0;
      text-align: left;
    }

    .description {
      max-width: 35rem;
      font-size: 1.6rem;
      line-height: 1.3;
      color: lighten($textColor, 40%);
    }
  }

  .action-button {
    display: inline-block;
    font-size: 1.2rem;
    font-weight: bold;
    color: #fff;
    background-color: $accentColor;
    padding: 0.8rem 1.6rem;
    border-radius: 4px;
    transition: background-color 0.2s ease;
    box-sizing: border-box;
    margin-right: 0.4rem;
    margin-bottom: 1rem;

    svg {
      color: #fff;

      &:not(.outbound) {
        vertical-align: text-top;
      }
    }

    img {
      vertical-align: text-top;
    }

    &.secondary {
      background: none;
      box-shadow: inset 0 0 0 2px $accentColor;
      color: $accentColor;

      svg {
        color: $accentColor;
      }

      &:hover {
        background-color: lighten($accentColor, 80%);
      }
    }

    &:hover {
      background-color: $accentHighlightColor;
    }
  }

  .features {
    border-top: 1px solid $borderColor;
    padding: 1.2rem 0;
    margin-top: 2.5rem;
    display: flex;
    flex-wrap: wrap;
    align-items: flex-start;
    align-content: stretch;
    justify-content: space-between;
  }

  .feature {
    flex-grow: 1;
    flex-basis: 30%;
    max-width: 30%;

    h2 {
      font-size: 1.4rem;
      font-weight: 500;
      border-bottom: none;
      padding-bottom: 0;
      color: lighten($textColor, 10%);
    }

    p {
      color: lighten($textColor, 25%);
    }
  }
}

@media (max-width: $MQMobile) {
  .home {
    .features {
      flex-direction: column;
    }

    .feature {
      max-width: 100%;
      padding: 0 2.5rem;
    }
  }
}

@media (min-width: $MQMobileNarrow) {
  .home {
    .hero {
      h1 {
        font-size: 2rem;
      }

      h1, .description, .action {
        margin: 1.2rem auto 0;
      }

      .description {
        font-size: 1.2rem;
      }
    }

    .action-button {
      font-size: 1.1rem;
      padding: 0.6rem 1.2rem;
    }

    .feature {
      h2 {
        font-size: 1.25rem;
      }
    }
  }
}

.mb0 {
  margin-bottom: 0;
}

.plugin-logos {
  display: grid;
  grid-template-columns: 1fr;
  grid-template-rows: minmax(120px, 1fr);
  grid-column-gap: 30px;
  grid-row-gap: 30px;
  align-items: center;
  justify-content: center;
  padding: 30px;

  a {
    margin: 0 auto;
  }

  img {
    max-width: 120px;
    margin: 0 auto;
    filter: grayscale(1);
    transition: filter 0.2s ease-in-out;

    &:hover {
      filter: grayscale(0);
    }
  }
}

@media (min-width: 425px) {
  .plugin-logos {
    grid-template-columns: 1fr 1fr 1fr;
  }
}

@media (min-width: 768px) {
  .plugin-logos {
    grid-template-columns: 1fr 1fr 1fr 1fr 1fr 1fr;

    img {
      max-width: 120px;
      margin: 0 auto;
    }
  }
}

.ta-c {
  text-align: center;
}

.carbon-intensity-logo {
  display: flex;
  align-items: center;
  justify-conent: center;
  font-size: 1.5rem;
  font-weight: bold;
}

.jump-in {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-conent: center;

  .jump-in-message {
    margin-bottom: 1.8rem;
  }

  .language-bash {
    padding-right: 1.5rem;
  }
}

.rich-media-container {
  margin: 0 10%;
}

.embed-responsive {
  position: relative;
  display: block;
  height: 0;
  padding: 0;
  overflow: hidden;

  .embed-responsive-item, iframe, embed, object, video {
    position: absolute;
    top: 0;
    bottom: 0;
    left: 0;
    width: 100%;
    height: 100%;
    border: 0;
  }
}

.embed-responsive-16by9 {
  padding-bottom: 56.25%;
}

.mt-2r {
  margin-top: 1rem;
}
</style>
