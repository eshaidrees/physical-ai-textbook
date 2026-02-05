---
sidebar_position: 3
---

# Python Control with rclpy

This section focuses on controlling robots using Python with the `rclpy` library, which is the Python client library for ROS 2. You'll learn how to create nodes, handle parameters, and control robot hardware from Python scripts.

## Introduction to rclpy

`rclpy` provides Python bindings for ROS 2, allowing you to write ROS 2 nodes in Python. It's particularly useful for rapid prototyping, testing, and applications where Python's ecosystem provides advantages.

## Basic Node Structure

Every `rclpy` node follows a similar structure:

```python
import rclpy
from rclpy.node import Node

class RobotController(Node):
    def __init__(self):
        super().__init__('robot_controller')
        # Initialize publishers, subscribers, services, etc.
        self.get_logger().info('Robot Controller node initialized')

def main(args=None):
    rclpy.init(args=args)
    node = RobotController()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
```

## Working with Parameters

Parameters allow you to configure your node without recompiling:

```python
import rclpy
from rclpy.node import Node

class ParameterNode(Node):
    def __init__(self):
        super().__init__('parameter_node')

        # Declare parameters with default values
        self.declare_parameter('robot_name', 'humanoid_robot')
        self.declare_parameter('max_speed', 1.0)
        self.declare_parameter('safety_distance', 0.5)

        # Access parameter values
        self.robot_name = self.get_parameter('robot_name').value
        self.max_speed = self.get_parameter('max_speed').value
        self.safety_distance = self.get_parameter('safety_distance').value

        self.get_logger().info(f'Robot: {self.robot_name}, Max Speed: {self.max_speed}')

def main(args=None):
    rclpy.init(args=args)
    node = ParameterNode()
    rclpy.spin_once(node, timeout_sec=1)  # Run once to log parameters
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
```

## Robot Movement Control

Here's an example of controlling a robot's movement using Twist messages:

```python
import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist

class MovementController(Node):
    def __init__(self):
        super().__init__('movement_controller')

        # Create publisher for cmd_vel topic
        self.cmd_vel_publisher = self.create_publisher(Twist, 'cmd_vel', 10)

        # Create a timer to send commands periodically
        self.timer = self.create_timer(0.1, self.send_command)

        # Initialize movement parameters
        self.linear_speed = 0.5  # m/s
        self.angular_speed = 0.5  # rad/s

        self.get_logger().info('Movement Controller initialized')

    def send_command(self):
        msg = Twist()
        # Set linear and angular velocities
        msg.linear.x = self.linear_speed
        msg.angular.z = self.angular_speed
        self.cmd_vel_publisher.publish(msg)

def main(args=None):
    rclpy.init(args=args)
    controller = MovementController()

    try:
        rclpy.spin(controller)
    except KeyboardInterrupt:
        controller.get_logger().info('Stopping movement controller')
    finally:
        # Stop the robot before shutting down
        stop_msg = Twist()
        controller.cmd_vel_publisher.publish(stop_msg)
        controller.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()
```

## Joint Control for Humanoid Robots

For humanoid robots, you'll often need to control individual joints:

```python
import rclpy
from rclpy.node import Node
from sensor_msgs.msg import JointState
import math

class JointController(Node):
    def __init__(self):
        super().__init__('joint_controller')

        # Publisher for joint commands
        self.joint_publisher = self.create_publisher(JointState, 'joint_commands', 10)

        # Timer for sending joint commands
        self.timer = self.create_timer(0.05, self.send_joint_commands)

        # Define joint names for a humanoid robot
        self.joint_names = [
            'left_hip_joint', 'left_knee_joint', 'left_ankle_joint',
            'right_hip_joint', 'right_knee_joint', 'right_ankle_joint',
            'left_shoulder_joint', 'left_elbow_joint', 'left_wrist_joint',
            'right_shoulder_joint', 'right_elbow_joint', 'right_wrist_joint'
        ]

        self.time = 0.0
        self.get_logger().info('Joint Controller initialized')

    def send_joint_commands(self):
        msg = JointState()
        msg.name = self.joint_names
        msg.position = []

        # Generate sinusoidal joint movements
        for i, joint_name in enumerate(self.joint_names):
            # Create different movement patterns for different joint groups
            if 'hip' in joint_name:
                position = 0.2 * math.sin(self.time * 2.0)
            elif 'knee' in joint_name:
                position = 0.3 * math.sin(self.time * 2.0 + math.pi/2)
            elif 'shoulder' in joint_name:
                position = 0.5 * math.sin(self.time * 1.5)
            else:
                position = 0.1 * math.sin(self.time * 1.0)

            msg.position.append(position)

        msg.header.stamp = self.get_clock().now().to_msg()
        self.joint_publisher.publish(msg)
        self.time += 0.05

def main(args=None):
    rclpy.init(args=args)
    controller = JointController()

    try:
        rclpy.spin(controller)
    except KeyboardInterrupt:
        controller.get_logger().info('Stopping joint controller')
    finally:
        controller.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()
```

## Error Handling and Safety

When controlling robots, it's crucial to implement proper error handling:

```python
import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist
from sensor_msgs.msg import LaserScan
import threading
import time

class SafeController(Node):
    def __init__(self):
        super().__init__('safe_controller')

        self.cmd_vel_publisher = self.create_publisher(Twist, 'cmd_vel', 10)
        self.scan_subscriber = self.create_subscription(
            LaserScan, 'scan', self.scan_callback, 10)

        self.safety_distance = 0.5  # meters
        self.obstacle_detected = False
        self.desired_linear_speed = 0.5
        self.desired_angular_speed = 0.0

        # Timer for control loop
        self.control_timer = self.create_timer(0.1, self.control_loop)

        self.get_logger().info('Safe Controller initialized')

    def scan_callback(self, msg):
        # Check for obstacles in front of the robot
        if len(msg.ranges) > 0:
            # Check the front 30 degrees
            front_ranges = msg.ranges[:len(msg.ranges)//12] + msg.ranges[-len(msg.ranges)//12:]
            min_distance = min([r for r in front_ranges if r > 0 and not r > 10], default=float('inf'))

            self.obstacle_detected = min_distance < self.safety_distance
            if self.obstacle_detected:
                self.get_logger().warn(f'Obstacle detected at {min_distance:.2f}m')

    def control_loop(self):
        cmd_msg = Twist()

        if self.obstacle_detected:
            # Stop the robot when obstacle is detected
            cmd_msg.linear.x = 0.0
            cmd_msg.angular.z = 0.0
            self.get_logger().info('Obstacle detected - stopping robot')
        else:
            # Apply desired velocities
            cmd_msg.linear.x = self.desired_linear_speed
            cmd_msg.angular.z = self.desired_angular_speed

        self.cmd_vel_publisher.publish(cmd_msg)

def main(args=None):
    rclpy.init(args=args)
    controller = SafeController()

    try:
        rclpy.spin(controller)
    except KeyboardInterrupt:
        controller.get_logger().info('Shutting down safe controller')
    finally:
        # Always stop the robot before exiting
        stop_msg = Twist()
        controller.cmd_vel_publisher.publish(stop_msg)
        controller.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()
```

## Hands-on Exercise

Create a Python node that implements a simple state machine for a humanoid robot:

1. Define states: IDLE, WALKING, TURNING, STOPPING
2. Implement transitions based on sensor input
3. Control the robot to move forward until it detects an obstacle
4. When an obstacle is detected, turn in a random direction
5. Resume forward motion after turning

This exercise will help you understand how to implement robot control logic using Python and rclpy.