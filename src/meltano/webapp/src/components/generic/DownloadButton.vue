<script>
import utils from '@/utils/utils'

export default {
  name: 'DownloadButton',
  props: {
    fileName: { type: String, required: true },
    label: { type: String, required: false, default: 'Download' },
    triggerPromise: { type: Function, required: true },
    triggerPayload: { type: Object, required: true },
  },
  data() {
    return {
      isLoading: false,
    }
  },
  methods: {
    download() {
      this.isLoading = true
      this.triggerPromise(this.triggerPayload).then((response) => {
        utils.downloadBlobAsFile(response.data, this.fileName)
        this.isLoading = false
      })
    },
  },
}
</script>

<template>
  <button class="button" :class="{ 'is-loading': isLoading }" @click="download">
    <span class="icon">
      <font-awesome-icon icon="file-download" />
    </span>
    <span>{{ label }}</span>
  </button>
</template>

<style lang="scss"></style>
