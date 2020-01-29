<script>
import Vue from 'vue'

import Dropdown from '@/components/generic/Dropdown'
import reportsApi from '@/api/reports'
import utils from '@/utils/utils'

export default {
  name: 'EmbedButton',
  components: {
    Dropdown
  },
  props: {
    buttonClasses: { type: String, default: '' },
    report: { type: Object, required: true }
  },
  data: () => ({
    isAwaitingEmbed: false
  }),
  methods: {
    copyToClipboard(refName) {
      const el = this.$refs[refName]
      const isSuccess = utils.copyToClipboard(el)
      isSuccess
        ? Vue.toasted.global.success('Copied to clipboard')
        : Vue.toasted.global.error('Failed copy, try manual selection')
    },
    getReportEmbed(report) {
      this.isAwaitingEmbed = true
      reportsApi
        .generateEmbedURL(report)
        .then(response => {
          this.$refs[`embed-${report.id}`].value = response.data.snippet
          if (response.data.isNew) {
            Vue.toasted.global.success(`${report.name} embed code created`)
          }
        })
        .catch(error => {
          Vue.toasted.global.error(
            `${report.name} embed error. [Error code: ${error.response.data.code}]`
          )
        })
        .finally(() => (this.isAwaitingEmbed = false))
    }
  }
}
</script>

<template>
  <Dropdown
    :tooltip="{
      classes: 'is-tooltip-left',
      message: 'Create an embeddable code snippet'
    }"
    label="Embed"
    :button-classes="`button ${buttonClasses}`"
    menu-classes="dropdown-menu-300"
    :disabled="isAwaitingEmbed"
    is-right-aligned
    @dropdown:open="getReportEmbed(report)"
  >
    <div class="dropdown-content is-size-7">
      <div class="dropdown-item">
        <div class="field has-addons">
          <p class="control is-expanded">
            <input
              :ref="`embed-${report.id}`"
              class="input is-small is-family-code has-background-white-ter	has-text-grey-dark	"
              type="text"
              placeholder="Generating snippet..."
              readonly
            />
          </p>
          <p class="control">
            <button
              class="button is-small"
              :disabled="isAwaitingEmbed"
              @click="copyToClipboard(`embed-${report.id}`)"
            >
              Copy Snippet
            </button>
          </p>
        </div>
      </div>
      <div class="dropdown-item">
        <p class="is-italic is-size-7">
          The above snippet is a
          <strong>publicly embeddable</strong> and
          <strong>read-only</strong> version of this report.
        </p>
      </div>
    </div>
  </Dropdown>
</template>

<style lang="scss"></style>
