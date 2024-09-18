/* eslint-disable no-undef */
import React, { useRef, useState, useEffect } from 'react';
import styles from './usecases.module.scss';
import Link from '@docusaurus/Link';
import { Swiper, SwiperSlide } from 'swiper/react';
import { Navigation, A11y } from 'swiper/modules';
import 'swiper/css';
import 'swiper/css/navigation';

const UseCaseList = [
  {
    title: 'Move from internal and niche APIs',
    Svg: require('@site/static/img/homepage/move.svg').default,
    description: (
      <>Iterate with confidence using software development workflows.</>
    ),
    link: {
      title: 'Experience the tool',
      url: '#',
      target: '_blank',
    },
  },
  {
    title: 'Move data from internal databases',
    Svg: require('@site/static/img/homepage/shield.svg').default,
    description: (
      <>Benefit from predictable pricing and lower costs at high volumes.</>
    ),
    link: {
      title: 'See it in action',
      url: '#',
      target: '_blank',
    },
  },
  {
    title: 'Move data from files and spreadsheets',
    Svg: require('@site/static/img/homepage/slice.svg').default,
    description: (
      <>
        Meltano works with any source format and support any storage, from S3 to
        FTP to web URLs.
      </>
    ),
    link: {
      title: 'Experience the tool',
      url: '#',
      target: '_blank',
    },
  },
  {
    title: 'Move data from SaaS applications',
    Svg: require('@site/static/img/homepage/graph.svg').default,
    description: (
      <>
        Choose from our extensive library of connectors and tweak connector
        {/* eslint-disable-next-line no-irregular-whitespace */}
        behavior without support. 
      </>
    ),
    link: {
      title: 'See it in action',
      url: '#',
      target: '_blank',
    },
  },
  {
    title: 'Move from internal and niche APIs',
    Svg: require('@site/static/img/homepage/move.svg').default,
    description: (
      <>Iterate with confidence using software development workflows.</>
    ),
    link: {
      title: 'Experience the tool',
      url: '#',
      target: '_blank',
    },
  },
  {
    title: 'Move from internal and niche APIs',
    Svg: require('@site/static/img/homepage/shield.svg').default,
    description: (
      <>
        Get started with Meltano and run an EL[T] pipeline with a data source
        and destination of your choosing.
      </>
    ),
    link: {
      title: 'See it in action',
      url: '#',
      target: '_blank',
    },
  },
];

// eslint-disable-next-line react/prop-types
function UseCase({ Svg, title, description, link }) {
  return (
    <div className={'h-full ' + styles.card}>
      <div className={'text-left flex flex-col justify-between h-full'}>
        <div className={styles.usecaseContent}>
          <div className={styles.header}>
            <Svg className={styles.featureSvg} role="img" />
            <h4 className="text-2xl font-semibold mt-6 mb-3">{title}</h4>
          </div>
          <p className="p2 mb-6">{description}</p>
        </div>
        <Link
          // eslint-disable-next-line react/prop-types
          to={link.url}
          // eslint-disable-next-line react/prop-types
          target={link.target}
          className={'btn ' + styles.button}
        >
          <span />
          {/* eslint-disable-next-line react/prop-types */}
          {link.title}
        </Link>
      </div>
    </div>
  );
}

export default function HomepageUseCases() {
  const [swiper, setSwiper] = useState();
  const prevRef = useRef();
  const nextRef = useRef();

  useEffect(() => {
    if (swiper) {
      swiper.params.navigation.prevEl = prevRef.current;
      swiper.params.navigation.nextEl = nextRef.current;
      swiper.navigation.init();
      swiper.navigation.update();
    }
  }, [swiper]);

  return (
    <section className="my-10 md:my-20">
      <div className="container relative">
        <h2
          className={
            'text-center font-bold pb-10 md:pb-20 ' + styles.usecaseHeader
          }
        >
          Use cases
        </h2>
        <div className="relative px-10 md:px-0">
          <Swiper
            modules={[Navigation, A11y]}
            slidesPerView={1}
            onSwiper={setSwiper}
            spaceBetween="16"
            navigation={{
              prevEl: prevRef?.current,
              nextEl: nextRef?.current,
            }}
            breakpoints={{
              320: {
                slidesPerView: 1,
              },
              996: {
                slidesPerView: 3,
              },
              1280: {
                slidesPerView: 4,
              },
            }}
            className={styles.usecaseSwiper}
            wrapperClass="grid"
          >
            {UseCaseList.map((props, idx) => (
              <SwiperSlide key={idx}>
                <UseCase {...props} />
              </SwiperSlide>
            ))}
          </Swiper>
          <div className={styles.swiperPrev} ref={prevRef} />
          <div className={styles.swiperNext} ref={nextRef} />
        </div>
      </div>
    </section>
  );
}
