<script>
export default {
  name: 'DateRangeCustomVsRelative',
  props: {},
  data() {
    return {
      isCustom: true
    }
  },
  computed: {},
  methods: {
    onIsCustomChange(value) {
      this.isCustom = value
    }
  }
}
</script>

<template>
  <div class="field is-grouped">
    <div class="control">
      <div class="field has-addons">
        <div class="control">
          <button
            class="button is-small is-outlined"
            :class="{ 'is-interactive-secondary is-active': isCustom }"
            @click="onIsCustomChange(true)"
          >
            Custom
          </button>
        </div>
        <div class="control">
          <div
            class="button is-small is-outlined"
            :class="{
              'is-interactive-secondary is-active has-nested-control': !isCustom
            }"
            @click="onIsCustomChange(false)"
          >
            <span>Relative</span>
          </div>
        </div>
      </div>
    </div>

    <div v-if="!isCustom" class="control">
      <div class="field has-addons">
        <div class="control">
          <span class="select is-small">
            <select value="Past">
              <option>Past</option>
              <option>Future</option>
            </select>
          </span>
        </div>
        <div class="control">
          <input
            class="input is-small max-width-3r"
            type="number"
            placeholder="7"
          />
        </div>
        <div class="control">
          <span class="select is-small">
            <select value="Days">
              <option>Days</option>
              <option>Months</option>
              <option>Years</option>
            </select>
          </span>
        </div>
      </div>
    </div>
  </div>
</template>

<style lang="scss">
.max-width-3r {
  max-width: 3rem;
}
</style>
