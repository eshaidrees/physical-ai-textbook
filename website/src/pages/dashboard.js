import React from 'react';
import Layout from '@theme/Layout';
import PersonalizedDashboard from '../components/PersonalizedDashboard';
import Recommendations from '../components/Recommendations';

function DashboardPage() {
  return (
    <Layout
      title="Personalized Learning Dashboard"
      description="Your personalized dashboard for the Physical AI & Humanoid Robotics textbook">
      <div className="container margin-vert--lg">
        <div className="row">
          <div className="col col--12">
            <h1>Personalized Learning Dashboard</h1>
            <p>
              Track your progress, manage your interests, and get personalized recommendations
              for your learning journey in Physical AI & Humanoid Robotics.
            </p>

            <Recommendations />

            <PersonalizedDashboard />
          </div>
        </div>
      </div>
    </Layout>
  );
}

export default DashboardPage;