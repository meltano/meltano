<template>
  <div class="columns">
    <div class="column is-6">
      <div class="control is-expanded">
        <div class="select is-fullwidth">
          <select>
            <option value="1">is any value</option>
            <option value="0">is</option>
          </select>
        </div>
      </div>
    </div>
    <div class="column is-6">
      <div class="control is-expanded">
        <div class="select is-fullwidth">
          <select>
            <option value="1">Yes</option>
            <option value="0">No</option>
          </select>
        </div>
      </div>
    </div>
  </div>
</template>
<script>
export default {
  name: 'YesNoFilter',
};
</script>
