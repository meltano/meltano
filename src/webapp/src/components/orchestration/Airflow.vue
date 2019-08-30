<script>
import Message from '@/components/generic/Message'

export default {
  components: {
    Message
  },
  data() {
    return {
      refreshUrl: '',
      targetUrl: '',
      airflowRefreshTimeout: null
    }
  },
  computed: {
    airflowUrl() {
      return FLASK.airflowUrl
    },
    isRefreshing() {
      return this.targetUrl === this.refreshUrl
    }
  },
  beforeDestroy() {
    if(this.airflowRefreshTimeout) {
      clearTimeout(this.airflowRefreshTimeout)
      console.log("clear");
    }
  },
  created() {
    this.targetUrl = this.airflowUrl
  },
  methods: {
    refreshAirflow() {
      this.targetUrl = this.targetUrl === this.airflowUrl ? this.refreshUrl : this.airflowUrl
      if (this.targetUrl === this.refreshUrl) {
        this.airflowRefreshTimeout = setTimeout(this.refreshAirflow, 1000)
      }
    }
  }
}
</script>

<template>
  <section>
    <div class="columns">
      <div class="column">
        <Message>
          <div class="level">
            <div class="level-left">
              <a
                class="button"
                :class="{ 'is-loading': isRefreshing }"
                @click="refreshAirflow">Refresh Airflow</a>
            </div>
            <div class="level-right">
              <p>
                You are now looking at the Airflow UI. See the
                <a target="_blank" href="https://airflow.apache.org/ui.html"
                  >documentation</a
                >
                for more details.
              </p>
            </div>
          </div>
        </Message>

        <div class="proxy-container">
          <iframe class="proxy" :src="targetUrl" />
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
  min-height: 50vh;
}
</style>
