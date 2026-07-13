import React, { useEffect } from 'react';
import { useHistory, useLocation } from '@docusaurus/router';

// Netlify "Pretty URLs" serves pages at a trailing-slash URL on first load
// (e.g. /resources/accounts/), while in-app navigation uses the slashless
// form (/resources/accounts). React Router resolves relative link clicks
// against the current location, so the trailing slash makes sibling links
// like `profiles#...` resolve to `accounts/profiles#...` on first load only.
// Normalizing the runtime location makes first-load behave like SPA nav.
// eslint-disable-next-line react/prop-types
export default function Root({ children }) {
  const history = useHistory();
  const { pathname, search, hash } = useLocation();

  useEffect(() => {
    if (pathname.length > 1 && pathname.endsWith('/')) {
      history.replace({ pathname: pathname.replace(/\/+$/, ''), search, hash });
    }
  }, [pathname, search, hash, history]);

  return <>{children}</>;
}
