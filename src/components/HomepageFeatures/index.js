import clsx from 'clsx';
import Heading from '@theme/Heading';
import styles from './styles.module.css';

const FeatureList = [
    {
        title: 'By students, for students.',
        imgSrc: require('@site/static/img/help.png').default, // Add .default for webpack to get URL
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
        imgSrc: require('@site/static/img/resources.png').default,
        description: (
            <>
                
                From explanations and practice questions to videos and formula sheets — 
                everything you need to tackle electricity and magnetism is right here. 
                Feel free to use whatever you need.
            </>
        ),
    },
    {
        title: 'E&M Might Be About Electric Type Pokémon',
        imgSrc: require('@site/static/img/pokemon-minun-and-plusle-pack.png').default,
        description: (
            <>
                In the year 2040, the 3rd FRQ of the AP Physics E&M exam will be about Pikachu and other electric type Pokémon.
            </>
        ),
    },
];

function Feature({ imgSrc, title, description }) {
    return (
        <div className={clsx('col col--4')}>
            <div className="text--center">
                <img className={styles.featureSvg} src={imgSrc} alt={title} />
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
