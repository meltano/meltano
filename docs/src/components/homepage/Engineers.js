import React from 'react'
import PropTypes from 'prop-types'
import { useState, useRef, useEffect } from 'react'
import MeltyProgramming from '@site/static/img/engineers/melty-programming.webp'
import styles from './engineers.module.scss';

const Engineers = ({ data }) => {
  const paths = [
    { svg: '/img/engineers/path-1.svg', class: 'curved-path-1' },
    { svg: '/img/engineers/path-2.svg', class: 'curved-path-2' },
    { svg: '/img/engineers/path-3.svg', class: 'curved-path-3' },
    { svg: '/img/engineers/path-4.svg', class: 'curved-path-4' },
    { svg: '/img/engineers/path-5.svg', class: 'curved-path-5' },
    { svg: '/img/engineers/path-6.svg', class: 'curved-path-6' },
    { svg: '/img/engineers/path-7.svg', class: 'curved-path-7' },
    { svg: '/img/engineers/path-8.svg', class: 'curved-path-8' },
  ]

  const tableItems = data.engineersTable.map((path, index) => ({
    ...path,
    index: index,
    line: paths[index],
  }))

  const firstTable = tableItems.slice(0, 4)
  const secondTable = tableItems.slice(4)

  const [isVisible, setIsVisible] = useState(false)
  const givesRef = useRef(null)

  useEffect(() => {
    const el = givesRef.current
    if (!el) return

    const observer = new IntersectionObserver(
      ([entry]) => {
        if (entry.isIntersecting) {
          setIsVisible(true)
          observer.disconnect()
        }
      },
      { threshold: 0.1 }
    )

    observer.observe(el)

    return () => {
      observer.disconnect()
    }
  }, [])

  return (
    <>
      <div
        className={`${styles['meltano-gives-engineers']} section ${
          isVisible ? styles['in-view'] : ''
        }`}
      >
        <div className={styles.container}>
          <div className="heading">
            <h2 className="my-6" dangerouslySetInnerHTML={{ __html: data.engineersTitle }} />
            <p
              className="heading-description p2"
              dangerouslySetInnerHTML={{ __html: data.engineersText }}
            />
          </div>

          <div className={styles['meltano-gives-table-head']}>
            <h5 className={`brackets ${styles['brackets-left']}`}>
              {data.engineersHead.engineersHeadLeft}
            </h5>
            <h5 className={`brackets-blue ${styles['brackets-right']}`}>
              {data.engineersHead.engineersHeadRight}
            </h5>
          </div>
          <div className={styles['meltano-gives-table']}>
            <div className={`${styles['meltano-gives-table-list']} ${styles['table-list-left']}`}>
              {firstTable.map(item => (
                <div
                  key={item.index}
                  className={`${styles['meltano-gives-table-item']} ${styles[`table-item-order-${item.line.class.substring(12)}`]}`}
                >
                  <div className={styles['meltano-gives-table-item-bubble']}>
                    <item.engineersTableImage
                      className={styles['meltano-gives-table-item-image']}
                      alt={item.engineersTableText}
                    />
                    <span className={styles['meltano-gives-table-item-label']}>
                      {item.engineersTableText}
                    </span>
                  </div>
                  <img
                    className={`${styles['meltano-gives-table-item-path']} ${styles[item.line.class]}`}
                    src={item.line.svg}
                    alt=""
                    width="100%"
                    height="auto"
                  />
                  <div
                    className={`${styles['meltano-gives-table-item-path-dot']} ${styles[item.line.class]}`}
                  />
                </div>
              ))}
            </div>
            <div className={styles['meltano-gives-terminal']} ref={givesRef}>
              <img
                className={styles['meltano-gives-terminal-image']}
                src='/img/engineers/meltano-terminal.svg'
                alt=""
                width="100%"
                height="auto"
              />
              <img
                className={styles['meltano-gives-melty-image']}
                src={MeltyProgramming}
                alt=""
                width="100%"
                height="auto"
              />
            </div>
            <div className={`${styles['meltano-gives-table-list']} ${styles['table-list-right']}`}>
              {secondTable.map(item => (
                <div
                  key={item.index}
                  className={`${styles['meltano-gives-table-item']} ${styles[`table-item-order-${item.line.class.substring(12)}`]}`}
                >
                  <img
                    className={`${styles['meltano-gives-table-item-path']} ${styles[item.line.class]}`}
                    src={item.line.svg}
                    alt=""
                    width="100%"
                    height="auto"
                  />
                  <div
                    className={`${styles['meltano-gives-table-item-path-dot']} ${styles[item.line.class]}`}
                  />
                  <div className={styles['meltano-gives-table-item-bubble']}>
                    <item.engineersTableImage
                      className={styles['meltano-gives-table-item-image']}
                      alt={item.engineersTableText}
                    />
                    <span className={styles['meltano-gives-table-item-label']}>
                      {item.engineersTableText}
                    </span>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>
      {/* <Modal
        isOpen={modalIsOpen}
        // eslint-disable-next-line react/jsx-no-bind
        onRequestClose={closeModal}
        contentLabel="Subscribe Modal"
        ariaHideApp={false}
        className="video-modal"
        overlayClassName="video-overlay"
        shouldCloseOnOverlayClick
      >
        <div className="button-wrapper">
          <button type="button" onClick={closeModal}>
            <img src={CloseButton} alt="" className="" />
          </button>
        </div>
        <div className="modal-content">
          <div className="video-poster">
            <iframe
              width="791"
              height="508"
              src="https://www.youtube.com/embed/rGlf43bAG6I?enablejsapi=1"
              title="YouTube video player"
              frameBorder="0"
              allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share"
              allowfullscreen
            />
          </div>
        </div>
      </Modal> */}
    </>
  )
}

Engineers.propTypes = {
  data: PropTypes.shape({
    engineersTable: PropTypes.arrayOf(PropTypes.object).isRequired,
    engineersTitle: PropTypes.string.isRequired,
    engineersText: PropTypes.string.isRequired,
    engineersHead: PropTypes.shape({
      engineersHeadLeft: PropTypes.string.isRequired,
      engineersHeadRight: PropTypes.string.isRequired,
    }).isRequired,
  }).isRequired,
}

export default Engineers
