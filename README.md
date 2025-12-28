# Physical AI and Humanoid Robotics Book

This repository contains the source for the Physical AI and Humanoid Robotics Book, an educational resource for AI engineers, software developers, and robotics students entering Physical AI and humanoid robotics.

## Documentation Modules

### Module 1: The Robotic Nervous System (ROS 2)
This module covers ROS 2 as the core middleware enabling communication between AI software and humanoid robot hardware (embodied intelligence). It includes:

- Chapter 1: ROS 2 and Embodied Intelligence
- Chapter 2: Communication in Humanoid Robots — Nodes, Topics, and Services
- Chapter 3: Bridging Python AI Agents to Robot Bodies

### Module 2: The Digital Twin (Gazebo & Unity)
This module covers building and using digital twins to simulate humanoid robots, physical laws, environments, and sensors before real-world deployment. It includes:

- Chapter 1: Digital Twins and Physics-Based Simulation
- Chapter 2: Environment Building with Gazebo and Unity
- Chapter 3: Simulating Robot Sensors

### Module 3: The AI-Robot Brain (NVIDIA Isaac™)
This module covers using NVIDIA Isaac to train, perceive, and navigate humanoid robots through photorealistic simulation and hardware-accelerated robotics pipelines. It includes:

- Chapter 1: NVIDIA Isaac Sim and Synthetic Data
- Chapter 2: Isaac ROS and Hardware-Accelerated Perception
- Chapter 3: Navigation and Path Planning with Nav2

### Module 4: Vision-Language-Action (VLA)
This module covers the convergence of large language models, speech, vision, and robotics to enable high-level human-to-robot interaction and autonomous task execution. It includes:

- Chapter 1: Vision-Language-Action Systems in Robotics
- Chapter 2: Voice-to-Action with Speech and LLMs
- Chapter 3: Capstone — The Autonomous Humanoid

## Structure

- `frontend_book/` - Docusaurus-based documentation site
- `specs/` - Feature specifications and plans
- `history/` - Prompt history records

## Getting Started

To run the documentation site locally:

1. Navigate to the `frontend_book` directory
2. Install dependencies: `npm install`
3. Start the development server: `npm start`

## Building for Production

To build the site for deployment:

1. Navigate to the `frontend_book` directory
2. Run: `npm run build`

The site is configured for GitHub Pages deployment.