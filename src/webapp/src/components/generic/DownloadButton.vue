<script>
import utils from '@/utils/utils'

export default {
  name: 'DownloadButton',
  props: {
    isDisabled: { type: Boolean, required: false, default: true },
    fileName: { type: String, required: true },
    label: { type: String, required: false, default: 'Download' },
    triggerPromise: { type: Function, required: true },
    triggerPayload: { type: Object, required: true }
  },
  data() {
    return {
      isLoading: false
    }
  },
  methods: {
    download() {
      this.isLoading = true
      this.triggerPromise(this.triggerPayload).then(response => {
        utils.downloadBlobAsFile(response.data, this.fileName)
        this.isLoading = false
      })
    }
  }
}
</script>

<template>
  <a
    class="button"
    :class="{ 'is-loading': isLoading }"
    :disabled="isDisabled"
    @click="download"
    >{{ label }}</a
  >
</template>

<style lang="scss"></style>
