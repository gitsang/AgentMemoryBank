import type {ReactNode} from 'react';
import Link from '@docusaurus/Link';
import useDocusaurusContext from '@docusaurus/useDocusaurusContext';
import Layout from '@theme/Layout';
import Heading from '@theme/Heading';

export default function Home(): ReactNode {
  const {siteConfig} = useDocusaurusContext();

  return (
    <Layout title={siteConfig.title} description={siteConfig.tagline}>
      <main className="container margin-vert--xl">
        <div className="row">
          <div className="col col--8 col--offset-2">
            <Heading as="h1">{siteConfig.title}</Heading>
            <p>{siteConfig.tagline}</p>
            <p>
              Open the handbook or start the local practice page from the
              normalized subject 1 dataset.
            </p>
            <div className="button-group button-group--block">
              <Link className="button button--primary button--lg" to="/docs/handbook-outline">
                Open handbook
              </Link>
              <Link className="button button--secondary button--lg" to="/practice">
                Start practice
              </Link>
            </div>
          </div>
        </div>
      </main>
    </Layout>
  );
}
