import React from 'react';
import clsx from 'clsx';
import styles from './styles.module.css';
// eslint-disable-next-line react/prop-types
function ColorModeToggle({ className, buttonClassName, value, onChange }) {
  return (
    <div
      className={clsx(styles.toggle, className, buttonClassName, 'relative')}
    >
      <label className={styles.lightDarkToggle}>
        <input
          className={styles.toggleCheckbox}
          type="checkbox"
          checked={value === 'light'}
          onClick={() => onChange(value === 'dark' ? 'light' : 'dark')}
          readOnly
        />
        <div className={styles.toggleSlot}>
          <div className={styles.sunIconWrapper}>
            <svg
              className="sun-icon"
              width="20"
              height="20"
              viewBox="0 0 20 20"
              fill="none"
            >
              <line
                x1="9.66602"
                y1="20.0002"
                x2="9.66602"
                y2="16.0002"
                stroke="#080216"
                strokeOpacity="0.5"
                strokeWidth="2"
              />
              <line
                x1="9.66504"
                y1="4.00024"
                x2="9.66504"
                y2="0.000244053"
                stroke="#080216"
                strokeOpacity="0.5"
                strokeWidth="2"
              />
              <line
                x1="-0.000976316"
                y1="9.66699"
                x2="3.99902"
                y2="9.66699"
                stroke="#080216"
                strokeOpacity="0.5"
                strokeWidth="2"
              />
              <line
                x1="15.998"
                y1="9.66675"
                x2="19.998"
                y2="9.66675"
                stroke="#080216"
                strokeOpacity="0.5"
                strokeWidth="2"
              />
              <line
                x1="3.13078"
                y1="16.6264"
                x2="5.95921"
                y2="13.798"
                stroke="#080216"
                strokeOpacity="0.5"
                strokeWidth="2"
              />
              <line
                x1="13.7968"
                y1="5.95964"
                x2="16.6252"
                y2="3.13121"
                stroke="#080216"
                strokeOpacity="0.5"
                strokeWidth="2"
              />
              <line
                x1="3.21199"
                y1="3.13054"
                x2="6.04042"
                y2="5.95897"
                stroke="#080216"
                strokeOpacity="0.5"
                strokeWidth="2"
              />
              <line
                x1="13.878"
                y1="13.7975"
                x2="16.7064"
                y2="16.626"
                stroke="#080216"
                strokeOpacity="0.5"
                strokeWidth="2"
              />
              <circle
                opacity="0.5"
                cx="9.99805"
                cy="10.0005"
                r="4"
                transform="rotate(-180 9.99805 10.0005)"
                fill="#080216"
              />
            </svg>
          </div>
          <div className={styles.toggleButton} />
          <div className={styles.moonIconWrapper}>
            <svg
              className="moon-icon"
              width="15"
              height="16"
              viewBox="0 0 15 16"
              fill="none"
            >
              <path
                fillRule="evenodd"
                clipRule="evenodd"
                d="M5.14848 0.548777C2.1512 1.58901 -0.00047206 4.43786 -0.000472353 7.78925C-0.000472723 12.0209 3.42999 15.4514 7.66169 15.4514C10.4116 15.4514 12.8231 14.0028 14.1748 11.8271C13.3875 12.1003 12.5419 12.2488 11.6616 12.2488C7.4299 12.2488 3.99943 8.81831 3.99943 4.58662C3.99943 3.10479 4.42008 1.72121 5.14848 0.548777Z"
                fill="#080216"
                fillOpacity="0.5"
              />
            </svg>
          </div>
        </div>
      </label>
    </div>
  );
}
export default React.memo(ColorModeToggle);
