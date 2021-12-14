<script>
export default {
  name: "GlobalFooter",
};
</script>

<template>
  <footer class="footer">
    <div class="footer-logo">
      <img src="../public/meltano-logo-with-text-white.svg" />
    </div>
    <div class="footer-links-columns">
      <div class="footer-links-column">
        <h5>Quick links</h5>
        <ul>
          <li><a href="https://hub.meltano.com/">Meltano Hub</a></li>
          <li><a href="https://meltano.com/docs/">Doumentation</a></li>
          <li><a href="https://meltano.com/tutorials/">Tutorials</a></li>
          <li>
            <a href="https://meltano.com/docs/community.html">Community</a>
          </li>
          <li><a href="https://meltano.com/blog/">Blog</a></li>
        </ul>
      </div>
      <div class="footer-links-column">
        <h5>Company</h5>
        <ul>
          <li>
            <a href="https://meltano.com/handbook/#subresources"
              >About Meltano</a
            >
          </li>
          <li><a href="https://meltano.com/handbook/">Handbook</a></li>
          <li><a href="https://meltano.com/docs/#job-openings">Careers</a></li>
          <li><a href="https://meltano.com/press/">Press</a></li>
        </ul>
      </div>
    </div>
    <div class="footer-copyright">
      <p>
        <a
          href="https://meltano.com/docs/contributor-guide.html"
          target="_blank"
          >Meltano is open source. Contribute to the project! <OutboundLink
        /></a>
      </p>
      <p>Copyright 2021 Meltano &mdash; All rights reserved</p>
    </div>
  </footer>
</template>

<style lang="stylus">
.footer
  display flex
  flex-direction column
  padding 2rem 1.5rem
  text-align center
  color white
  background-color #3e3c8e
  .footer-logo img
    width: 2.2rem
  .footer-links-columns
    display: flex
    justify-content: center
  .footer-links-column
    margin: 0 50px;
  .footer-copyright
    margin-top: 20px;
  ul
    list-style-type: none;
    margin: 0;
    padding: 0;
  p
    margin 0.5rem

  a
    color white
    font-weight 500

    &:hover
      text-decoration underline
</style>
