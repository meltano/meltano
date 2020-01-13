<template>
  <div class="home">
    <div>
      <div class="hero homepage-cta feature-section-wrapper">
        <div class="hero-left">
          <h2 class="hero-header" style="border-bottom:0px;">
            Data dashboards<br /><strong>for startup founders</strong>
          </h2>
          <p class="hero-tagline">
            Analytics software to visualize your business operations
          </p>

          <p class="action">
            <NavLink class="action-button" :item="$frontmatter.primaryAction" />
            <NavLink
              class="action-button secondary"
              :item="$frontmatter.secondaryAction"
            />
          </p>
        </div>

        <div class="hero-right">
          <img
            src="../assets/meltano-founder.jpg"
            alt="Happy Meltano User Says Hi"
            width="500px"
          />
        </div>
      </div>
    </div>

    <div class="feature-section-wrapper">
      <div
        class="content-width-wide"
        style="background-color:#fffbe4; padding-top:20px; padding-bottom:20px;"
      >
        <p class="description">
          Connect to data from popular services to build powerful dashboards
        </p>

        <div class="plugin-logos">
          <a href="/plugins/extractors/stripe.html"
            ><img src="../assets/logo-stripe.png" alt="Stripe Logo"
          /></a>

          <a href="/plugins/extractors/salesforce.html"
            ><img src="../assets/logo-salesforce.png" alt="Salesforce Logo"
          /></a>

          <a href="/plugins/extractors/zendesk.html"
            ><img src="../assets/logo-zendesk.png" alt="Zendesk Logo"
          /></a>

          <a href="/plugins/extractors/google-analytics.html"
            ><img
              src="../assets/logo-googleanalytics.png"
              alt="Google Analytics Logo"
            />
          </a>
        </div>

        <p class="description ta-c">
          For more information, check out our
          <a href="/plugins/extractors/">plugins documentation</a>
        </p>

        <p style="text-align:center; font-size:12px;">
          <em
            >All trademarks and logos are owned by their respective owners.</em
          >
        </p>
      </div>
    </div>

    <div class="features" v-if="data.features && data.features.length">
      <div
        class="feature"
        v-for="(feature, index) in data.features"
        :key="index"
      >
        <h2>{{ feature.title }}</h2>
        <p>{{ feature.details }}</p>
      </div>
    </div>

    <div class="feature-section-wrapper is-white">
      <div class="feature-section">
        <div class="feature-left">
          <img
            style="max-width: 100%; margin: 0 auto; display: block;"
            src="/screenshots/meltano-queries.png"
            alt="Screenshot of Meltano Analyze page"
          />
        </div>
        <div class="feature-right">
          <h2 class="section-title">
            No queries required
          </h2>
          <p class="hero-tagline">
            Go from data to dashboard in minutes, without writing any code.
          </p>
        </div>
      </div>
    </div>

    <div class="feature-section-wrapper">
      <div class="content-width-wide">
        <h2 class="section-title" style="text-align: center; margin-top: 0;">
          A single workflow for the entire data life cycle.
        </h2>

        <div class="rich-media-container">
          <div class="embed-responsive embed-responsive-16by9">
            <iframe
              class="embed-responsive-item"
              src="https://www.youtube.com/embed/2Glsf89WQ5w"
              frameborder="0"
              allow="accelerometer; autoplay; encrypted-media; gyroscope; picture-in-picture"
              allowfullscreen
            ></iframe>
          </div>
        </div>

        <p class="description">
          Meltano leverages best practices from software development such as
          version control, continuous integration and deployment, and a powerful
          command line interface so you can focus on your data.
        </p>

        <table class="meltano-stages-table">
          <thead>
            <tr class="meltano-header-row">
              <th>Stage:</th>
              <th>Model</th>
              <th>Extract</th>
              <th>Load</th>
              <th>Transform</th>
              <th>Analyze</th>
              <th>Notebook</th>
              <th>Orchestrate</th>
            </tr>
          </thead>
          <tbody>
            <tr class="meltano-use-row">
              <td class="meltano-uses">Meltano uses:</td>
              <td class="meltano-uses-secondary">
                <a
                  href="https://meltano.com/docs/architecture.html#meltano-model"
                  target="_blank"
                  >Meltano Model</a
                >
              </td>
              <td class="meltano-uses-secondary">
                <a href="https://www.singer.io/#taps">Singer Taps</a>
              </td>
              <td class="meltano-uses-secondary">
                <a href="https://www.singer.io/#targets">Singer Targets</a>
              </td>
              <td class="meltano-uses-secondary">
                <a href="https://www.getdbt.com/">dbt</a>
              </td>
              <td class="meltano-uses-secondary">
                <a href="https://meltano.com/docs/architecture.html#meltano-ui"
                  >Meltano UI</a
                >
              </td>
              <td class="meltano-uses-secondary">
                <a href="https://github.com/jupyterhub/jupyterhub"
                  >Jupyter Notebooks</a
                >
              </td>
              <td class="meltano-uses-secondary">
                <a href="https://airflow.apache.org/">Apache Airflow</a>
              </td>
            </tr>
            <tr class="meltano-replace-row">
              <td>Meltano can be an alternative to:</td>
              <td>
                <ul>
                  <li>
                    <a href="http://www.modelsphere.com/org/"
                      >Open ModelSphere</a
                    >
                  </li>
                  <li>
                    <a href="https://looker.com/platform/data-modeling"
                      >LookML</a
                    >
                  </li>
                  <li>
                    <a
                      href="http://www.stephenlevin.co/data-modeling-layer-startup-analytics-dbt-vs-matillion-vs-lookml/"
                      >Matillion</a
                    >
                  </li>
                </ul>
              </td>
              <td>
                <ul>
                  <li>
                    <a href="http://www.pentaho.com/product/data-integration"
                      >Pentaho DI</a
                    >
                  </li>
                  <li>
                    <a href="https://www.talend.com/">Talend</a>
                  </li>
                  <li>
                    <a href="https://www.alooma.com/">Alooma</a>
                  </li>
                  <li>
                    <a href="https://fivetran.com/">Fivetran</a>
                  </li>
                </ul>
              </td>
              <td>
                <ul>
                  <li>
                    <a href="http://www.pentaho.com/product/data-integration"
                      >Pentaho DI</a
                    >
                  </li>
                  <li>
                    <a href="https://www.talend.com/">Talend</a>
                  </li>
                  <li>
                    <a href="https://www.alooma.com/">Alooma</a>
                  </li>
                  <li>
                    <a href="https://fivetran.com/">Fivetran</a>
                  </li>
                </ul>
              </td>
              <td>
                <ul>
                  <li>
                    <a
                      href="https://meltano.com/docs/best-practices.html#stored-procedures"
                      >Stored procedures</a
                    >
                  </li>
                  <li>
                    <a href="http://www.pentaho.com/product/data-integration"
                      >Pentaho DI</a
                    >
                  </li>
                  <li>
                    <a href="https://www.alooma.com/">Alooma</a>
                  </li>
                </ul>
              </td>
              <td>
                <ul>
                  <li>
                    <a href="https://www.tableau.com/">Tableau</a>
                  </li>
                  <li>
                    <a href="https://www.metabase.com/">Metabase</a>
                  </li>
                  <li>
                    <a href="https://looker.com/">Looker</a>
                  </li>
                  <li>
                    <a href="https://www.periscopedata.com/">Periscope</a>
                  </li>
                  <li>
                    <a href="https://redash.io/">Redash</a>
                  </li>
                </ul>
              </td>
              <td>
                <ul>
                  <li>
                    <a href="https://www.gnu.org/software/octave/"
                      >GNU Octave</a
                    >
                  </li>
                  <li>
                    <a href="https://www.nurtch.com/">Nurtch</a>
                  </li>
                  <li>
                    <a
                      href="https://www.datadoghq.com/blog/data-driven-notebooks/"
                      >Datadog Notebooks</a
                    >
                  </li>
                </ul>
              </td>
              <td>
                <ul>
                  <li>
                    <a href="https://github.com/spotify/luigi">Luigi</a>
                  </li>
                  <li>
                    <a href="https://nifi.apache.org/">Nifi</a>
                  </li>
                  <li>
                    <a href="https://fivetran.com/">Fivetran</a>
                  </li>
                </ul>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <div class="feature-section-wrapper is-white">
      <div class="content-width-wide">
        <h2 class="section-title ta-c">See Meltano in action!</h2>
        <div class="rich-media-container">
          <div class="embed-responsive embed-responsive-16by9">
            <iframe
              class="embed-responsive-item"
              src="https://www.youtube.com/embed/vtNStRP5m_Y"
              frameborder="0"
              allow="accelerometer; autoplay; encrypted-media; gyroscope; picture-in-picture"
              allowfullscreen
            ></iframe>
          </div>
        </div>
      </div>
    </div>

    <div class="feature-section-wrapper is-white">
      <div class="content-width-wide">
        <h2 class="section-title ta-c">What People Are Saying</h2>

        <p class="description">
          <em
            >“The Meltano project out of GitLab is stitching together fragmented
            open-source data analytics projects into a single end-to-end
            platform. Meltano describes itself as ‘an open source
            convention-over-configuration product for the whole data lifecycle,
            all the way from loading data to analyzing it.’ Based on the success
            that GitLab has had with other projects, we predict that Meltano
            could eventually give the big, proprietary platforms a run for their
            money.”</em
          >
          --
          <a
            href="https://www.hashpath.com/2019/06/google-cloud-looker-snowflake/"
            >Hashpath Consulting</a
          >
        </p>
      </div>
    </div>

    <div class="feature-section-wrapper">
      <h2 class="section-title" style="text-align: center; margin-top: 0;">
        Self Host Meltano Locally or in the Cloud
      </h2>
      <p style="text-align: center; margin-bottom:20px;">
        Meltano is built to run wherever you get your work done. Looking to self
        host?
        <a href="/docs/installation.html"
          >Check out our installation instructions</a
        >.
      </p>

      <div class="rich-media-container">
        <div class="embed-responsive embed-responsive-16by9">
          <iframe
            width="560"
            height="315"
            src="https://www.youtube.com/embed/tf_EIbwDmXk"
            frameborder="0"
            allow="accelerometer; autoplay; encrypted-media; gyroscope; picture-in-picture"
            allowfullscreen
          ></iframe>
        </div>
      </div>
    </div>

    <div class="feature-section-wrapper is-shorter is-white">
      <section class="section">
        <h2 class="section__title" style="padding-bottom:20px;">
          We'd Love to Hear From You
        </h2>
        <a
          :href="$site.themeConfig.data.slackChannelUrl"
          class="button"
          target="_blank"
          >Slack</a
        >
        <a href="https://www.youtube.com/meltano" class="button" target="_blank"
          >YouTube</a
        >
        <a href="https://twitter.com/meltanodata" class="button" target="_blank"
          >Twitter</a
        >
        <a href="https://meltano.com/blog/" class="button" target="_blank"
          >Blog</a
        >
        <a
          href="https://gitlab.com/meltano/meltano"
          class="button"
          target="_blank"
          >Repo</a
        >

        <p class="description ta-c">
          If you're looking for help with a problem, check out
          <a href="/docs/getting-help.html">Getting Help</a>
        </p>
      </section>
    </div>

    <div class="feature-section-wrapper is-shorter">
      <div class="content-width-wide">
        <section class="section">
          <h2 class="section__title">Sign up for our newsletter!</h2>
          <p class="section__text">
            Get the latest updates on Meltano delivered right to your inbox! We
            will only use your email to provide you with updates and will never
            sell your information!
          </p>
          <a href="https://meltano.substack.com" class="button" target="_blank"
            >Subscribe</a
          >
        </section>
      </div>
    </div>

    <GlobalFooter
      ><a
        href="https://gitlab.com/meltano/meltano/edit/master/docs/src/.vuepress/theme/views/Home.vue"
        target="_blank"
        >{{ $site.themeConfig.editLinkText }} <OutboundLink
      /></a>
    </GlobalFooter>
  </div>
</template>

<script>
import NavLink from '../components/NavLink.vue'

export default {
  components: { NavLink },

  computed: {
    data() {
      return this.$page.frontmatter
    }
  }
}
</script>

<style lang="stylus">
@import '../styles/config.styl'

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
    transition: all 0.2s ease-in;l

    &:hover,
    &:focus {
      color: #fff;
      background-color: $accentColor;
    }

    &.is-purple.is-filled {
      background-color: $purpleColor;
      border-color: $purpleColor;
      color: white;
    }
}

.quote {
  border-top: 1px solid #ddd;
  border-bottom: 0;
  text-align: center;
  padding-top: 5rem;
  display: block;
  margin-bottom: 1rem;
  font-weight:400;
  font-size:36px;
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
  font-size:14px;
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
  background-color:#3e3c8e;
  width:10%;
}

.meltano-uses-secondary {
  background-color:#5959a7;
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
  font-size:11px;
  td:first-child {
    background: #eee;
    font-weight: bold;
  }
}

.section {
  padding: 6rem 0;
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
    margin-bottom: .25rem;
  }
}

@media (min-width: $MQNarrow) {
  .section__text {
    max-width: 60%;
    margin: 1.5rem auto;
  }
}

.homepage-cta {
  min-height: 500px;
  display: flex;
  justify-content: center;
  align-items: center;
  flex-direction: column-reverse;
}

@media (min-width: $MQNarrow) {
  .homepage-cta {
    flex-direction: row;
  }
}

.hero-left {
  max-width: 80%;
  text-align: left;
}

.feature-section {
  display: flex;
  flex-direction: column;
  align-items: center;
}

.feature-section-wrapper {
  background-color: white;
  padding-top: 0rem;
  padding-bottom: 4rem;

  &.is-shorter {
    padding: 3rem 0;
  }

  &.is-white {
    background-color: #fff;
  }
}

.feature-left {
  max-width: 80%;
}

.feature-right {
  max-width: 80%;
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

  .feature-left {
    padding-left: 30px;
  }

  .feature-right {
    margin-left: 30px;
    text-align: left;
    max-width: 40%;
  }
}

.hero-tagline {
  font-size: 1.2rem;
  padding-right: 20px;
  padding-bottom: 10px;
  color: #474C4F;
}

.hero-header {
  padding-right: 40px;
  font-weight: 400;
  font-size: 36px;
  color: #1D1D1D;
  margin: 0;
}

@media (min-width: $MQNarrow) {
  .hero-header {
    font-size: 54px;
    text-align: left;
    padding-top: 40px;
    line-height: 1.2em;
  }
  .hero-left {
    max-width: 50%;
  }
  .hero-tagline {
    padding-right: 80px;
  }
}

.section-title {
  font-weight: bold;
  font-size: 32px;
  margin-top: 0;
}

.home
  padding $navbarHeight 0 0
  margin 0px auto
  .hero
    width 100%
    text-align center
    padding 0 0 4rem
    img
      max-width 100%
    h1
      font-size 3rem
    h1, .description, .action
      margin 1.8rem auto 0
      text-align: left;
    .description
      max-width 35rem
      font-size 1.6rem
      line-height 1.3
      color lighten($textColor, 40%)
    .action-button
      display inline-block
      font-size 1.2rem
      font-weight bold
      color #fff
      background-color #464ACB;
      padding 0.8rem 1.6rem
      border-radius 4px
      transition background-color .2s ease
      letter-spacing 0.1rem
      box-sizing border-box
      margin-right: 0.4rem;
      margin-bottom: 1rem;
      &.secondary
        background none
        box-shadow inset 0 0 0 2px #464ACB
        color #464ACB
        &:hover
          background-color lighten(#464ACB, 80%)
      &:hover
        background-color lighten(#464ACB, 10%)

  .features
    border-top 1px solid $borderColor
    padding 1.2rem 0
    margin-top 2.5rem
    display flex
    flex-wrap wrap
    align-items flex-start
    align-content stretch
    justify-content space-between
  .feature
    flex-grow 1
    flex-basis 30%
    max-width 30%
    h2
      font-size 1.4rem
      font-weight 500
      border-bottom none
      padding-bottom 0
      color lighten($textColor, 10%)
    p
      color lighten($textColor, 25%)

@media (max-width: $MQMobile)
  .home
    .features
      flex-direction column
    .feature
      max-width 100%
      padding 0 2.5rem

@media (min-width: $MQMobileNarrow)
  .home
    .hero
      img
        max-height 480px
        display block
        margin-right: -33px
      h1
        font-size 2rem
      h1, .description, .action
        margin 1.2rem auto 0
      .description
        font-size 1.2rem
      .action-button
        font-size 1rem
        padding 0.6rem 1.2rem
    .feature
      h2
        font-size 1.25rem

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
    max-width: 200px;
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
    grid-template-columns: 1fr 1fr;
  }
}

@media (min-width: 768px) {
  .plugin-logos {
    grid-template-columns: 1fr 1fr 1fr 1fr;

    img {
      max-width: 200px;
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

  .embed-responsive-item,
  iframe,
  embed,
  object,
  video {
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
