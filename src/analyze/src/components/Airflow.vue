<template>
<div>

  <ClosableMessage title='Notice'>
    <p>You are now looking at the Airflow UI. See the <a target="_blank" href="https://airflow.apache.org/ui.html">documentation</a> for more details.</p>
  </ClosableMessage>

  <div class="proxy-container">
    <iframe class="proxy" :src="airflowUrl" />
  </div>

</div>
</template>
<script>
import ClosableMessage from '@/components/generic/ClosableMessage';

export default {
  components: {
    ClosableMessage,
  },
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
