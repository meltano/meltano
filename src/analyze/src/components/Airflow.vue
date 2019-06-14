<template>
  <div class="proxy-container">

    <article class="message is-warning is-small">
      <div class="message-header">
        <p>Warning</p>
      </div>
      <div class="message-body">
        <p>You are now looking at the Airflow UI. See the <a target="_blank" href="https://airflow.apache.org/ui.html">documentation</a> for more details.</p>
      </div>
    </article>

    <iframe class="proxy" :src="airflowUrl" />
  </div>
</template>
<script>
export default {
  computed: {
    airflowUrl() {
      return FLASK.airflowUrl;
    },
  },
};
</script>
<style lang="scss">
 .proxy-container {
   display: flex;
   flex-grow: 1;
   flex-direction: column;
 }

 .proxy {
    height: 100vh;
 }
</style>
