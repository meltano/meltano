<template>
  <div class="home" style="background:#e5e4e2; max-width:none; padding-right:0px;">
    <div class="hero">
    
      <div style="float:left; text-align:left; width:60%;">
        <h1 style="font-size: 36px; text-align: left; padding-top: 20px; padding-left: 35px; font-weight:400;">Open source data dashboarding software</h1>
        <p style="padding-left:35px;">Meltano is a free alternative to expensive SaaS tools for building automated business dashboards. Our platform powers end-to-end workflows with tools for modeling, extracting, loading, transforming, analyzing, notebooking, and orchestrating your data.</p> 
      </div>

      <div style="float:right; text-align:left; width:40%;">
         <img style="float:right;" src="https://media.istockphoto.com/vectors/young-freelancer-working-at-home-flat-editable-vector-illustration-vector-id827691618?" />
      </div>
      

      <p style="text-align: left; padding-left: 35px; padding-top:20px;"
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

    <h2 class="quote">Meltano is built so you can use the extractors and loaders that work for your data and your team.</h2>

    <p class="description">One of the hardest steps of getting insight from your data is standardizing it so you can actually analyze it. Check out all the extractors and/or loaders we currently support (and there is more to come):</p>

    <div class="el-logos">
      <img src="../assets/gitlab-logo.png" alt="GitLab Logo">
      <img src="../assets/stripe-logo.png" alt="Stripe Logo">
      <img src="../assets/csv-logo.png" alt="CSV Logo">
      <img src="../assets/salesforce-logo.png" alt="Salesforce Logo">
      <img src="../assets/sqlite-logo.png" alt="SQLite Logo">
      <img src="../assets/zendesk-logo.png" alt="Zendesk Logo">
      <img src="../assets/zuora-logo.png" alt="Zuora Logo">
      <img src="../assets/marketo-logo.png" alt="Marketo Logo">
      <div class="carbon-intensity-logo">
        <img src="../assets/carbon-intensity-logo.png" alt="Carbon Intensity Favicon">
        Carbon Intensity API
      </div>
      <img src="../assets/fastly-logo.png" alt="Fastly Logo">
      <img src="../assets/mongodb-logo.png" alt="MongoDB Logo">
      <img src="../assets/snowflake-logo.png" alt="Snowflake Logo">
    </div>

    <p class="description ta-c">For more information, check out our <a href="/docs/plugins.html">plugins documentation</a></p>

    <p class="description"></p>

    <h2 class="quote">Test Meltano does for data what Docker did for containers</h2>

    <p class="description">Meltano is a single workflow for the entire data life cycle. From loading your data to generating beautiful reports for analysis, Meltano leverages best practices from software development such as version control, continuous integration and deployment, and a powerful command line interface so you can focus on your data.</p>

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
          <td>Meltano uses:</td>
          <td>
            <a href="https://meltano.com/docs/architecture.html#meltano-model" target="_blank">Meltano Model</a>
          </td>
          <td>
            <a href="https://www.singer.io/#taps">Singer Taps</a>
          </td>
          <td>
            <a href="https://www.singer.io/#targets">Singer Targets</a>
          </td>
          <td>
            <a href="https://www.getdbt.com/">dbt</a>
          </td>
          <td>
            <a href="https://meltano.com/docs/architecture.html#meltano-ui">Meltano UI</a>
          </td>
          <td>
            <a href="https://github.com/jupyterhub/jupyterhub">JupyterHub</a>
          </td>
          <td>
            <a href="https://airflow.apache.org/">Airflow</a>
          </td>
        </tr>
        <tr class="meltano-replace-row">
          <td>Meltano can be an alternative to:</td>
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

    <section class="section">
      <h2 class="section__title">Communicate with the team!</h2>
      <p class="section__text">Got questions or want to chat with the team? You can find us in the Meltano Slack channel, watch our videos on YouTube, or use another preferred channel.</p>
      <a href="https://join.slack.com/t/meltano/shared_invite/enQtNTM2NjEzNDY2MDgyLWI1N2EyZjA1N2FiNDBlNDE2OTg4YmI1N2I3OWVjOWI2MzIyYmJmMDQwMTY2MmUwZjNkMTBiYzhiZTI2M2IxMDc" class="button" target="_blank">Meltano Slack</a>
      <a href="https://www.youtube.com/meltano" class="button" target="_blank">Meltano YouTube</a>
      <a href="https://twitter.com/meltanodata" class="button" target="_blank">Twitter</a>
      <a href="https://meltano.com/blog/" class="button" target="_blank">Blog</a>
      <a href="https://gitlab.com/meltano/meltano" class="button" target="_blank">Repo</a>
    </section>

    <section class="section">
      <h2 class="section__title">Sign up for our newsletter!</h2>
      <p class="section__text">Get the latest updates on Meltano delivered right to your inbox! We will only use your email to provide you with updates and will never sell your information!</p>
      <a href="https://docs.google.com/forms/d/e/1FAIpQLSdyiKeMwO2qB4hJZnjBhVExBZwPATgz6_QTJjXKLiTNPmhW9w/viewform?usp=sf_link" class="button" target="_blank">Subscribe</a>
    </section>

    <div
      class="footer"
    >
      <a href="https://gitlab.com/meltano/meltano/edit/master/docs/src/.vuepress/theme/views/Home.vue" target="_blank">Edit this page</a>
    </div>
  </div>
</template>

<script>
import NavLink from '../components/NavLink.vue'

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
@import '../styles/config.styl'

.button {
    display: inline-block;
    font-size: 1.2rem;
    color: $accentColor;
    padding: 0.8rem 1.6rem 0.9rem;
    border-radius: 4px;
    transition: background-color 0.1s ease;
    box-sizing: border-box;
    border: 2px solid $accentColor;
    transition: all 0.2s ease-in;l

    &:hover,
    &:focus {
      color: #fff;
      background-color: $accentColor;
    }
}

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

.meltano-header-row {
  height: 75px;

  th:first-child {
    background: #eee;
    //width: 80px;
    text-align: left;
  }
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
  td:first-child {
    background: #eee;
    font-weight: bold;
  }
}

.section {
  border-top: 1px solid #eaecef;
  padding: 2.5rem 0;
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

.mb0 {
  margin-bottom: 0;
}

.el-logos {
  display: grid;
  grid-template-columns: 1fr 1fr 1fr;
  grid-column-gap: 30px;
  grid-template-rows: repeat(4, 150px);
  align-items: center;
  justify-content: center;
  grid-row-gap: 30px;
  text-align: center;
  padding: 30px;

  img {
    max-width: 200px;
    margin: 0 auto;
  }
}

.el-logos {
  display: grid;
  grid-template-columns: 1fr;
  grid-template-rows: minmax(120px, 1fr);
  grid-column-gap: 30px;
  grid-row-gap: 30px;
  align-items: center;
  justify-content: center;
  padding: 30px;
}


@media (min-width: 425px) {
  .el-logos {
    grid-template-columns: 1fr 1fr;
  }
}

@media (min-width: 768px) {
  .el-logos {
    grid-template-columns: 1fr 1fr 1fr;

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
</style>
