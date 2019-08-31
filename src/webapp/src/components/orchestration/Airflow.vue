<script>
import Message from '@/components/generic/Message'

export default {
  components: {
    Message
  },
  computed: {
    airflowUrl() {
      return FLASK.airflowUrl
    }
  }
}
</script>

<template>
  <section>
    <div class="columns">
      <div class="column">
        <Message>
          <p>
            You are now looking at the Airflow UI. See the
            <a target="_blank" href="https://airflow.apache.org/ui.html"
              >documentation</a
            >
            for more details.
          </p>
        </Message>

        <div class="proxy-container">
          <iframe class="proxy" :src="airflowUrl" />
        </div>
      </div>
    </div>
  </section>
</template>

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
