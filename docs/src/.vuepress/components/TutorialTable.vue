<script>
export default {
  name: 'TutorialTable',
}
</script>

<template>
  <div class='tutorial-container'>

    <div class="tutorial-item">
      <div class='tutorial-header'><a href="#starter">Starter - Carbon Emissions</a></div>
      <div>
        <p>Experience a taste of data extraction and loading using Meltano CLI followed by analysis using Meltano UI with its automatic SQL generation.</p>
        <ul>
          <li>SQLite database</li>
          <li>No authentication</li>
          <li>Public carbon emissions dataset</li>
        </ul>
      </div>
    </div>
    <div class="tutorial-item">
      <div class='tutorial-header'><a href="#intermediate">Intermediate - Salesforce</a></div>
      <div>
        <p>Experience the full extract, load, and transorm pipeline with authentication using Meltano CLI followed by analysis using Meltano UI with its automatic SQL generation.</p>
        <ul>
          <li>Postgres database</li>
          <li>Authentication</li>
          <li>Your private Salesforce dataset</li>
        </ul>
      </div>
    </div>
    <div class="tutorial-item">
      <div class='tutorial-header'><a href="#advanced">Advanced - Coming Soon</a></div>
      <div>
        <p>Experience the full ELT pipeline with Snowflake, custom transforms, custom models, and authentication using Meltano CLI followed by analysis using Meltano UI with its automatic SQL generation.</p>
        <ul>
          <li>Postgres database</li>
          <li>Authentication</li>
          <li>Your private Salesforce dataset</li>
          <li>Snowflake integration</li>
          <li>Custom Transforms</li>
          <li>Custom models</li>
        </ul>
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
  padding-left: .5rem;
  padding-right: .5rem;
}
.tutorial-header {
  font-weight: bold;
  padding-bottom: .75rem;
  margin-right: .75rem;
  border-bottom: 1px solid #eaecef;
}

@media screen and (min-width: 768px) {
	.tutorial-item {
    padding-left: 0;
	}
}
</style>
