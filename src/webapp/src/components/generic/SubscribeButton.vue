<script>
import Vue from 'vue'
import { mapActions } from 'vuex'

import utils from '@/utils/utils'

export default {
  name: 'Subscribe',
  props: {
    eventType: { type: String, required: true },
    sourceType: { type: String, default: null },
    sourceId: { type: String, default: null }
  },

  data() {
    return {
      model: {
        recipient: null
      }
    }
  },

  computed: {
    isValid() {
      return utils.isValidEmail(this.model.recipient)
    }
  },

  methods: {
    ...mapActions('orchestration', ['createSubscription']),
    handleSubscribe() {
      if (!this.isValid) {
        return
      }

      this.createSubscription({
        eventType: this.eventType,
        sourceType: this.sourceType,
        sourceId: this.sourceId,
        ...this.model
      })
        .then(response => {
          const { recipient } = response.data
          Vue.toasted.global.success(`Subscription created for '${recipient}'.`)
        })
        .catch(this.$error.handle)
        .finally(this.reset)
    },

    reset() {
      this.model.recipient = null
    }
  }
}
</script>

<template>
  <div class="field has-addons">
    <div class="control has-icons-left">
      <input
        v-model="model.recipient"
        class="input"
        type="email"
        name="email"
        placeholder="Your email address"
      />
      <span class="icon is-small is-left">
        <font-awesome-icon icon="envelope" />
      </span>
    </div>
    <div class="control">
      <button class="button is-primary is-outlined" @click="handleSubscribe">
        <span class="icon is-small">
          <font-awesome-icon icon="bell" />
        </span>
        <span>
          Subscribe
        </span>
      </button>
    </div>
  </div>
</template>
