<template>
  <div class="proxy-container">
    <p class="disclaimer">You are now looking at the Airflow UI. See the <a target="_blank" href="https://airflow.apache.org/ui.html">documentation</a> for more details.</p>
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
 @import 'bulma';

 .proxy-container {
   display: flex;
   flex-grow: 1;
   flex-direction: column;
 }

 .disclaimer {
   @extend .has-text-white;
   @extend .has-text-centered;
   @extend .is-size-7;

   padding: 0.3rem;
   background: #5555aa;
 }

 .disclaimer a {
   @extend .has-text-white;
   text-decoration: underline;
 }

 .proxy {
    height: 100vh;
 }
</style>
