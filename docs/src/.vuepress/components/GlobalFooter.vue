<script>
export default {
  name: 'GlobalFooter',
  data: () => ({
    atPageBottom: false
  }),
  beforeMount() {
    window.onscroll = () => {
      const INTERCOM_BUTTON_HEIGHT_IMPACT = 50

      if (
        window.innerHeight + window.pageYOffset >=
        document.body.offsetHeight - INTERCOM_BUTTON_HEIGHT_IMPACT
      ) {
        this.atPageBottom = true
      } else {
        this.atPageBottom = false
      }
    }
  }
}
</script>

<template>
  <footer class="footer">
    <div>
      <slot></slot>
      <a href="https://meltano.com/docs/contributing.html" target="_blank"
        >Contribute to the project! <OutboundLink
      /></a>
    </div>
    <a
      href="https://about.gitlab.com/handbook/marketing/corporate-marketing/#gitlab-trademark--logo-guidelines"
      class="trademark"
      :class="atPageBottom ? 'is-offset' : ''"
      >Meltano is a trademark of GitLab, Inc.</a
    >
  </footer>
</template>

<style scoped>
.footer {
  display: flex;
  justify-content: space-between;
  padding: 2rem 1.5rem;
  text-align: center;
  color: white;
  background-color: #3e3c8e;
}

.footer a {
  color: white;
  font-weight: 500;
}

.trademark {
  transition: transform 0.2s ease-in-out;
}

.trademark.is-offset {
  /* Magic number is the visual impact
  of width needed for the trademwork 
  to be legible */
  transform: translateX(-75px);
}
</style>
