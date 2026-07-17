import React from 'react';
import clsx from 'clsx';
import Translate, {translate} from '@docusaurus/Translate';
import Link from '@docusaurus/Link';
import styles from './styles.module.css';
function ReadMoreLabel() {
  return (
    <b>
      <Translate
        id="theme.blog.post.readMore"
        description="The label used in blog post item excerpts to link to full blog posts">
        Read More
      </Translate>
    </b>
  );
}
export default function BlogPostItemFooterReadMoreLink(props) {
  // eslint-disable-next-line react/prop-types
  const {blogPostTitle, className, ...linkProps} = props;
  return (
    <Link
      aria-label={translate(
        {
          message: 'Read more about {title}',
          id: 'theme.blog.post.readMoreLabel',
          description:
            'The ARIA label for the link to full blog posts from excerpts',
        },
        {title: blogPostTitle},
      )}
      className={clsx('changelog-readmore-link', styles.readMoreButton, className)}
      {...linkProps}>
      <ReadMoreLabel />
    </Link>
  );
}
