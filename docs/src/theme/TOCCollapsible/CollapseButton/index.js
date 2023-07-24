import React from 'react';
import clsx from 'clsx';
import styles from './styles.module.css';
// eslint-disable-next-line react/prop-types
export default function TOCCollapsibleCollapseButton({ collapsed, ...props }) {
  return (
    <button
      type="button"
      {...props}
      className={clsx(
        'clean-btn',
        styles.tocCollapsibleButton,
        !collapsed && styles.tocCollapsibleButtonExpanded,
        // eslint-disable-next-line react/prop-types
        props.className
      )}
    >
      <svg
        width="24"
        height="25"
        viewBox="0 0 24 25"
        fill="none"
        xmlns="http://www.w3.org/2000/svg"
        className="toc-book-icon"
      >
        <g id="book-open/outline">
          <path
            id="Vector"
            d="M12 7.29201C10.3516 5.81337 8.2144 4.99695 6 5.00001C4.948 5.00001 3.938 5.18001 3 5.51201V19.762C3.96362 19.422 4.97816 19.2489 6 19.25C8.305 19.25 10.408 20.117 12 21.542M12 7.29201C13.6483 5.81328 15.7856 4.99686 18 5.00001C19.052 5.00001 20.062 5.18001 21 5.51201V19.762C20.0364 19.422 19.0218 19.2489 18 19.25C15.7856 19.247 13.6484 20.0634 12 21.542M12 7.29201V21.542"
            stroke="white"
            strokeWidth="1.5"
            strokeLinecap="round"
            strokeLinejoin="round"
          />
        </g>
      </svg>
    </button>
  );
}
