<script>
export default {
  name: 'TutorialTable',
}
</script>

<template>
  <div class='tutorial-container'>

    <div class="tutorial-item">
      <div class='tutorial-header'><a href="#starter">Starter</a></div>
      <div>
        <ul>
          <li>SQLite database</li>
          <li>No authentication</li>
          <li>Public carbon emissions dataset</li>
        </ul>
      </div>
    </div>
    <div class="tutorial-item">
      <div class='tutorial-header'><a href="#intermediate">Intermediate</a></div>
      <div>
        <ul>
          <li>Postgres database</li>
          <li>Authentication</li>
          <li>Private Salesforce dataset</li>
        </ul>
      </div>
    </div>
    <div class="tutorial-item">
      <div class='tutorial-header'><a href="#advanced">Advanced</a></div>
      <div>
        <ul>
          <li>Postgres database</li>
          <li>Authentication</li>
          <li>Private Salesforce dataset</li>
          <li>Snowflake integration</li>
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
