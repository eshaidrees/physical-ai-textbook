---
sidebar_position: 2
---

# Gazebo Simulation - Physics-Based Robot Testing

This section covers creating and using physics-based simulation environments in Gazebo for safe robot testing. You'll learn to create realistic simulation environments that accurately model robot physics, sensors, and interactions.

## Understanding Gazebo for Robotics

Gazebo is a powerful physics simulation environment that provides:
- Accurate physics simulation with multiple physics engines (ODE, Bullet, Simbody)
- Realistic sensor simulation (cameras, LIDAR, IMU, etc.)
- Flexible world creation and modification
- Integration with ROS 2 for seamless robot simulation
- High-performance simulation for testing complex behaviors

### Key Benefits for Robotics Development

1. **Safe Testing**: Test robot behaviors without risk of hardware damage
2. **Reproducible Experiments**: Create consistent testing environments
3. **Cost-Effective**: Reduce need for physical prototypes and testing spaces
4. **Accelerated Development**: Run simulations faster than real-time
5. **Sensor Simulation**: Test with various sensor configurations

## Setting Up Gazebo Environment

### Basic Gazebo Installation and Setup

```xml
<!-- Example robot model in URDF for Gazebo simulation -->
<?xml version="1.0"?>
<robot name="humanoid_robot" xmlns:xacro="http://www.ros.org/wiki/xacro">

  <!-- Include Gazebo-specific plugins and materials -->
  <material name="blue">
    <color rgba="0.0 0.0 1.0 1.0"/>
  </material>

  <!-- Base link -->
  <link name="base_link">
    <visual>
      <geometry>
        <box size="0.3 0.2 0.1"/>
      </geometry>
      <material name="blue"/>
    </visual>
    <collision>
      <geometry>
        <box size="0.3 0.2 0.1"/>
      </geometry>
    </collision>
    <inertial>
      <mass value="5.0"/>
      <inertia ixx="0.1" ixy="0.0" ixz="0.0" iyy="0.1" iyz="0.0" izz="0.1"/>
    </inertial>
  </link>

  <!-- Head link -->
  <joint name="head_joint" type="fixed">
    <parent link="base_link"/>
    <child link="head_link"/>
    <origin xyz="0 0 0.15"/>
  </joint>

  <link name="head_link">
    <visual>
      <geometry>
        <sphere radius="0.1"/>
      </geometry>
      <material name="blue"/>
    </visual>
    <collision>
      <geometry>
        <sphere radius="0.1"/>
      </geometry>
    </collision>
    <inertial>
      <mass value="1.0"/>
      <inertia ixx="0.004" ixy="0.0" ixz="0.0" iyy="0.004" iyz="0.0" izz="0.004"/>
    </inertial>
  </link>

  <!-- Gazebo plugins for ROS 2 control -->
  <gazebo reference="base_link">
    <material>Gazebo/Blue</material>
  </gazebo>

  <gazebo reference="head_link">
    <material>Gazebo/Blue</material>
  </gazebo>

  <!-- Gazebo ROS 2 control plugin -->
  <gazebo>
    <plugin filename="libgazebo_ros2_control.so" name="gazebo_ros2_control">
      <parameters>$(find my_robot_description)/config/my_robot_controllers.yaml</parameters>
    </plugin>
  </gazebo>

</robot>
```

### Creating Custom Worlds

```xml
<!-- Example custom world file -->
<sdf version="1.7">
  <world name="my_robot_world">
    <!-- Include default physics -->
    <physics name="default_physics" type="ode">
      <max_step_size>0.001</max_step_size>
      <real_time_factor>1.0</real_time_factor>
      <real_time_update_rate>1000.0</real_time_update_rate>
    </physics>

    <!-- Lighting -->
    <light name="sun" type="directional">
      <cast_shadows>true</cast_shadows>
      <pose>0 0 10 0 0 0</pose>
      <diffuse>0.8 0.8 0.8 1</diffuse>
      <specular>0.2 0.2 0.2 1</specular>
      <attenuation>
        <range>1000</range>
        <constant>0.9</constant>
        <linear>0.01</linear>
        <quadratic>0.001</quadratic>
      </attenuation>
      <direction>-0.4 0.2 -1</direction>
    </light>

    <!-- Ground plane -->
    <model name="ground_plane">
      <static>true</static>
      <link name="link">
        <collision name="collision">
          <geometry>
            <plane>
              <normal>0 0 1</normal>
            </plane>
          </geometry>
        </collision>
        <visual name="visual">
          <geometry>
            <plane>
              <normal>0 0 1</normal>
              <size>100 100</size>
            </plane>
          </geometry>
          <material>
            <ambient>0.7 0.7 0.7 1</ambient>
            <diffuse>0.7 0.7 0.7 1</diffuse>
            <specular>0.0 0.0 0.0 1</specular>
          </material>
        </visual>
      </link>
    </model>

    <!-- Add obstacles -->
    <model name="table">
      <pose>2 0 0 0 0 0</pose>
      <link name="table_link">
        <collision name="collision">
          <geometry>
            <box>
              <size>1 0.8 0.8</size>
            </box>
          </geometry>
        </collision>
        <visual name="visual">
          <geometry>
            <box>
              <size>1 0.8 0.8</size>
            </box>
          </geometry>
          <material>
            <ambient>0.8 0.6 0.4 1</ambient>
            <diffuse>0.8 0.6 0.4 1</diffuse>
          </material>
        </visual>
        <inertial>
          <mass>10.0</mass>
          <inertia>
            <ixx>1.0</ixx>
            <ixy>0.0</ixy>
            <ixz>0.0</ixz>
            <iyy>1.0</iyy>
            <iyz>0.0</iyz>
            <izz>1.0</izz>
          </inertia>
        </inertial>
      </link>
    </model>

    <!-- Place your robot -->
    <include>
      <uri>model://my_humanoid_robot</uri>
      <pose>0 0 1 0 0 0</pose>
    </include>
  </world>
</sdf>
```

## Advanced Gazebo Configuration

### Sensor Integration

```xml
<!-- Adding sensors to your robot model -->
<link name="camera_link">
  <visual>
    <geometry>
      <box size="0.05 0.05 0.05"/>
    </geometry>
  </visual>
  <collision>
    <geometry>
      <box size="0.05 0.05 0.05"/>
    </geometry>
  </collision>
  <inertial>
    <mass value="0.1"/>
    <inertia ixx="1e-6" ixy="0" ixz="0" iyy="1e-6" iyz="0" izz="1e-6"/>
  </inertial>
</link>

<joint name="camera_joint" type="fixed">
  <parent link="head_link"/>
  <child link="camera_link"/>
  <origin xyz="0.05 0 0" rpy="0 0 0"/>
</joint>

<!-- Gazebo camera sensor -->
<gazebo reference="camera_link">
  <sensor type="camera" name="camera1">
    <update_rate>30.0</update_rate>
    <camera name="head_camera">
      <horizontal_fov>1.3962634</horizontal_fov>
      <image>
        <width>800</width>
        <height>600</height>
        <format>R8G8B8</format>
      </image>
      <clip>
        <near>0.02</near>
        <far>300</far>
      </clip>
    </camera>
    <plugin name="camera_controller" filename="libgazebo_ros_camera.so">
      <frame_name>camera_link</frame_name>
      <topic_name>/camera/image_raw</topic_name>
    </plugin>
  </sensor>
</gazebo>

<!-- LIDAR sensor -->
<link name="lidar_link">
  <visual>
    <geometry>
      <cylinder radius="0.05" length="0.05"/>
    </geometry>
  </visual>
  <collision>
    <geometry>
      <cylinder radius="0.05" length="0.05"/>
    </geometry>
  </collision>
  <inertial>
    <mass value="0.2"/>
    <inertia ixx="1e-5" ixy="0" ixz="0" iyy="1e-5" iyz="0" izz="1e-5"/>
  </inertial>
</link>

<joint name="lidar_joint" type="fixed">
  <parent link="base_link"/>
  <child link="lidar_link"/>
  <origin xyz="0.1 0 0.05" rpy="0 0 0"/>
</joint>

<gazebo reference="lidar_link">
  <sensor type="ray" name="lidar_sensor">
    <pose>0 0 0 0 0 0</pose>
    <visualize>false</visualize>
    <update_rate>10</update_rate>
    <ray>
      <scan>
        <horizontal>
          <samples>360</samples>
          <resolution>1.0</resolution>
          <min_angle>-3.14159</min_angle>
          <max_angle>3.14159</max_angle>
        </horizontal>
      </scan>
      <range>
        <min>0.1</min>
        <max>30.0</max>
        <resolution>0.01</resolution>
      </range>
    </ray>
    <plugin name="lidar_controller" filename="libgazebo_ros_laser.so">
      <topic_name>/scan</topic_name>
      <frame_name>lidar_link</frame_name>
    </plugin>
  </sensor>
</gazebo>
```

### Physics Configuration and Tuning

```python
#!/usr/bin/env python3

"""
Gazebo physics configuration and robot control example
"""

import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist
from sensor_msgs.msg import LaserScan, Image
from nav_msgs.msg import Odometry
import cv2
from cv_bridge import CvBridge
import numpy as np


class GazeboRobotController(Node):
    def __init__(self):
        super().__init__('gazebo_robot_controller')

        # Publishers for robot control
        self.cmd_vel_pub = self.create_publisher(Twist, '/cmd_vel', 10)

        # Subscribers for sensor data
        self.scan_sub = self.create_subscription(LaserScan, '/scan', self.scan_callback, 10)
        self.image_sub = self.create_subscription(Image, '/camera/image_raw', self.image_callback, 10)
        self.odom_sub = self.create_subscription(Odometry, '/odom', self.odom_callback, 10)

        # Timer for control loop
        self.control_timer = self.create_timer(0.1, self.control_loop)

        # State variables
        self.laser_data = None
        self.position = None
        self.velocity = None
        self.bridge = CvBridge()

        self.get_logger().info('Gazebo Robot Controller initialized')

    def scan_callback(self, msg):
        """Process laser scan data"""
        self.laser_data = np.array(msg.ranges)
        # Filter out invalid ranges
        self.laser_data = self.laser_data[(self.laser_data > msg.range_min) &
                                         (self.laser_data < msg.range_max)]

    def image_callback(self, msg):
        """Process camera image data"""
        try:
            cv_image = self.bridge.imgmsg_to_cv2(msg, "bgr8")
            # Process image if needed
            # For example, detect objects, lines, etc.
        except Exception as e:
            self.get_logger().error(f'Error processing image: {e}')

    def odom_callback(self, msg):
        """Process odometry data"""
        self.position = msg.pose.pose.position
        self.velocity = msg.twist.twist.linear

    def control_loop(self):
        """Main control loop for robot behavior in simulation"""
        if self.laser_data is not None:
            # Simple obstacle avoidance
            min_distance = 0.5  # meters

            # Check front, left, and right sectors
            front_sector = self.laser_data[160:200]  # Front 40 beams
            left_sector = self.laser_data[80:120]    # Left 40 beams
            right_sector = self.laser_data[240:280]  # Right 40 beams

            front_min = np.min(front_sector) if len(front_sector) > 0 else float('inf')
            left_min = np.min(left_sector) if len(left_sector) > 0 else float('inf')
            right_min = np.min(right_sector) if len(right_sector) > 0 else float('inf')

            cmd_vel = Twist()

            if front_min < min_distance:
                # Obstacle detected in front, turn
                if left_min > right_min:
                    cmd_vel.angular.z = 0.5  # Turn left
                else:
                    cmd_vel.angular.z = -0.5  # Turn right
            else:
                # Clear path, move forward
                cmd_vel.linear.x = 0.5

            # Publish command
            self.cmd_vel_pub.publish(cmd_vel)

    def navigate_to_goal(self, goal_x, goal_y):
        """Navigate to a specific goal position"""
        if self.position is not None:
            # Calculate direction to goal
            dx = goal_x - self.position.x
            dy = goal_y - self.position.y
            distance = np.sqrt(dx**2 + dy**2)

            cmd_vel = Twist()

            if distance > 0.2:  # If not close to goal
                # Calculate desired angle
                desired_angle = np.arctan2(dy, dx)

                # Simple proportional controller for angular velocity
                cmd_vel.angular.z = 0.5 * desired_angle

                # Move forward if roughly aligned with goal
                if abs(desired_angle) < 0.2:
                    cmd_vel.linear.x = 0.3
            else:
                # Reached goal, stop
                cmd_vel.linear.x = 0.0
                cmd_vel.angular.z = 0.0

            self.cmd_vel_pub.publish(cmd_vel)


def main(args=None):
    rclpy.init(args=args)

    controller = GazeboRobotController()

    try:
        rclpy.spin(controller)
    except KeyboardInterrupt:
        controller.get_logger().info('Shutting down Gazebo Robot Controller')
    finally:
        controller.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
```

## Simulation Launch Files

### Launch Configuration

```xml
<!-- launch/gazebo_simulation.launch.py -->
from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription, DeclareLaunchArgument
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration, PathJoinSubstitution
from launch_ros.actions import Node
from launch_ros.substitutions import FindPackageShare


def generate_launch_description():
    # Launch configuration variables
    use_sim_time = LaunchConfiguration('use_sim_time')
    world = LaunchConfiguration('world')

    # Declare launch arguments
    declare_use_sim_time_cmd = DeclareLaunchArgument(
        'use_sim_time',
        default_value='true',
        description='Use simulation (Gazebo) clock if true'
    )

    declare_world_cmd = DeclareLaunchArgument(
        'world',
        default_value='empty.sdf',
        description='Choose one of the world files from `/my_robot_gazebo/worlds`'
    )

    # Start Gazebo server
    start_gazebo_server_cmd = IncludeLaunchDescription(
        PythonLaunchDescriptionSource([
            PathJoinSubstitution([
                FindPackageShare('gazebo_ros'),
                'launch',
                'gzserver.launch.py'
            ])
        ]),
        launch_arguments={
            'world': world,
            'use_sim_time': use_sim_time,
        }.items()
    )

    # Start Gazebo client
    start_gazebo_client_cmd = IncludeLaunchDescription(
        PythonLaunchDescriptionSource([
            PathJoinSubstitution([
                FindPackageShare('gazebo_ros'),
                'launch',
                'gzclient.launch.py'
            ])
        ]),
        launch_arguments={
            'use_sim_time': use_sim_time,
        }.items()
    )

    # Spawn robot in Gazebo
    spawn_entity_cmd = Node(
        package='gazebo_ros',
        executable='spawn_entity.py',
        arguments=[
            '-topic', 'robot_description',
            '-entity', 'my_humanoid_robot',
            '-x', '0.0',
            '-y', '0.0',
            '-z', '1.0'
        ],
        output='screen'
    )

    # Robot state publisher
    robot_state_publisher_cmd = Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        parameters=[{
            'use_sim_time': use_sim_time,
        }],
        arguments=[PathJoinSubstitution([
            FindPackageShare('my_robot_description'),
            'urdf',
            'my_robot.urdf'
        ])],
        output='screen'
    )

    ld = LaunchDescription()

    # Add the actions
    ld.add_action(declare_use_sim_time_cmd)
    ld.add_action(declare_world_cmd)
    ld.add_action(start_gazebo_server_cmd)
    ld.add_action(start_gazebo_client_cmd)
    ld.add_action(robot_state_publisher_cmd)
    ld.add_action(spawn_entity_cmd)

    return ld
```

## Best Practices for Gazebo Simulation

### Performance Optimization

```python
# Performance optimization tips for Gazebo simulation

"""
1. Physics Parameters:
   - Use appropriate step size (typically 0.001 for accuracy)
   - Balance real_time_factor for performance vs. accuracy
   - Choose the right physics engine for your needs

2. Sensor Configuration:
   - Reduce update rates for sensors that don't need high frequency
   - Use appropriate resolutions for cameras and LIDAR
   - Disable visualization for sensors during batch testing

3. Model Complexity:
   - Use simplified collision geometries where possible
   - Reduce visual mesh complexity
   - Use instancing for multiple similar objects

4. World Design:
   - Keep worlds simple for faster loading
   - Use static objects when possible
   - Limit the number of active dynamic objects
"""

# Example: Optimized launch parameters
"""
<physics name="default_physics" type="ode">
  <max_step_size>0.01</max_step_size>  <!-- Increased for performance -->
  <real_time_factor>1.0</real_time_factor>
  <real_time_update_rate>100.0</real_time_update_rate>  <!-- Reduced for performance -->
</physics>
"""
```

## Hands-on Exercise

Create a complete Gazebo simulation environment for your humanoid robot that includes:
1. A custom world with obstacles and features
2. Proper URDF model with Gazebo plugins
3. Sensor integration (camera and LIDAR)
4. Basic navigation and obstacle avoidance
5. Launch files to start the complete simulation

This exercise will help you understand the complete workflow for creating and testing robots in Gazebo simulation.