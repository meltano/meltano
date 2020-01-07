<script>
export default {
  name: 'GlobalFooter'
}
</script>

<template>
  <footer class="footer">
    <slot></slot>
    <a href="https://meltano.com/docs/contributing.html" target="_blank"
      >Contribute to the project! <OutboundLink
    /></a>
    <a
      href="https://about.gitlab.com/handbook/marketing/corporate-marketing/#gitlab-trademark--logo-guidelines"
      >Copyright 2020, all rights reserved. Meltano is a trademark of GitLab, Inc.</a
    >
  </footer>
</template>

<style scoped>
.footer {
  display: flex;
  flex-direction: column;
  padding: 2rem 1.5rem;
  text-align: center;
  color: white;
  background-color: #3e3c8e;
}

.footer a {
  color: white;
  font-weight: 500;
  margin: .5rem;
}
</style>
