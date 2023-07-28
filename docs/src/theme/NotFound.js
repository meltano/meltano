import React from 'react';
import Translate, { translate } from '@docusaurus/Translate';
import { PageMetadata } from '@docusaurus/theme-common';
import Layout from '@theme/Layout';
import Melty from '@site/static/img/melty.png';

export default function NotFound() {
  return (
    <>
      <PageMetadata
        title={translate({
          id: 'theme.NotFound.title',
          message: 'Page Not Found',
        })}
      />
      <Layout>
        <main className="container my-20">
          <div className="row">
            <div className="col col--6 col--offset-3 text-center flex flex-col justify-center">
              <img src={Melty} alt="Melty" className="-mb-16 lost-melty" />
              <h1 className="hero__title brackets text-6xl my-10">
                <Translate
                  id="theme.NotFound.title"
                  description="The title of the 404 page"
                >
                  404
                </Translate>
              </h1>
              <p className="text-2xl font-semibold">
                <Translate
                  id="theme.NotFound.p1"
                  description="The first paragraph of the 404 page"
                >
                  Here Be Dragons
                </Translate>
              </p>
              <p className="p3 opacity-70">
                <Translate
                  id="theme.NotFound.p2"
                  description="The 2nd paragraph of the 404 page"
                >
                  Do you see what you’re looking for below?
                </Translate>
              </p>
            </div>
          </div>
        </main>
      </Layout>
    </>
  );
}
