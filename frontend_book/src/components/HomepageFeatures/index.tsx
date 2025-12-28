import type {ReactNode} from 'react';
import clsx from 'clsx';
import Heading from '@theme/Heading';
import styles from './styles.module.css';

type FeatureItem = {
  title: string;
  Svg: React.ComponentType<React.ComponentProps<'svg'>>;
  description: ReactNode;
};

const FeatureList: FeatureItem[] = [
  {
    title: 'Physical AI',
    Svg: require('@site/static/img/humanoid-robot.svg').default,
    description: (
      <>
        Explore the fundamentals of Physical AI - the integration of artificial intelligence
        with physical systems and robotics. Learn how AI algorithms control real-world
        mechanical systems.
      </>
    ),
  },
  {
    title: 'Digital Twin',
    Svg: require('@site/static/img/neural-network.svg').default,
    description: (
      <>
        Understand digital twin technology in robotics - virtual replicas of physical
        robots that enable simulation, testing, and optimization before real-world deployment.
      </>
    ),
  },
  {
    title: 'AI-Robot Brain',
    Svg: require('@site/static/img/robot-icon.svg').default,
    description: (
      <>
        Discover the cognitive architecture of AI-powered robots, including perception,
        decision-making, and action execution systems that enable autonomous behavior.
      </>
    ),
  },
];

function Feature({title, Svg, description}: FeatureItem) {
  // Map titles to their corresponding doc paths
  const getDocPath = (title: string) => {
    switch(title) {
      case 'Physical AI':
        return '/docs/ros2-nervous-system';
      case 'Digital Twin':
        return '/docs/digital-twin-simulation';
      case 'AI-Robot Brain':
        return '/docs/ai-robot-brain-isaac';
      default:
        return '/docs/intro';
    }
  };

  const docPath = getDocPath(title);

  return (
    <a
      href={docPath}
      className={clsx('col col--4', styles.featureLink)}
      aria-label={`Learn more about ${title}`}
    >
      <div className="text--center">
        <Svg className={styles.featureSvg} role="img" aria-label={`${title} icon`} />
      </div>
      <div className="text--center padding-horiz--md">
        <Heading as="h3">{title}</Heading>
        <p>{description}</p>
      </div>
    </a>
  );
}

export default function HomepageFeatures(): ReactNode {
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
