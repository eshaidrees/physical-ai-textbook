import React from 'react';
import { useUserPreferences } from '../contexts/UserPreferencesContext';

const PersonalizedDashboard = () => {
  const {
    preferences,
    progress,
    markChapterCompleted,
    markChapterIncomplete,
    isChapterCompleted,
    addInterest,
    removeInterest
  } = useUserPreferences();

  // Sample chapter data for demonstration
  const chapters = [
    { id: 'intro-to-physical-ai', title: 'Introduction to Physical AI' },
    { id: 'robotics', title: 'Basics of Humanoid Robotics' },
    { id: 'ros-fundamentals', title: 'ROS 2 Fundamentals' },
    { id: 'digital-twin-simulation', title: 'Digital Twin Simulation' },
    { id: 'vision-language-action', title: 'Vision-Language-Action Systems' },
    { id: 'capstone', title: 'Capstone: Simple AI-Robot Pipeline' }
  ];

  // Calculate progress percentage
  const progressPercentage = Math.round((preferences.completedChapters.length / chapters.length) * 100);

  // Sample interests for the user to choose from
  const availableInterests = [
    'Physical AI', 'Humanoid Robotics', 'ROS 2', 'Simulation',
    'Computer Vision', 'Natural Language Processing', 'Control Systems'
  ];

  return (
    <div className="personalized-dashboard">
      <div className="dashboard-section">
        <h3>Your Learning Progress</h3>
        <div className="progress-container">
          <div className="progress-bar">
            <div
              className="progress-fill"
              style={{ width: `${progressPercentage}%` }}
            ></div>
          </div>
          <div className="progress-text">{progressPercentage}% Complete</div>
        </div>
        <div className="chapters-list">
          <h4>Chapters:</h4>
          {chapters.map((chapter) => (
            <div key={chapter.id} className="chapter-item">
              <span className="chapter-title">{chapter.title}</span>
              <div className="chapter-actions">
                <button
                  className={`status-btn ${isChapterCompleted(chapter.id) ? 'completed' : 'incomplete'}`}
                  onClick={() =>
                    isChapterCompleted(chapter.id)
                      ? markChapterIncomplete(chapter.id)
                      : markChapterCompleted(chapter.id)
                  }
                >
                  {isChapterCompleted(chapter.id) ? 'Completed' : 'Mark Complete'}
                </button>
              </div>
            </div>
          ))}
        </div>
      </div>

      <div className="dashboard-section">
        <h3>Your Interests</h3>
        <div className="interests-list">
          {preferences.interests.map((interest) => (
            <div key={interest} className="interest-tag">
              {interest}
              <button
                className="remove-interest"
                onClick={() => removeInterest(interest)}
              >
                ×
              </button>
            </div>
          ))}
          {preferences.interests.length === 0 && (
            <p className="no-interests">No interests selected yet.</p>
          )}
        </div>
        <div className="add-interests">
          <h4>Add Interests:</h4>
          <div className="interest-options">
            {availableInterests
              .filter(interest => !preferences.interests.includes(interest))
              .map((interest) => (
                <button
                  key={interest}
                  className="interest-option"
                  onClick={() => addInterest(interest)}
                >
                  {interest}
                </button>
              ))}
          </div>
        </div>
      </div>

      <div className="dashboard-section">
        <h3>Learning Path</h3>
        <div className="learning-path-selection">
          <button
            className={`path-btn ${preferences.learningPath === 'beginner' ? 'active' : ''}`}
            onClick={() => {}}
            disabled
          >
            Beginner
          </button>
          <button
            className={`path-btn ${preferences.learningPath === 'intermediate' ? 'active' : ''}`}
            onClick={() => {}}
            disabled
          >
            Intermediate
          </button>
          <button
            className={`path-btn ${preferences.learningPath === 'advanced' ? 'active' : ''}`}
            onClick={() => {}}
            disabled
          >
            Advanced
          </button>
        </div>
        <p className="path-description">
          Your learning path is set to <strong>{preferences.learningPath}</strong>.
          This affects the difficulty level and depth of explanations.
        </p>
      </div>

      <style jsx>{`
        .personalized-dashboard {
          max-width: 800px;
          margin: 0 auto;
          padding: 1rem;
        }

        .dashboard-section {
          margin-bottom: 2rem;
          padding: 1.5rem;
          border: 1px solid var(--ifm-color-emphasis-300);
          border-radius: 8px;
          background-color: var(--ifm-background-surface-color);
        }

        .dashboard-section h3 {
          margin-top: 0;
          color: var(--ifm-color-primary);
        }

        .progress-container {
          display: flex;
          align-items: center;
          gap: 1rem;
          margin-bottom: 1rem;
        }

        .progress-bar {
          flex: 1;
          height: 20px;
          background-color: var(--ifm-color-emphasis-200);
          border-radius: 10px;
          overflow: hidden;
        }

        .progress-fill {
          height: 100%;
          background-color: var(--ifm-color-primary);
          transition: width 0.3s ease;
        }

        .progress-text {
          font-weight: bold;
          min-width: 60px;
        }

        .chapters-list h4 {
          margin-bottom: 0.5rem;
        }

        .chapter-item {
          display: flex;
          justify-content: space-between;
          align-items: center;
          padding: 0.5rem 0;
          border-bottom: 1px solid var(--ifm-color-emphasis-200);
        }

        .chapter-item:last-child {
          border-bottom: none;
        }

        .chapter-title {
          flex: 1;
        }

        .status-btn {
          padding: 0.25rem 0.75rem;
          border: 1px solid var(--ifm-color-emphasis-400);
          border-radius: 4px;
          background: none;
          cursor: pointer;
        }

        .status-btn:hover {
          background-color: var(--ifm-color-emphasis-200);
        }

        .status-btn.completed {
          background-color: #d4edda;
          border-color: #28a745;
          color: #28a745;
        }

        .interests-list {
          margin-bottom: 1rem;
        }

        .interest-tag {
          display: inline-block;
          background-color: var(--ifm-color-primary-lightest);
          color: var(--ifm-color-primary-darkest);
          padding: 0.25rem 0.75rem;
          border-radius: 20px;
          margin: 0.25rem;
          font-size: 0.85rem;
        }

        .remove-interest {
          background: none;
          border: none;
          color: #dc3545;
          cursor: pointer;
          margin-left: 0.25rem;
          font-size: 1.2rem;
        }

        .no-interests {
          color: var(--ifm-color-emphasis-600);
          font-style: italic;
        }

        .add-interests h4 {
          margin-bottom: 0.5rem;
        }

        .interest-options {
          display: flex;
          flex-wrap: wrap;
          gap: 0.5rem;
        }

        .interest-option {
          padding: 0.25rem 0.75rem;
          border: 1px solid var(--ifm-color-emphasis-400);
          border-radius: 20px;
          background: none;
          cursor: pointer;
          font-size: 0.85rem;
        }

        .interest-option:hover {
          background-color: var(--ifm-color-emphasis-200);
        }

        .learning-path-selection {
          display: flex;
          gap: 1rem;
          margin-bottom: 1rem;
        }

        .path-btn {
          padding: 0.5rem 1rem;
          border: 1px solid var(--ifm-color-emphasis-400);
          background: none;
          cursor: pointer;
          border-radius: 4px;
        }

        .path-btn:hover:not(:disabled) {
          background-color: var(--ifm-color-emphasis-200);
        }

        .path-btn.active {
          background-color: var(--ifm-color-primary);
          color: white;
          border-color: var(--ifm-color-primary);
        }

        .path-btn:disabled {
          opacity: 0.6;
          cursor: not-allowed;
        }

        .path-description {
          font-size: 0.9rem;
          color: var(--ifm-color-emphasis-700);
        }
      `}</style>
    </div>
  );
};

export default PersonalizedDashboard;