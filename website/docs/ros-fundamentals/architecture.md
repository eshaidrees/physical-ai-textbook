# ROS 2 Architecture and Concepts

The Robot Operating System 2 (ROS 2) provides a flexible framework for developing robot applications. This chapter covers the fundamental architecture and concepts that form the foundation of ROS 2.

## ROS 2 Overview

ROS 2 is a collection of software frameworks for robot software development. It provides:

- Hardware abstraction
- Device drivers
- Libraries for implementing common robot functionality
- Message-passing between processes
- Package management

## Core Architecture

### Nodes
Nodes are processes that perform computation. In ROS 2:

- Each node runs a specific task or function
- Nodes communicate with each other through topics, services, and actions
- Nodes can be written in different programming languages (C++, Python, etc.)

### Topics and Publishers/Subscribers
Topics enable asynchronous message passing between nodes:

- Publishers send messages to topics
- Subscribers receive messages from topics
- Multiple publishers and subscribers can use the same topic
- Communication is decoupled in time and space

### Services
Services enable synchronous request/response communication:

- A service client sends a request
- A service server processes the request and sends a response
- Useful for operations that require a specific response

### Actions
Actions provide a way to send goals to servers and receive feedback:

- Used for long-running tasks
- Supports preemption (canceling in-progress goals)
- Provides feedback during execution
- Reports results upon completion

## Communication Patterns

### Publisher-Subscriber Pattern
The publisher-subscriber pattern enables decoupled communication:

```python
# Publisher example
publisher = node.create_publisher(String, 'topic_name', 10)

# Subscriber example
subscriber = node.create_subscription(String, 'topic_name', callback, 10)
```

### Client-Server Pattern
The client-server pattern enables synchronous communication:

```python
# Service server example
service = node.create_service(AddTwoInts, 'add_two_ints', handle_add_two_ints)

# Service client example
client = node.create_client(AddTwoInts, 'add_two_ints')
```

## Quality of Service (QoS)

QoS settings allow customization of communication behavior:

- Reliability: Best effort or reliable delivery
- Durability: Volatile or transient local durability
- History: Keep last N messages or keep all messages
- Rate limits: Maximum rate for message delivery

## Package Management

### Packages
ROS 2 packages contain:

- Source code
- Dependencies
- Build instructions
- Launch files
- Configuration files

### Package Structure
A typical ROS 2 package includes:

```
package_name/
├── CMakeLists.txt      # Build instructions for C++
├── package.xml         # Package metadata
├── src/                # Source code
├── include/            # Header files
├── launch/             # Launch files
├── config/             # Configuration files
└── test/               # Unit tests
```

## Build System

ROS 2 uses the `colcon` build system:

- `colcon build` - Compiles packages
- `colcon test` - Runs tests
- `colcon clean` - Removes build artifacts

## Launch Files

Launch files allow starting multiple nodes simultaneously:

```xml
<launch>
  <node pkg="package_name" exec="executable_name" name="node_name">
    <param name="param_name" value="param_value"/>
  </node>
</launch>
```

## Parameter Management

Parameters allow configuration of nodes at runtime:

- Parameters can be set at launch time
- Parameters can be changed dynamically
- Parameter files can store configuration values

## Tools and Utilities

### Command Line Tools
- `ros2 run` - Execute a node
- `ros2 topic` - Interact with topics
- `ros2 service` - Interact with services
- `ros2 action` - Interact with actions
- `ros2 param` - Manage parameters

### Visualization Tools
- RViz - 3D visualization tool
- rqt - GUI plugin framework
- ros2 bag - Data recording and playback

## Security Features

ROS 2 includes security features:

- Authentication of nodes
- Authorization of communication
- Encryption of data

## Migration from ROS 1

Key differences from ROS 1:

- DDS (Data Distribution Service) as the underlying middleware
- Improved real-time support
- Better multi-robot support
- Enhanced security features

## Summary

ROS 2 provides a comprehensive framework for robot software development. Understanding its architecture and concepts is essential for building effective robotic applications. The modular design allows for flexible system composition while maintaining standard interfaces for interoperability.