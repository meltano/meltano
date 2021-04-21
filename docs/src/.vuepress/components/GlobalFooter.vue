<script>
export default {
  name: "GlobalFooter"
};
</script>

<template>
  <footer class="footer">
    <slot></slot>
    <a
      href="https://meltano.com/docs/contributor-guide.html"
      target="_blank"
      >Meltano is open source. Contribute to the project! <OutboundLink
    /></a>
    <a
      href="https://about.gitlab.com/handbook/marketing/corporate-marketing/#gitlab-trademark--logo-guidelines"
      >Copyright 2021, all rights reserved. Meltano is a trademark of GitLab,
      Inc.</a
    >
    <a href="/terms.html">Terms of Service</a>
    <a href="/privacy.html">Privacy Policy</a>
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
  margin: 0.5rem;
}
</style>
