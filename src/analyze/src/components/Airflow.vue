<template>
  <div class="proxy-container">
    <p class="disclaimer">You are now looking at the Airflow UI.</p>
    <iframe class="proxy" :src="airflowUrl" />
  </div>
</template>
<script>
import Vue from 'vue';

export default {
  computed: {
    airflowUrl() {
      return FLASK.airflowUrl;
    },
  },

  beforeRouteEnter(to, from, next) {
    if (FLASK.airflowUrl) {
      next();
    } else {
      Vue.toasted.show("Airflow is not installed.");
      next(from.path);
    }
  },
};
</script>
<style>
 .proxy-container {
   display: flex;
   flex-grow: 1;
   flex-direction: column;
 }

 .disclaimer {
   font-size: 0.8rem;
   padding: 0.3rem;
   color: white;
   text-align: center;
   background: #5555aa;
 }

 .proxy {
   flex: 1;
 }
</style>
