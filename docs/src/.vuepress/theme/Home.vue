<template>
  <div class="home">
    <div class="hero">
      <img
        v-if="data.heroImage"
        :src="$withBase(data.heroImage)"
        alt="hero"
      >
      <h1>{{ data.heroText || $title || 'Hello' }}</h1>

      <p class="description">
        {{ data.tagline || $description || 'Welcome to your VuePress site' }}
      </p>

      <p
        class="action"
        v-if="data.actionText && data.actionLink"
      >
        <NavLink
          class="action-button"
          :item="actionLink"
        />
      </p>
    </div>

    <div
      class="features"
      v-if="data.features && data.features.length"
    >
      <div
        class="feature"
        v-for="(feature, index) in data.features"
        :key="index"
      >
        <h2>{{ feature.title }}</h2>
        <p>{{ feature.details }}</p>
      </div>
    </div>

    <h2 class="quote">Meltano does for data what docker did for containers</h2>

    <p class="description">From loading your data to generating beautiful reports for analysis, Meltano leverages best practices from software devlopment such as version control, continuous integration and deploymeent, and a powerful command line interface so you can focus on your data.</p>

    <table class="meltano-stages-table">
      <thead>
        <tr>
          <th><span class="sr-only">Description</span></th>
          <th>Model</th>
          <th>Extract</th>
          <th>Load</th>
          <th>Transform</th>
          <th>Analyze</th>
          <th>Notebok</th>
          <th>Orchestrate</th>
        </tr>
      </thead>
      <tbody>
        <tr class="meltano-row">
          <td>Meltano is a single workflow for the entire data life cycle.</td>
          <td class="ta-c">
            <a href="https://meltano.com/docs/architecture.html#meltano-model" target="_blank">Meltano Model</a>
          </td>
          <td class="ta-c">
            <a href="https://meltano.com/docs/taps-targets.html#tap">Singer Tap</a>
          </td>
          <td class="ta-c">
            <a href="https://meltano.com/docs/taps-targets.html#target">Singer Target</a>
          </td>
          <td class="ta-c">
            <a href="https://www.getdbt.com/">dbt</a>
          </td>
          <td class="ta-c">
            <a href="https://meltano.com/docs/architecture.html#meltano-analyze">Meltano Analyze</a>
          </td>
          <td class="ta-c">
            <a href="https://github.com/jupyterhub/jupyterhub">JupyterHub</a>
          </td>
          <td class="ta-c">
            <a href="https://docs.gitlab.com/ee/ci/">GitLab CI</a> /  <a href="https://airflow.apache.org/">Airflow</a>
          </td>
        </tr>
        <tr>
          <td>Meltano can replace</td>
          <td>
            <ul>
              <li>
                <a href="http://www.modelsphere.com/org/">Open ModelSphere</a>
              </li>
              <li>
                <a href="https://looker.com/platform/data-modeling">LookML</a>
              </li>
              <li>
                <a href="http://www.stephenlevin.co/data-modeling-layer-startup-analytics-dbt-vs-matillion-vs-lookml/">Matillion</a>
              </li>
            </ul>
          </td>
          <td>
            <ul>
              <li>
                <a href="http://www.pentaho.com/product/data-integration">Pentaho DI</a>
              </li>
              <li>
                <a href="https://www.talend.com/">Talend</a>
              </li>
              <li>
                <a href="https://www.alooma.com/">Alooma</a></li>
              <li>
                <a href="https://fivetran.com/">Fivetran</a>
              </li>
            </ul>
          </td>
          <td>
            <ul>
              <li>
                <a href="http://www.pentaho.com/product/data-integration">Pentaho DI</a>
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
                <a href="https://meltano.com/docs/best-practices.html#stored-procedures">Stored procedures</a>
              </li>
              <li>
                <a href="http://www.pentaho.com/product/data-integration">Pentaho DI</a>
              </li>
              <li>
                <a href="https://www.alooma.com/">Alooma</a>
              </li>
            </ul>
          </td>
          <td>
            <ul>
              <li>
                <a href="https://www.metabase.com/">Metabase</a>
              </li>
              <li>
                <a href="https://looker.com/">Looker</a>
              </li>
              <li>
                <a href="https://www.periscopedata.com/">Periscope</a>
              </li>
            </ul>
          </td>
          <td>
            <ul>
              <li>
                <a href="https://www.gnu.org/software/octave/">GNU Octave</a>
              </li>
              <li>
                <a href="https://www.nurtch.com/">Nurtch</a>
              </li>
              <li>
                <a href="https://www.datadoghq.com/blog/data-driven-notebooks/">Datadog Notebooks</a>
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

    <section class="hiring">
      <h2 class="hiring__title">We're Hiring!</h2>
      <p class="hiring__text">Want to help create a new product and make an impact in the world of data? We are currently looking for a <a href="https://boards.greenhouse.io/gitlab/jobs/4059274002">General Manager</a> and a <a href="https://boards.greenhouse.io/gitlab/jobs/4059265002">Senior Product Manager</a>. </p> 
    </section>

    <div
      class="footer"
    >
      <a href="https://gitlab.com/meltano/meltano/edit/master/docs/src/README.md" target="_blank">Edit this page</a>
    </div>
  </div>
</template>

<script>
import NavLink from './NavLink.vue'

export default {
  components: { NavLink },

  computed: {
    data () {
      return this.$page.frontmatter
    },

    actionLink () {
      return {
        link: this.data.actionLink,
        text: this.data.actionText
      }
    }
  }
}
</script>

<style lang="stylus">
@import './styles/config.styl'

.quote {
  border-top: 1px solid #ddd;
  border-bottom: 0;
  font-size: 2.4rem;
  text-align: center;
  margin-top: 5rem;
  padding-top: 5rem;
  display: block;
  margin-bottom: 1rem;
}

.description {
  font-size: 1.4rem;
  margin-bottom: 0;
}

.meltano-stages-table {
  display: block;
  margin: 2.5rem auto 7rem;

  tr:nth-child(2n) {
    background-color: white;
  }
}

.meltano-row {
  background-color: #3915c0;
  color: white;
  font-weight: bold;
  padding: 10px 0;
  height: 200px;

  a {
    color: white;
    font-weight: bold;

    &:hover {
      text-decoration: underline;
    }
  }
}

.ta-c { 
  text-align: center;
}

.hiring {
  border-top: 1px solid #eaecef;
  padding: 2rem 0 2.5rem;
  text-align: center;

  &__text {
    font-size: 1.4rem;
    margin-bottom: 0.82rem;
  }

  &__title {
    margin-bottom: 0;
    padding-bottom: 0;
    border-bottom: 0;
    font-size: 2rem;
  }
}

@media (min-width: $MQNarrow) {
  .hiring__text {
    max-width: 60%;
    margin: 1rem auto;
  }
}

.home
  padding $navbarHeight 2rem 0
  max-width 1080px
  margin 0px auto
  .hero
    text-align center
    img
      max-height 280px
      display block
      margin 3rem auto 1.5rem
    h1
      font-size 3rem
    h1, .description, .action
      margin 1.8rem auto
    .description
      max-width 35rem
      font-size 1.6rem
      line-height 1.3
      color lighten($textColor, 40%)
    .action-button
      display inline-block
      font-size 1.2rem
      color #fff
      background-color $accentColor
      padding 0.8rem 1.6rem
      border-radius 4px
      transition background-color .1s ease
      box-sizing border-box
      border-bottom 1px solid darken($accentColor, 10%)
      &:hover
        background-color lighten($accentColor, 10%)
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
  .footer
    padding 2.5rem
    border-top 1px solid $borderColor
    text-align center
    color lighten($textColor, 25%)

@media (max-width: $MQMobile)
  .home
    .features
      flex-direction column
    .feature
      max-width 100%
      padding 0 2.5rem

@media (max-width: $MQMobileNarrow)
  .home
    padding-left 1.5rem
    padding-right 1.5rem
    .hero
      img
        max-height 210px
        margin 2rem auto 1.2rem
      h1
        font-size 2rem
      h1, .description, .action
        margin 1.2rem auto
      .description
        font-size 1.2rem
      .action-button
        font-size 1rem
        padding 0.6rem 1.2rem
    .feature
      h2
        font-size 1.25rem
</style>
