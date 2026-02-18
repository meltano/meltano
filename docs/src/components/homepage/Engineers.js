/* eslint-disable jsx-a11y/mouse-events-have-key-events */
import { useState, useRef, useEffect } from 'react'
import MeltyProgramming from '@site/static/img/engineers/melty-programming.webp'

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
        className={`meltano-gives-engineers section ${
          isVisible ? 'in-view' : ''
        }`}
      >
        <div className="container">
          <div className="heading">
            <h2 className="my-6" dangerouslySetInnerHTML={{ __html: data.engineersTitle }} />
            <p
              className="heading-description p2"
              dangerouslySetInnerHTML={{ __html: data.engineersText }}
            />
          </div>

          <div className='meltano-gives-table-head'>
            <h5 className="brackets brackets-left">
              {data.engineersHead.engineersHeadLeft}
            </h5>
            <h5 className="brackets-blue brackets-right">
              {data.engineersHead.engineersHeadRight}
            </h5>
          </div>
          <div className='meltano-gives-table'>
            <div className="meltano-gives-table-list table-list-left">
              {firstTable.map(item => (
                <div
                  key={item.index}
                  className={`meltano-gives-table-item table-item-order-${item.line.class.substring(
                    12
                  )}`}
                >
                  <div className="meltano-gives-table-item-bubble">
                    <item.engineersTableImage
                      className="meltano-gives-table-item-image"
                      alt={item.engineersTableText}
                    />
                    <span className="meltano-gives-table-item-label">
                      {item.engineersTableText}
                    </span>
                  </div>
                  <img
                    className={`meltano-gives-table-item-path ${item.line.class}`}
                    src={item.line.svg}
                    alt=""
                    width="100%"
                    height="auto"
                  />
                  <div
                    className={`meltano-gives-table-item-path-dot ${item.line.class}`}
                  />
                </div>
              ))}
            </div>
            <div className="meltano-gives-terminal" ref={givesRef}>
              <img
                className="meltano-gives-terminal-image"
                src='/img/engineers/meltano-terminal.svg'
                alt=""
                width="100%"
                height="auto"
              />
              <img
                className="meltano-gives-melty-image"
                ref={givesRef}
                src={MeltyProgramming}
                alt=""
                width="100%"
                height="auto"
              />
            </div>
            <div className="meltano-gives-table-list table-list-right">
              {secondTable.map(item => (
                <div
                  key={item.index}
                  className={`meltano-gives-table-item table-item-order-${item.line.class.substring(
                    12
                  )}`}
                >
                  <img
                    className={`meltano-gives-table-item-path ${item.line.class}`}
                    src={item.line.svg}
                    alt=""
                    width="100%"
                    height="auto"
                  />
                  <div
                    className={`meltano-gives-table-item-path-dot ${item.line.class}`}
                  />
                  <div className="meltano-gives-table-item-bubble">
                    <item.engineersTableImage
                      className="meltano-gives-table-item-image"
                      alt={item.engineersTableText}
                    />
                    <span className="meltano-gives-table-item-label">
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

