<script>
export default {
  name: 'YouTubeEmbed',
  props: {
    src: {
      type: String,
      required: true
    }
  }
}
</script>

<template>
  <div class="embed-responsive embed-responsive-16by9">
    <iframe
      width="560"
      height="315"
      :src="src"
      frameborder="0"
      allow="accelerometer; autoplay; encrypted-media; gyroscope; picture-in-picture"
      allowfullscreen
    ></iframe>
  </div>
</template>

<style></style>
