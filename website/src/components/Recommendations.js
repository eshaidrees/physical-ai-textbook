import React from 'react';
import { useUserPreferences } from '../contexts/UserPreferencesContext';

const Recommendations = () => {
  const { preferences } = useUserPreferences();

  // Sample recommendations based on user interests and progress
  const generateRecommendations = () => {
    const recs = [];

    // If user is interested in ROS, recommend ROS chapter if not completed
    if (preferences.interests.includes('ROS 2') && !preferences.completedChapters.includes('ros-fundamentals')) {
      recs.push({
        title: 'ROS 2 Fundamentals',
        link: '/docs/ros-fundamentals/architecture',
        reason: 'Based on your interest in ROS 2',
        type: 'chapter'
      });
    }

    // If user is interested in Computer Vision, recommend related content
    if (preferences.interests.includes('Computer Vision') && !preferences.completedChapters.includes('vision-language-action')) {
      recs.push({
        title: 'Vision-Language-Action Systems',
        link: '/docs/vision-language-action/multimodal-ai',
        reason: 'Based on your interest in Computer Vision',
        type: 'chapter'
      });
    }

    // If user is interested in Simulation, recommend related content
    if (preferences.interests.includes('Simulation') && !preferences.completedChapters.includes('digital-twin-simulation')) {
      recs.push({
        title: 'Digital Twin Simulation (Gazebo + Isaac)',
        link: '/docs/digital-twin-simulation/environment-overview',
        reason: 'Based on your interest in Simulation',
        type: 'chapter'
      });
    }

    // If user has completed the introduction, recommend next logical chapter
    if (preferences.completedChapters.includes('intro-to-physical-ai') && !preferences.completedChapters.includes('robotics')) {
      recs.push({
        title: 'Basics of Humanoid Robotics',
        link: '/docs/robotics/anatomy',
        reason: 'Next logical step after introduction',
        type: 'chapter'
      });
    }

    // If user is on an advanced learning path and has completed basic chapters
    if (preferences.learningPath === 'advanced' &&
        preferences.completedChapters.includes('intro-to-physical-ai') &&
        preferences.completedChapters.includes('robotics') &&
        !preferences.completedChapters.includes('capstone')) {
      recs.push({
        title: 'Capstone: Simple AI-Robot Pipeline',
        link: '/docs/capstone/integration',
        reason: 'Advanced integration project',
        type: 'chapter'
      });
    }

    // Default recommendations if no specific ones apply
    if (recs.length === 0) {
      recs.push({
        title: 'Introduction to Physical AI',
        link: '/docs/intro-to-physical-ai/index',
        reason: 'Start with the fundamentals',
        type: 'chapter'
      });

      if (!preferences.completedChapters.includes('intro-to-physical-ai')) {
        recs.push({
          title: 'Basics of Humanoid Robotics',
          link: '/docs/robotics/anatomy',
          reason: 'Follows the introduction',
          type: 'chapter'
        });
      }
    }

    return recs.slice(0, 3); // Limit to 3 recommendations
  };

  const recommendations = generateRecommendations();

  return (
    <div className="recommendations-section">
      <h3>Recommended for You</h3>
      <p>Based on your interests and learning progress</p>
      <div className="recommendations-list">
        {recommendations.map((rec, index) => (
          <div key={index} className="recommendation-card">
            <h4>
              <a href={rec.link}>{rec.title}</a>
            </h4>
            <p className="recommendation-reason">{rec.reason}</p>
            <span className="recommendation-type">{rec.type}</span>
          </div>
        ))}
      </div>

      <style jsx>{`
        .recommendations-section {
          margin: 2rem 0;
          padding: 1.5rem;
          border: 1px solid var(--ifm-color-emphasis-300);
          border-radius: 8px;
          background-color: var(--ifm-color-emphasis-100);
        }

        .recommendations-section h3 {
          margin-top: 0;
          color: var(--ifm-color-primary);
        }

        .recommendations-list {
          display: grid;
          gap: 1rem;
        }

        .recommendation-card {
          padding: 1rem;
          border: 1px solid var(--ifm-color-emphasis-300);
          border-radius: 6px;
          background-color: var(--ifm-background-surface-color);
        }

        .recommendation-card h4 {
          margin: 0 0 0.5rem 0;
        }

        .recommendation-card h4 a {
          color: var(--ifm-color-primary);
          text-decoration: none;
        }

        .recommendation-card h4 a:hover {
          text-decoration: underline;
        }

        .recommendation-reason {
          margin: 0.5rem 0;
          font-size: 0.9rem;
          color: var(--ifm-color-emphasis-700);
        }

        .recommendation-type {
          display: inline-block;
          padding: 0.25rem 0.5rem;
          background-color: var(--ifm-color-primary-lightest);
          color: var(--ifm-color-primary-darkest);
          border-radius: 4px;
          font-size: 0.75rem;
          font-weight: bold;
        }
      `}</style>
    </div>
  );
};

export default Recommendations;