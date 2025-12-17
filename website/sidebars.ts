import type {SidebarsConfig} from '@docusaurus/plugin-content-docs';

// This runs in Node.js - Don't use client-side code here (browser APIs, JSX...)

/**
 * Creating a sidebar enables you to:
 - create an ordered group of docs
 - render a sidebar for each doc of that group
 - provide next/previous navigation

 The sidebars can be generated from the filesystem, or explicitly defined here.

 Create as many sidebars as you want.
 */
const sidebars: SidebarsConfig = {
  // Manual sidebar configuration for the textbook
  tutorialSidebar: [
    'intro',
    {
      type: 'category',
      label: 'Chapter 1: Introduction to Physical AI',
      items: ['intro-to-physical-ai/index'],
    },
    {
      type: 'category',
      label: 'Chapter 2: Basics of Humanoid Robotics',
      items: ['robotics/anatomy'],
    },
    {
      type: 'category',
      label: 'Chapter 3: ROS 2 Fundamentals',
      items: ['ros-fundamentals/architecture'],
    },
    {
      type: 'category',
      label: 'Chapter 4: Digital Twin Simulation (Gazebo + Isaac)',
      items: ['digital-twin-simulation/environment-overview'],
    },
    {
      type: 'category',
      label: 'Chapter 5: Vision-Language-Action Systems',
      items: ['vision-language-action/multimodal-ai'],
    },
    {
      type: 'category',
      label: 'Chapter 6: Capstone - Simple AI-Robot Pipeline',
      items: ['capstone/integration'],
    },
    {
      type: 'category',
      label: 'AI Chatbot',
      items: ['chat'],
    }
  ],
};

export default sidebars;
