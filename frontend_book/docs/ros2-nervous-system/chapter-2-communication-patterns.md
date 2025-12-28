---
sidebar_position: 2
title: 'Chapter 2: Communication in Humanoid Robots — Nodes, Topics, and Services'
---

# Chapter 2: Communication in Humanoid Robots — Nodes, Topics, and Services

## ROS 2 Nodes and Lifecycle

In ROS 2, nodes represent individual processes that perform computational tasks within the robotic system. Each node encapsulates a specific functionality and communicates with other nodes to achieve complex behaviors in humanoid robots.

### Node Characteristics
- **Process Isolation**: Each node runs as a separate process, providing fault isolation
- **Language Independence**: Nodes can be written in different programming languages (C++, Python, etc.)
- **Resource Management**: Each node manages its own resources and computational load
- **Lifecycle Management**: Nodes can be configured with lifecycle states for complex initialization and shutdown procedures

### Lifecycle States
ROS 2 provides a lifecycle system for nodes that includes:
- **Unconfigured**: Node created but not yet configured
- **Inactive**: Node configured but not yet activated
- **Active**: Node is fully operational
- **Finalized**: Node has been shut down

This lifecycle management is particularly important in humanoid robots where safety and proper initialization sequences are critical.

## Topics and Asynchronous Message Passing

Topics are the primary mechanism for asynchronous communication in ROS 2. They enable one-to-many communication patterns where publishers send messages to subscribers without direct coordination.

### Topic Communication
- **Publishers**: Nodes that send messages to a topic
- **Subscribers**: Nodes that receive messages from a topic
- **Message Types**: Strongly typed messages defined in `.msg` files
- **QoS (Quality of Service)**: Configurable policies for reliability, durability, and performance

### Use Cases in Humanoid Robots
- **Sensor Data**: Camera images, LIDAR scans, IMU data
- **Control Commands**: Joint position, velocity, or torque commands
- **State Information**: Robot pose, battery level, system status
- **Perception Results**: Detected objects, recognized speech, planned paths

## Services and Request-Response Patterns

Services provide synchronous, request-response communication patterns in ROS 2. Unlike topics, services establish a direct connection between a client and a server for specific requests.

### Service Communication
- **Service Server**: Node that provides a specific service
- **Service Client**: Node that requests the service
- **Request/Response Types**: Strongly typed defined in `.srv` files
- **Synchronous**: Client waits for the server's response

### Use Cases in Humanoid Robots
- **Calibration**: Requesting sensor or actuator calibration
- **Planning Services**: Requesting path planning for specific goals
- **Configuration**: Changing robot parameters or settings
- **Status Queries**: Requesting detailed system status information

## Real Humanoid Use Cases (Movement, Sensors, Commands)

### Movement Coordination
In humanoid robots, multiple nodes coordinate to achieve complex movements:
- **High-level Planner**: Determines desired motion goals
- **Trajectory Generator**: Creates detailed movement trajectories
- **Controller**: Executes the trajectories on robot joints
- **Feedback System**: Monitors actual motion and adjusts as needed

### Sensor Integration
Humanoid robots integrate multiple sensor systems:
- **Vision System**: Camera feeds processed by perception nodes
- **Tactile Sensors**: Touch feedback from hands and feet
- **Inertial Measurement**: Balance and orientation data
- **Audio System**: Speech recognition and sound localization

### Command Execution
Command execution involves multiple coordination patterns:
- **Safety Monitoring**: Continuous checking of robot state
- **Task Sequencing**: Coordinating multiple sequential actions
- **Error Handling**: Managing failures and exceptions gracefully

## Conceptual Introduction to Actions (High Level)

Actions represent a third communication pattern in ROS 2, designed for long-running tasks that require feedback and goal management. Actions combine aspects of both topics and services:

- **Goal**: Request for a long-running task to be performed
- **Feedback**: Continuous updates on task progress
- **Result**: Final outcome when the task completes

In humanoid robots, actions are used for:
- **Navigation**: Moving to specific locations with continuous feedback
- **Manipulation**: Complex object handling tasks
- **Behavior Execution**: Multi-step behavioral sequences
- **Learning Tasks**: Long-running machine learning processes

Actions provide the coordination needed for complex humanoid behaviors that require both immediate responses and long-term progress tracking.

This chapter has explored the communication patterns that enable ROS 2 to function as a robotic nervous system. The next chapter will examine how AI agents connect to these communication patterns to control humanoid robots.