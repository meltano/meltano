<script>
export default {
  name: 'TutorialTable'
}
</script>

<template>
  <div class="tutorial-container">
    <div class="tutorial-item">
      <h2 class="tutorial-header">Table of Contents</h2>
    </div>
    <div class="tutorial-item">
      <div class="tutorial-header">
        <a href="/docs/getting-started.html">Carbon Emissions + SQLite</a>
      </div>
      <div>
        <p>
          Experience a taste of data extraction and loading using Meltano CLI
          followed by analysis using Meltano UI with its automatic SQL
          generation.
        </p>
        <ul>
          <li>SQLite database</li>
          <li>No authentication</li>
          <li>Public carbon emissions dataset</li>
        </ul>
      </div>
    </div>
    <div class="tutorial-item">
      <div class="tutorial-header">
        <a href="/tutorials/gitlab-and-postgres.html">GitLab API + Postgres</a>
      </div>
      <div>
        <p>
          Experience the full extract, load, and transform pipeline with
          authentication using Meltano CLI followed by analysis using Meltano UI
          with its automatic SQL generation.
        </p>
        <ul>
          <li>Postgres database</li>
          <li>Authentication</li>
          <li>Your private GitLab dataset</li>
        </ul>
      </div>
    </div>
    <div class="tutorial-item">
      <div class="tutorial-header">
        <a href="/tutorials/google-analytics-with-postgres.html">
          Google Analytics API + Postgres
        </a>
      </div>
      <div>
        <p>
          Experience the full extract, load, and transform pipeline with
          authentication using Meltano CLI followed by analysis using Meltano UI
          with its automatic SQL generation.
        </p>
        <ul>
          <li>Postgres database</li>
          <li>Authentication</li>
          <li>Your private Google Analytics dataset</li>
        </ul>
      </div>
    </div>
    <div class="tutorial-item">
      <div class="tutorial-header">
        <a href="/tutorials/salesforce-and-postgres.html"
          >Salesforce API + Postgres</a
        >
      </div>
      <div>
        <p>
          Experience the full extract, load, and transform pipeline with
          authentication using Meltano CLI followed by analysis using Meltano UI
          with its automatic SQL generation.
        </p>
        <ul>
          <li>Postgres database</li>
          <li>Authentication</li>
          <li>Your private Salesforce dataset</li>
        </ul>
      </div>
    </div>
    <div class="tutorial-item">
      <div class="tutorial-header">
        <a href="/tutorials/create-custom-transforms-and-models.html">
          Create Custom Transformations and Models
        </a>
      </div>
      <div>
        <p>Experience building custom transforms and models.</p>
        <ul>
          <li>Postgres database</li>
          <li>Authentication</li>
          <li>Your private Salesforce dataset</li>
          <li>Custom transforms</li>
          <li>Custom models</li>
        </ul>
      </div>
    </div>
    <div class="tutorial-item">
      <div class="tutorial-header">
        <a href="/tutorials/postgres-with-postgres.html">
          Use Postgres as a Loader and Extractor
        </a>
      </div>
      <div>
        <p>
          Learn how to run <code>tap-postgres</code> with
          <code>target-postgres</code> in Meltano.
        </p>
      </div>
    </div>
    <div class="tutorial-item">
      <div class="tutorial-header">
        <a href="/tutorials/csv-with-postgres.html">
          Loading CSV files into a Postgres Database
        </a>
      </div>
      <div>
        <p>
          Learn how to load data stored in multiple CSV files to a Postgres
          Database and then use Custom Transforms and Models to combine them
          together and analyze the results.
        </p>
      </div>
    </div>
    <div class="tutorial-item">
      <div class="tutorial-header">
        <a href="/tutorials/using-jupyter-notebooks.html">
          Using Jupyter Notebooks
        </a>
      </div>
      <div>
        <p>
          Learn how to connect Jupyter Notebook to a Meltano Project that uses
          Postgres to store the transformed data.
        </p>
      </div>
    </div>
    <div class="tutorial-item">
      <div class="tutorial-header">
        <a href="/tutorials/manual-digitalocean-droplet.html">
          Manually Create a DigitalOcean Droplet for Meltano
        </a>
      </div>
      <div>
        <p>
          Learn how to manually configure a DigitalOcean Droplet for use with
          Meltano.
        </p>
      </div>
    </div>
    <div class="tutorial-item">
      <div class="tutorial-header">
        <a href="/tutorials/create-a-custom-extractor.html">
          Create a Custom Extractor
        </a>
      </div>
      <div>
        <p>
          Learn how to create a custom extractor!
        </p>
      </div>
    </div>
    <div class="tutorial-item">
      <div class="tutorial-header">
        <a href="/tutorials/using-ftp-with-meltano.html">
          How to Use FTP with Meltano
        </a>
      </div>
      <div>
        <p>
          This guide will walk you through how to use FTP with Meltano.
        </p>
      </div>
    </div>
  </div>
</template>

<style scoped>
.tutorial-container {
  display: flex;
  flex-direction: row;
  flex-wrap: wrap;
}
.tutorial-item {
  display: flex;
  flex: 1 1 auto;
  flex-direction: column;
  padding-left: 0.5rem;
  padding-right: 0.5rem;
}
.tutorial-header {
  font-weight: bold;
  padding-bottom: 0.75rem;
  margin-right: 0.75rem;
  border-bottom: 1px solid #eaecef;
}

@media screen and (min-width: 768px) {
  .tutorial-item {
    padding-left: 0;
  }
}
</style>
