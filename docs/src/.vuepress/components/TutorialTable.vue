<script>
export default {
  name: "TutorialTable",
};
</script>

<template>
  <div class="tutorial-container">
    <div class="tutorial-item">
      <h2 class="tutorial-header">Table of Contents</h2>
    </div>
    <div class="tutorial-item">
      <div class="tutorial-header">
        <a href="/tutorials/create-a-custom-extractor.html">
          Create a Custom Extractor
        </a>
      </div>
      <div>
        <p>
          Learn how to create your own custom extractor!
        </p>
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
        <a href="/tutorials/install-on-aws.html">
          Installing Meltano on Amazon Web Services (AWS)
        </a>
      </div>
      <div>
        <p>
          Learn how to install Meltano on AWS
        </p>
      </div>
    </div>
  </div>
</template>

<style scoped>
.tutorial-container {
  /* display: flex;
  flex-direction: row;
  flex-wrap: wrap; */
}
.tutorial-item {
  /* display: flex;
  flex: 1 1 auto;
  flex-direction: column; */
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
