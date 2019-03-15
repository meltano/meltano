
// We could consider merging this PR https://github.com/vuejs/vuepress/pull/751 to be more Vue less vanilla
(function(){

  // Initialization

  window.addEventListener('load', init);

  // Methods

  function init() {
    var codeBlocks = Array.from(document.querySelectorAll('pre'));
    codeBlocks.forEach(copyifyCodeBlock);
  }

  function copyifyCodeBlock(el) {
    el.addEventListener('click', onCopy);
  }

  // Sourced from https://hackernoon.com/copying-text-to-clipboard-with-javascript-df4d4988697f but ES5
  function copyToClipboard(str) {
    // cache
    var el, selected;

    // dummy textarea copy target
    el = document.createElement('textarea');
    el.value = str;
    el.setAttribute('readonly', '');
    el.style.position = 'absolute';
    el.style.left = '-9999px';
    document.body.appendChild(el);

    // copy validation
    selected =
      document.getSelection().rangeCount > 0
        ? document.getSelection().getRangeAt(0)
        : false;

    // copy and cleanup
    el.select();
    document.execCommand('copy');
    document.body.removeChild(el);
    if (selected) {
      document.getSelection().removeAllRanges();
      document.getSelection().addRange(selected);
    }
  };

  // Handlers

  function onCopy(e) {
    var codeString = e.currentTarget.querySelector('code').innerText;
    copyToClipboard(codeString);
  }

})();
