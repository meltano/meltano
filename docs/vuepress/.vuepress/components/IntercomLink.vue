<script>
export default {
  methods: {
    showIntercom() {
      this.$intercom.show();
    }
  }
};
</script>

<template>
  <a @click.prevent="showIntercom" href="#"><slot></slot></a>
</template>
