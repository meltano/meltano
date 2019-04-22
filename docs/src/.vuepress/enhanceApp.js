import CodeBlockCopyButton from './components/CodeBlockCopyButton';

export default ({
  Vue, // the version of Vue being used in the VuePress app
  options, // the options for the root Vue instance
  router, // the router instance for the app
  siteData // site metadata
}) => {

  // Initialization

  window.addEventListener('load', enableCodeBlockCopying);
  router.afterEach((to, from) => {
    Vue.nextTick(() => {
      enableCodeBlockCopying();
    });
  });

  // Methods

  function enableCodeBlockCopying() {
    // Inspired by https://github.com/vuejs/vuepress/pull/751/
    const codeBlocks = Array.from(document.querySelectorAll('div[class*="language-"]'));
    codeBlocks.forEach(generateCodeBlockButton);
  }

  function generateCodeBlockButton(container) {
    // Button setup
    const copyElement = document.createElement('span');
    copyElement.className = 'code-block-copy-button';
    copyElement.title = 'Copy to clipboard';

    // Button append
    copyElement.addEventListener('click', () => {
      const pre = container.querySelector('pre');
      copyToClipboard(pre.innerText);
    });
    container.appendChild(copyElement);

    // Button style offset
    const pseudoBefore = getComputedStyle(container, ':before');
    const hasPseudo = pseudoBefore.getPropertyValue('content') !== 'none';
    if(hasPseudo) {
      copyElement.classList.add('code-block-copy-button-offset');
    }
  }

  // Sourced from https://hackernoon.com/copying-text-to-clipboard-with-javascript-df4d4988697f
  function copyToClipboard(str) {
    // dummy textarea copy target
    const el = document.createElement('textarea');
    el.value = str;
    el.setAttribute('readonly', '');
    el.style.position = 'absolute';
    el.style.left = '-9999px';
    document.body.appendChild(el);

    // copy validation
    const selected =
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

}
