<script>
export default {};
</script>

<template>
  <a
    :href="$site.themeConfig.data.slackChannelUrl"
    target="_blank"
    rel="noopener noreferrer"
  >
    <slot></slot>
  </a>
</template>
