<script>
import embedsApi from '@/api/embeds'
import Logo from '@/components/navigation/Logo'
import RouterViewLayout from '@/views/RouterViewLayout'

export default {
  name: 'ResourceEmbed',
  components: {
    Logo,
    RouterViewLayout,
  },
  props: {
    token: { type: String, default: null },
    today: { type: String, default: null },
  },
  data() {
    return {
      error: null,
      isLoading: true,
      resource: null,
      resourceType: null,
    }
  },
  created() {
    this.initialize()
  },
  methods: {
    initialize() {
      embedsApi
        .load(this.token, this.today)
        .then((response) => {
          this.resource = response.data.resource
          this.resourceType = response.data.resourceType
        })
        .catch((error) => {
          this.error = error.response.data.code
        })
        .finally(() => (this.isLoading = false))
    },
  },
}
</script>

<template>
  <router-view-layout>
    <div v-if="isLoading" class="box is-marginless">
      <progress class="progress is-small is-info"></progress>
    </div>

    <div v-else class="box is-marginless">
      <div class="content has-text-centered">
        <p class="is-italic">{{ error }}</p>
      </div>
    </div>

    <div class="is-pulled-right mt-05r scale-08">
      <a href="https://meltano.com" target="_blank" class="is-size-7">
        <span class="is-inline-block has-text-grey">Made with</span>
        <Logo class="ml-05r"
      /></a>
    </div>
  </router-view-layout>
</template>

<style lang="scss">
.scale-08 {
  transform: scale(0.8);
}
</style>
