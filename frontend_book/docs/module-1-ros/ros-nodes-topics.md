---
sidebar_position: 2
---

# ROS 2 Nodes, Topics, Services, and Actions

This section covers the fundamental communication patterns in ROS 2: nodes, topics, services, and actions. These components form the backbone of the robotic nervous system, enabling different parts of the robot to communicate and coordinate.

## Nodes

A node is a process that performs computation. In ROS 2, nodes are the basic building blocks of a distributed system. Each node typically performs a specific task, such as controlling a sensor, processing data, or commanding actuators.

### Creating a Simple Node

Here's a basic ROS 2 node implementation:

```python
import rclpy
from rclpy.node import Node

class MinimalPublisher(Node):

    def __init__(self):
        super().__init__('minimal_publisher')
        self.publisher_ = self.create_publisher(String, 'topic', 10)
        timer_period = 0.5  # seconds
        self.timer = self.create_timer(timer_period, self.timer_callback)
        self.i = 0

    def timer_callback(self):
        msg = String()
        msg.data = 'Hello World: %d' % self.i
        self.publisher_.publish(msg)
        self.get_logger().info('Publishing: "%s"' % msg.data)
        self.i += 1

def main(args=None):
    rclpy.init(args=args)

    minimal_publisher = MinimalPublisher()

    rclpy.spin(minimal_publisher)

    minimal_publisher.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
```

## Topics and Publishers/Subscribers

Topics enable asynchronous communication between nodes using a publish/subscribe pattern. Publishers send messages to a topic, and subscribers receive messages from that topic.

### Publisher Example

```python
import rclpy
from rclpy.node import Node
from std_msgs.msg import String

class Publisher(Node):

    def __init__(self):
        super().__init__('publisher')
        self.publisher = self.create_publisher(String, 'robot_commands', 10)
        self.timer = self.create_timer(1.0, self.publish_message)

    def publish_message(self):
        msg = String()
        msg.data = 'Move forward'
        self.publisher.publish(msg)
        self.get_logger().info(f'Publishing: {msg.data}')
```

### Subscriber Example

```python
import rclpy
from rclpy.node import Node
from std_msgs.msg import String

class Subscriber(Node):

    def __init__(self):
        super().__init__('subscriber')
        self.subscription = self.create_subscription(
            String,
            'robot_commands',
            self.listener_callback,
            10)
        self.subscription  # prevent unused variable warning

    def listener_callback(self, msg):
        self.get_logger().info(f'I heard: {msg.data}')
```

## Services

Services provide synchronous request/response communication between nodes. A service client sends a request to a service server, which processes the request and returns a response.

### Service Server Example

```python
from example_interfaces.srv import AddTwoInts
import rclpy
from rclpy.node import Node

class MinimalService(Node):

    def __init__(self):
        super().__init__('minimal_service')
        self.srv = self.create_service(AddTwoInts, 'add_two_ints', self.add_two_ints_callback)

    def add_two_ints_callback(self, request, response):
        response.sum = request.a + request.b
        self.get_logger().info(f'Returning {response.sum}')
        return response
```

## Actions

Actions are used for long-running tasks that require feedback and the ability to cancel. They combine the features of topics and services with additional capabilities for monitoring progress.

### Action Server Example

```python
import rclpy
from rclpy.action import ActionServer
from rclpy.node import Node

from interfaces.action import NavigateToPose  # Custom action interface

class NavigateActionServer(Node):

    def __init__(self):
        super().__init__('navigate_action_server')
        self._action_server = ActionServer(
            self,
            NavigateToPose,
            'navigate_to_pose',
            self.execute_callback)

    def execute_callback(self, goal_handle):
        self.get_logger().info('Executing goal...')

        # Execute navigation logic here
        feedback_msg = NavigateToPose.Feedback()

        # Send feedback periodically
        for i in range(10):
            feedback_msg.feedback = f'Navigating... {i}/10'
            goal_handle.publish_feedback(feedback_msg)

        result = NavigateToPose.Result()
        result.success = True
        result.message = 'Navigation completed successfully'

        goal_handle.succeed()
        return result
```

## Hands-on Exercise

Create a simple publisher and subscriber pair that allows you to control a simulated humanoid robot's basic movements. Implement topics for:
- Movement commands (forward, backward, turn left, turn right)
- Sensor feedback (distance to obstacles)
- Robot status (battery level, operational state)

This exercise will help you understand the publish/subscribe pattern and prepare you for more complex robot control scenarios.