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
  // By default, Docusaurus generates a sidebar from the docs folder structure
  tutorialSidebar: [
    'intro',
    {
      type: 'category',
      label: 'Module 1: The Robotic Nervous System (ROS 2)',
      items: [
        'ros2-nervous-system/intro',
        'ros2-nervous-system/chapter-1-embodied-intelligence',
        'ros2-nervous-system/chapter-2-communication-patterns',
        'ros2-nervous-system/chapter-3-ai-robot-bridge',
      ],
    },
    {
      type: 'category',
      label: 'Module 2: The Digital Twin (Gazebo & Unity)',
      items: [
        'digital-twin-simulation/intro',
        'digital-twin-simulation/chapter-1-digital-twins',
        'digital-twin-simulation/chapter-2-environment-building',
        'digital-twin-simulation/chapter-3-sensor-simulation',
      ],
    },
    {
      type: 'category',
      label: 'Module 3: The AI-Robot Brain (NVIDIA Isaac™)',
      items: [
        'ai-robot-brain-isaac/intro',
        'ai-robot-brain-isaac/chapter-1-isaac-sim',
        'ai-robot-brain-isaac/chapter-2-hardware-accelerated-perception',
        'ai-robot-brain-isaac/chapter-3-navigation-nav2',
      ],
    },
    {
      type: 'category',
      label: 'Module 4: Vision-Language-Action (VLA)',
      items: [
        'vision-language-action-vla/intro',
        'vision-language-action-vla/chapter-1-vla-systems',
        'vision-language-action-vla/chapter-2-voice-to-action',
        'vision-language-action-vla/chapter-3-autonomous-humanoid',
      ],
    },
  ],

  // But you can create a sidebar manually
  /*
  tutorialSidebar: [
    'intro',
    'hello',
    {
      type: 'category',
      label: 'Tutorial',
      items: ['tutorial-basics/create-a-document'],
    },
  ],
   */
};

export default sidebars;
