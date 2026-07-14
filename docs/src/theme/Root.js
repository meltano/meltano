import React, { useEffect } from 'react';
import { useHistory } from '@docusaurus/router';

// Netlify "Pretty URLs" serves pages at a trailing-slash URL (e.g.
// /resources/accounts/), while in-app navigation uses the slashless form
// (/resources/accounts). React Router resolves relative link clicks against
// the current location, so a trailing slash makes sibling links like
// `profiles#...` resolve to `accounts/profiles#...`. Normalizing the runtime
// location makes every navigation behave like slashless SPA navigation.
//
// Subscribe imperatively via history.listen rather than useLocation so Root
// never re-renders on navigation; the effect runs once (history is stable).
// eslint-disable-next-line react/prop-types
export default function Root({ children }) {
  const history = useHistory();

  useEffect(() => {
    const normalize = ({ pathname, search, hash }) => {
      if (pathname.length > 1 && pathname.endsWith('/')) {
        history.replace({ pathname: pathname.replace(/\/+$/, ''), search, hash });
      }
    };
    normalize(history.location); // current location (listen only fires on later navs)
    return history.listen(normalize);
  }, [history]);

  return <>{children}</>;
}
