import clsx from 'clsx';
import Heading from '@theme/Heading';
import styles from './styles.module.css';
import { useColorMode } from '@docusaurus/theme-common';

const FeatureList = [
    {
        title: 'By students, for students.',
        imgSrc: require('@site/static/img/helping-light.png').default, // Add .default for webpack to get URL
        imgSrcDark: require('@site/static/img/helping-dark.png').default,
        description: (
            <>
                We know physics can be confusing — so we made this site to make it make sense. 
                Here you'll find easy-to-understand lessons and resources all about electricity and magnetism, 
                written by students just like you. 
            </>
        ),
    },
    {
        title: 'Full of useful resources.',
        imgSrc: require('@site/static/img/equation-light.png').default,
        imgSrcDark: require('@site/static/img/equation-dark.png').default,
        description: (
            <>
                From explanations and practice questions to videos and formula sheets — 
                everything you need to tackle electricity and magnetism is right here. 
                Feel free to use whatever you need.
            </>
        ),
    },
    {
        title: 'Active support and infrastructure.',
        imgSrc: require('@site/static/img/circuit-light.png').default,
        imgSrcDark: require('@site/static/img/circuit-dark.png').default,
        description: (
            <>
                This site is developed and managed by Shuban Pal, Aashray Reddy, and Trevor Huang. We are committed to keeping it up-to-date and useful. Please feel free to reach out to us with any questions, suggestions, or feedback.
            </>
        ),
    },
];

function Feature({ imgSrc, imgSrcDark, title, description }) {
    const { colorMode } = useColorMode();
    const image = colorMode === 'dark' ? imgSrcDark : imgSrc;

    return (
        <div className={clsx('col col--4')}>
            <div className="text--center">
                <img className={styles.featureSvg} src={image} alt={title} />
            </div>
            <div className="text--center padding-horiz--md">
                <Heading as="h3">{title}</Heading>
                <p className="text--justify">{description}</p>
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
