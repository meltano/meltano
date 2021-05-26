export default ({
  Vue, // the version of Vue being used in the VuePress app
  options, // the options for the root Vue instance
  router, // the router instance for the app
  siteData, // site metadata,
  isServer // is this enhancement applied in server-rendering or client
}) => {
  if (!isServer) {
    window.addEventListener('load', enableExternalScroll);
  }

  function enableExternalScroll() {
    window.addEventListener('message', msg => {
      if (msg.data['source'] == 'meltano') {
        const anchor_name = msg.data['anchor'];
        const anchor = document.getElementById(anchor_name);

        if (anchor) {
          anchor.scrollIntoView();
        }
      }
    });
  }
};

