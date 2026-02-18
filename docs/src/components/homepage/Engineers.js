/* eslint-disable jsx-a11y/mouse-events-have-key-events */
import { useState, useRef, useEffect } from 'react'
import Path1 from '@site/static/img/engineers/path-1.svg'
import Path2 from '@site/static/img/engineers/path-2.svg'
import Path3 from '@site/static/img/engineers/path-3.svg'
import Path4 from '@site/static/img/engineers/path-4.svg'
import Path5 from '@site/static/img/engineers/path-5.svg'
import Path6 from '@site/static/img/engineers/path-6.svg'
import Path7 from '@site/static/img/engineers/path-7.svg'
import Path8 from '@site/static/img/engineers/path-8.svg'
import MeltyProgramming from '@site/static/img/engineers/melty-programming.webp'
import MeltanoTerminal from '@site/static/img/engineers/meltano-terminal.svg'

import styles from './engineers.module.scss';

const Engineers = ({ data }) => {
  const paths = [
    { svg: Path1, class: 'curved-path-1' },
    { svg: Path2, class: 'curved-path-2' },
    { svg: Path3, class: 'curved-path-3' },
    { svg: Path4, class: 'curved-path-4' },
    { svg: Path5, class: 'curved-path-5' },
    { svg: Path6, class: 'curved-path-6' },
    { svg: Path7, class: 'curved-path-7' },
    { svg: Path8, class: 'curved-path-8' },
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
    if (typeof window !== 'undefined') {
      const handleScroll = () => {
        const scrollTop = window.scrollY
        const elementHeight = givesRef.current.offsetHeight

        if (scrollTop > elementHeight) {
          setIsVisible(true)
        }
      }

      handleScroll()
      window.addEventListener('scroll', handleScroll)

      // Clean up the event listener on component unmount
      return () => {
        window.removeEventListener('scroll', handleScroll)
      }
    }
  }, [])

  return (
    <>
      <div
        className={`${styles['meltano-gives-engineers']} section ${
          isVisible ? styles['in-view'] : ''
        }`}
      >
        <div className="container">
          <div className="heading">
            <h2 class="my-6" dangerouslySetInnerHTML={{ __html: data.engineersTitle }} />
            <p
              className="heading-description p2"
              dangerouslySetInnerHTML={{ __html: data.engineersText }}
            />
          </div>

          <div className={styles['meltano-gives-table-head']}>
            <h5 className="brackets brackets-left">
              {data.engineersHead.engineersHeadLeft}
            </h5>
            <h5 className="brackets-blue brackets-right">
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
                  <item.line.svg
                    className={`${styles['meltano-gives-table-item-path']} ${styles[item.line.class]}`}
                    alt=""
                  />
                  <div
                    className={`${styles['meltano-gives-table-item-path-dot']} ${styles[item.line.class]}`}
                  />
                </div>
              ))}
            </div>
            <div className={styles['meltano-gives-terminal']} ref={givesRef}>
              <MeltanoTerminal
                className={styles['meltano-gives-terminal-image']}
              />
              <img
                className={styles['meltano-gives-melty-image']}
                ref={givesRef}
                src={MeltyProgramming}
                alt=""
              />
            </div>
            <div className={`${styles['meltano-gives-table-list']} ${styles['table-list-right']}`}>
              {secondTable.map(item => (
                <div
                  key={item.index}
                  className={`${styles['meltano-gives-table-item']} ${styles[`table-item-order-${item.line.class.substring(12)}`]}`}
                >
                  <item.line.svg
                    className={`${styles['meltano-gives-table-item-path']} ${styles[item.line.class]}`}
                    alt=""
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

export default Engineers
