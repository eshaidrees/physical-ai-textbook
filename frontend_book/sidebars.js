// @ts-check

/** @type {import('@docusaurus/plugin-content-docs').SidebarsConfig} */
const sidebars = {
  tutorialSidebar: [
    'intro',
    {
      type: 'category',
      label: 'Module 1: ROS 2 - Robotic Nervous System',
      items: [
        'module-1-ros/index',
        'module-1-ros/ros-nodes-topics',
        'module-1-ros/rclpy-control',
        'module-1-ros/urdf-modeling',
      ],
    },
    {
      type: 'category',
      label: 'Module 2: Digital Twin - Gazebo & Unity',
      items: [
        'module-2-simulation/index',
        'module-2-simulation/gazebo-simulation',
        'module-2-simulation/unity-visualization',
        'module-2-simulation/digital-twin',
      ],
    },
    {
      type: 'category',
      label: 'Module 3: AI Robot Brain - NVIDIA Isaac',
      items: [
        'module-3-ai/index',
        'module-3-ai/vslam-navigation',
        'module-3-ai/isaac-sim',
        'module-3-ai/nav2-planning',
      ],
    },
    {
      type: 'category',
      label: 'Module 4: Vision-Language-Action (VLA)',
      items: [
        'module-4-vla/index',
        'module-4-vla/whisper-voice',
        'module-4-vla/natural-language-interface',
        'module-4-vla/llm-planning',
        'module-4-vla/ros-execution',
        'module-4-vla/action-planning-integration',
      ],
    },
    {
      type: 'category',
      label: 'Capstone Project',
      items: [
        'capstone/index',
        'capstone/autonomous-robot',
      ],
    },
  ],
};

export default sidebars;