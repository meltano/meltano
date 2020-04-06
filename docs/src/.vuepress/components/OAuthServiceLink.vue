<script>
const OAUTH_SERVICE_URL="https://oauth.svc.meltanodata.com"

export default {
  name: 'OAuthServiceLink',
  props: {
    provider: null,
  },
  computed: {
    url() {
      return OAUTH_SERVICE_URL + '/' + this.provider;
    }
  },
  methods: {
    open() {
      const winOpts =
        'resizable=no,scrollbars=no,close=yes,height=640,width=480'

      window.open(this.url, name, winOpts)
    }
  },
}
</script>

<template>
  <a :href="url" @click.prevent="open" target="_blank">
    <slot></slot>
  </a>
</template>
