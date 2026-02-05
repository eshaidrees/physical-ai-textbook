import clsx from 'clsx';
import Link from '@docusaurus/Link';
import Heading from '@theme/Heading';
import styles from './styles.module.css';

const ModuleList = [
  {
    title: 'ROS 2 - Robotic Nervous System',
    description: 'Learn ROS 2 fundamentals, nodes, topics, and communication patterns for robot systems.',
    icon: '🤖',
    to: '/docs/module-1-ros/',
  },
  {
    title: 'Digital Twin - Gazebo & Unity',
    description: 'Create physics-accurate simulation environments for safe robot testing and development.',
    icon: '🎮',
    to: '/docs/module-2-simulation/digital-twin',
  },
  {
    title: 'AI Robot Brain - NVIDIA Isaac',
    description: 'Implement AI navigation, perception, and decision-making for autonomous robot behavior.',
    icon: '🧠',
    to: '/docs/module-3-ai/vslam-navigation',
  },
  {
    title: 'Vision-Language-Action (VLA)',
    description: 'Integrate vision, language, and action systems for intelligent human-robot interaction.',
    icon: '👁️',
    to: '/docs/module-4-vla/llm-planning',
  },
  {
    title: 'Capstone Project',
    description: 'Apply all concepts in a comprehensive autonomous humanoid robot project.',
    icon: '🎓',
    to: '/docs/capstone/',
  },
];

function ModuleCard({ module }) {
  return (
    <Link to={module.to} className={styles.moduleCardLink}>
      <div className={styles.moduleCard}>
        <div className={styles.moduleIcon}>{module.icon}</div>
        <Heading as="h3" className={styles.moduleTitle}>
          {module.title}
        </Heading>
        <p className={styles.moduleDescription}>
          {module.description}
        </p>
        <div className={styles.moduleCta}>
          Explore Module →
        </div>
      </div>
    </Link>
  );
}

export default function ModulesSection() {
  return (
    <section className={styles.modulesSection}>
      <div className="container">
        <div className="row">
          <div className="col col--12">
            <Heading as="h2" className={styles.modulesTitle}>
              Learning Modules
            </Heading>
            <p className={styles.modulesSubtitle}>
              Master the essential components of Physical AI and Humanoid Robotics
            </p>
          </div>
        </div>
        <div className="row">
          {ModuleList.map((module, index) => (
            <div key={index} className="col col--4 margin-bottom--lg">
              <ModuleCard module={module} />
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}