<script>
export default {
  name: "GlobalFooter"
};
</script>

<template>
<!--footer starts from here-->
<footer class="footer">
<div class="container bottom_border">
<div class="row">
<div class=" col-sm-4 col-md col-sm-4  col-12 col">
<h5 class="headin5_foot col_white_foot pt2">Quick links</h5>
<!--headin5_foot-->
<ul class="footer_ul_left">
<li><a href="https://hub.meltano.com/">Meltano Hub</a></li>
<li><a href="https://meltano.com/docs/">Doumentation</a></li>
<li><a href="https://meltano.com/tutorials/">Tutorials</a></li>
<li><a href="https://meltano.com/docs/community.html">Community</a></li>
<li><a href="https://meltano.com/blog/">Blog</a></li>  
</ul>
<!--footer_ul_left ends here-->
</div>

<div class=" col-sm-4 col-md  col-6 col">
<h5 class="headin5_foot col_white_foot pt2">Company</h5>
<!--headin5_amrc-->
<ul class="footer_ul_right">
<li><a href="https://meltano.com/handbook/#subresources">About Meltano</a></li> 
<li><a href="https://meltano.com/handbook/">Handbook</a></li>
<li><a href="https://meltano.com/docs/#job-openings">Careers</a></li>
<li><a href="https://meltano.com/press/">Press</a></li>
</ul>
<!--footer_ul_right ends here-->
</div>
<hr>
    <p>
      <a
        href="https://meltano.com/docs/contributor-guide.html"
        target="_blank"
      >
        Meltano is open source. Contribute to the project! <OutboundLink />
      </a>
    </p>
    <p>
      Copyright 2021 Meltano &mdash; All rights reserved
    </p>
    <ul class="social_footer_ul">
<li><a href="https://twitter.com/meltanodata/"><i class="fab fa-twitter"></i></a></li>
<li><a href="https://www.linkedin.com/company/meltano/"><i class="fab fa-linkedin"></i></a></li>
<li><a href="https://www.facebook.com/meltanodata/"><i class="fab fa-facebook-f"></i></a></li>
</ul>
<!--social_footer_ul ends here-->
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
  list-style-type none

  p
    margin 0.5rem

  a
    color white
    font-weight 500

    &:hover
      text-decoration underline
</style>
