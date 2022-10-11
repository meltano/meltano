<script>
import Vue from 'vue'

import Dropdown from '@/components/generic/Dropdown'
import embedsApi, { EMBED_RESOURCE_TYPES } from '@/api/embeds'
import utils from '@/utils/utils'

export default {
  name: 'EmbedShareButton',
  components: {
    Dropdown,
  },
  props: {
    buttonClasses: { type: String, default: '' },
    isDisabled: { type: Boolean, default: false },
    resource: { type: Object, required: true },
    resourceType: {
      type: String,
      required: true,
      validator: (value) => Object.values(EMBED_RESOURCE_TYPES).includes(value),
    },
  },
  data: () => ({
    isAwaitingEmbed: false,
  }),
  methods: {
    copyToClipboard(refName) {
      const el = this.$refs[refName]
      const isSuccess = utils.copyToClipboard(el)
      isSuccess
        ? Vue.toasted.global.success('Copied to clipboard')
        : Vue.toasted.global.error('Failed copy, try manual selection')
    },
    getResourceEmbed(resource) {
      this.isAwaitingEmbed = true
      embedsApi
        .generate({
          resourceId: resource.id,
          resourceType: this.resourceType,
          today: utils.formatDateStringYYYYMMDD(new Date()),
        })
        .then((response) => {
          this.$refs[`link-${resource.id}`].value = response.data.url
          this.$refs[`embed-${resource.id}`].value = response.data.snippet
          if (response.data.isNew) {
            Vue.toasted.global.success(`${resource.name} embed code created`)
          }
        })
        .catch((error) => {
          Vue.toasted.global.error(
            `${resource.name} embed error. [Error code: ${error.response.data.code}]`
          )
        })
        .finally(() => (this.isAwaitingEmbed = false))
    },
  },
}
</script>

<template>
  <Dropdown
    :tooltip="{
      classes: 'is-tooltip-left',
      message: 'Create a link or embed to share',
    }"
    label="Share"
    :button-classes="`button ${buttonClasses}`"
    menu-classes="dropdown-menu-300"
    :disabled="isAwaitingEmbed || isDisabled"
    is-right-aligned
    @dropdown:open="getResourceEmbed(resource)"
  >
    <div class="dropdown-content is-size-7">
      <div class="dropdown-item">
        <label class="label">Link</label>
        <div class="field has-addons">
          <p class="control is-expanded">
            <input
              :ref="`link-${resource.id}`"
              class="input is-small is-family-code has-background-white-ter has-text-grey-dark"
              type="text"
              placeholder="Generating link..."
              readonly
            />
          </p>
          <p class="control">
            <button
              class="button is-small"
              :disabled="isAwaitingEmbed"
              @click="copyToClipboard(`link-${resource.id}`)"
            >
              Copy
            </button>
          </p>
        </div>
      </div>
      <div class="dropdown-item">
        <div class="field">
          <label class="label">Embed</label>
          <div class="field has-addons">
            <p class="control is-expanded">
              <input
                :ref="`embed-${resource.id}`"
                class="input is-small is-family-code has-background-white-ter has-text-grey-dark"
                type="text"
                placeholder="Generating snippet..."
                readonly
              />
            </p>
            <p class="control">
              <button
                class="button is-small"
                :disabled="isAwaitingEmbed"
                @click="copyToClipboard(`embed-${resource.id}`)"
              >
                Copy
              </button>
            </p>
          </div>
        </div>
      </div>
      <div class="dropdown-item">
        <p class="is-italic is-size-7">
          The above link and embed are
          <strong>publicly accessible</strong> and
          <strong>read-only</strong> versions of this resource.
        </p>
      </div>
    </div>
  </Dropdown>
</template>

<style lang="scss"></style>
