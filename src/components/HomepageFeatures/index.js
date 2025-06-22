import clsx from 'clsx';
import Heading from '@theme/Heading';
import styles from './styles.module.css';

const FeatureList = [
  {
    title: 'Hey there!',
    Svg: require('@site/static/img/undraw_docusaurus_mountain.svg').default,
    description: (
      <>
        Go to <code>src\components\HomepageFeatures\index.js</code> to change this text.
        You can also change the descriptions and the svg images (the images above).
      </>
    ),
  },
  {
    title: 'Swag title goes here',
    Svg: require('@site/static/img/undraw_docusaurus_tree.svg').default,
    description: (
      <>
        It might be <code>src/components/HomepageFeatures/index.js</code> on non Windows systems.
        Either way, the file should be named <code>index.js</code>.
      </>
    ),
  },
  {
    title: 'I can\'t think of a funny joke here',
    Svg: require('@site/static/img/undraw_docusaurus_react.svg').default,
    description: (
      <>
        You could also probably <code>Ctrl + F</code> for this text or find <code>index.js</code>.
      </>
    ),
  },
];

function Feature({Svg, title, description}) {
  return (
    <div className={clsx('col col--4')}>
      <div className="text--center">
        <Svg className={styles.featureSvg} role="img" />
      </div>
      <div className="text--center padding-horiz--md">
        <Heading as="h3">{title}</Heading>
        <p>{description}</p>
      </div>
    </div>
  );
}

export default function HomepageFeatures() {
  return (
    <section className={styles.features}>
      <div className="container">
        <div className="row">
          {FeatureList.map((props, idx) => (
            <Feature key={idx} {...props} />
          ))}
        </div>
      </div>
    </section>
  );
}
