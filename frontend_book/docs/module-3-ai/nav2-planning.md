---
sidebar_position: 4
---

# Nav2 Planning for Humanoid Robots

This section covers implementing path planning for humanoid robots using the Navigation 2 (Nav2) stack. Unlike wheeled robots, humanoid robots have complex kinematics and dynamics that require specialized planning approaches.

## Introduction to Navigation 2

Navigation 2 (Nav2) is the latest ROS navigation stack designed for mobile robots. For humanoid robots, Nav2 provides:
- Global path planning
- Local path planning and obstacle avoidance
- Map management
- Behavior trees for complex navigation tasks
- Recovery behaviors

## Nav2 Architecture for Humanoid Robots

### Core Components

```python
import rclpy
from rclpy.node import Node
from nav_msgs.msg import OccupancyGrid, Path
from geometry_msgs.msg import PoseStamped, PointStamped
from geometry_msgs.msg import Twist
from sensor_msgs.msg import LaserScan, PointCloud2
from std_msgs.msg import String
import tf2_ros
from tf2_ros import TransformListener
from tf2_geometry_msgs import do_transform_pose
import numpy as np
from math import sqrt, atan2, cos, sin
import threading

class HumanoidNav2(Node):
    def __init__(self):
        super().__init__('humanoid_nav2')

        # Publishers
        self.cmd_vel_pub = self.create_publisher(Twist, '/cmd_vel', 10)
        self.global_plan_pub = self.create_publisher(Path, '/humanoid/global_plan', 10)
        self.local_plan_pub = self.create_publisher(Path, '/humanoid/local_plan', 10)
        self.goal_pub = self.create_publisher(PoseStamped, '/humanoid/goal', 10)

        # Subscribers
        self.goal_sub = self.create_subscription(
            PoseStamped, '/humanoid/goal', self.goal_callback, 10
        )
        self.laser_sub = self.create_subscription(
            LaserScan, '/scan', self.laser_callback, 10
        )
        self.odom_sub = self.create_subscription(
            String, '/odom', self.odom_callback, 10  # Simplified for this example
        )

        # TF2
        self.tf_buffer = tf2_ros.Buffer()
        self.tf_listener = tf2_ros.TransformListener(self.tf_buffer, self)

        # Navigation state
        self.current_pose = None
        self.goal_pose = None
        self.global_path = []
        self.local_path = []
        self.navigation_active = False
        self.obstacle_detected = False
        self.obstacle_distance = float('inf')

        # Navigation parameters
        self.linear_speed = 0.3  # m/s
        self.angular_speed = 0.5  # rad/s
        self.arrival_threshold = 0.5  # meters
        self.safe_distance = 0.8  # meters for obstacles

        # Timer for navigation loop
        self.nav_timer = self.create_timer(0.1, self.navigation_loop)

        self.get_logger().info('Humanoid Nav2 initialized')

    def goal_callback(self, msg):
        """Receive navigation goal"""
        self.goal_pose = msg
        self.get_logger().info(f'Navigation goal received: ({msg.pose.position.x}, {msg.pose.position.y})')

        # Start navigation
        if self.current_pose is not None:
            self.calculate_global_path()
            self.navigation_active = True

    def laser_callback(self, msg):
        """Process laser scan data for obstacle detection"""
        # Find minimum distance in front of robot
        front_scan = msg.ranges[len(msg.ranges)//2 - 30:len(msg.ranges)//2 + 30]  # 60-degree front
        self.obstacle_distance = min(front_scan) if front_scan else float('inf')
        self.obstacle_detected = self.obstacle_distance < self.safe_distance

    def odom_callback(self, msg):
        """Update robot position (simplified)"""
        # In a real implementation, this would process odometry data
        pass

    def navigation_loop(self):
        """Main navigation control loop"""
        if not self.navigation_active or self.current_pose is None or self.goal_pose is None:
            # Stop robot if navigation is not active
            stop_cmd = Twist()
            self.cmd_vel_pub.publish(stop_cmd)
            return

        if self.obstacle_detected:
            self.handle_obstacle()
        else:
            self.follow_path()

        # Check if goal reached
        if self.current_pose and self.goal_pose:
            distance_to_goal = self.calculate_distance_to_goal()
            if distance_to_goal < self.arrival_threshold:
                self.get_logger().info('Goal reached!')
                self.navigation_active = False
                self.publish_stop_command()

    def calculate_distance_to_goal(self):
        """Calculate distance to goal position"""
        if self.current_pose is None or self.goal_pose is None:
            return float('inf')

        dx = self.goal_pose.pose.position.x - self.current_pose.pose.position.x
        dy = self.goal_pose.pose.position.y - self.current_pose.pose.position.y
        return sqrt(dx*dx + dy*dy)

    def calculate_global_path(self):
        """Calculate global path to goal (simplified - use Nav2 plugins in practice)"""
        if self.current_pose is None or self.goal_pose is None:
            return

        # Simplified path calculation (in practice, use Nav2's global planner)
        current_pos = self.current_pose.pose.position
        goal_pos = self.goal_pose.pose.position

        # Create a straight line path (simplified)
        steps = int(sqrt((goal_pos.x - current_pos.x)**2 + (goal_pos.y - current_pos.y)**2) * 10)
        self.global_path = []

        for i in range(steps + 1):
            t = i / steps if steps > 0 else 0
            point = PoseStamped()
            point.header.frame_id = 'map'
            point.pose.position.x = current_pos.x + t * (goal_pos.x - current_pos.x)
            point.pose.position.y = current_pos.y + t * (goal_pos.y - current_pos.y)
            point.pose.position.z = current_pos.z + t * (goal_pos.z - current_pos.z)

            self.global_path.append(point)

        # Publish global plan
        self.publish_global_plan()

    def follow_path(self):
        """Follow the calculated path"""
        if not self.global_path:
            return

        # Simple path following for humanoid (simplified)
        cmd = Twist()

        # Calculate direction to next point
        if self.current_pose and len(self.global_path) > 0:
            target = self.global_path[0].pose  # First point in path
            current = self.current_pose.pose.position

            # Calculate desired heading
            dx = target.position.x - current.x
            dy = target.position.y - current.y
            desired_yaw = atan2(dy, dx)

            # Calculate current yaw (simplified)
            current_yaw = 0  # Should be calculated from orientation
            angle_diff = desired_yaw - current_yaw

            # Normalize angle
            while angle_diff > np.pi:
                angle_diff -= 2 * np.pi
            while angle_diff < -np.pi:
                angle_diff += 2 * np.pi

            # Set velocities
            cmd.linear.x = self.linear_speed if abs(angle_diff) < 0.2 else 0.0
            cmd.angular.z = self.angular_speed * angle_diff if abs(angle_diff) > 0.1 else 0.0

        self.cmd_vel_pub.publish(cmd)

    def handle_obstacle(self):
        """Handle obstacle avoidance"""
        cmd = Twist()

        # Simple obstacle avoidance: turn away from obstacle
        cmd.angular.z = self.angular_speed  # Turn in place
        cmd.linear.x = 0.0  # Stop forward motion

        self.cmd_vel_pub.publish(cmd)
        self.get_logger().info(f'Obstacle detected at {self.obstacle_distance:.2f}m, turning...')

    def publish_global_plan(self):
        """Publish the calculated global plan"""
        path_msg = Path()
        path_msg.header.frame_id = 'map'
        path_msg.header.stamp = self.get_clock().now().to_msg()

        for pose in self.global_path:
            path_msg.poses.append(pose)

        self.global_plan_pub.publish(path_msg)

    def publish_stop_command(self):
        """Publish command to stop the robot"""
        cmd = Twist()
        self.cmd_vel_pub.publish(cmd)

def main(args=None):
    rclpy.init(args=args)
    navigator = HumanoidNav2()

    try:
        rclpy.spin(navigator)
    except KeyboardInterrupt:
        navigator.get_logger().info('Shutting down Humanoid Nav2')
    finally:
        navigator.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()
```

## Specialized Planning for Humanoid Kinematics

Humanoid robots have different requirements compared to wheeled robots:

```python
import rclpy
from rclpy.node import Node
from geometry_msgs.msg import PoseStamped, Twist
from nav_msgs.msg import Path
from sensor_msgs.msg import JointState
from visualization_msgs.msg import MarkerArray
import numpy as np
from math import pi, sin, cos, atan2, sqrt

class HumanoidPathPlanner(Node):
    def __init__(self):
        super().__init__('humanoid_path_planner')

        # Publishers
        self.footstep_plan_pub = self.create_publisher(Path, '/humanoid/footstep_plan', 10)
        self.com_trajectory_pub = self.create_publisher(Path, '/humanoid/com_trajectory', 10)
        self.visualization_pub = self.create_publisher(MarkerArray, '/humanoid/plan_viz', 10)

        # Subscribers
        self.goal_sub = self.create_subscription(
            PoseStamped, '/humanoid/goal', self.goal_callback, 10
        )
        self.joint_state_sub = self.create_subscription(
            JointState, '/joint_states', self.joint_state_callback, 10
        )

        # Robot parameters
        self.leg_length = 0.5  # meters
        self.step_length = 0.3  # meters
        self.step_width = 0.2   # meters
        self.com_height = 0.8   # meters (center of mass height)

        # State
        self.current_pose = None
        self.current_joints = None
        self.foot_positions = {
            'left': np.array([0.0, 0.1, 0.0]),
            'right': np.array([0.0, -0.1, 0.0])
        }
        self.support_foot = 'left'  # Which foot is currently supporting the robot

        self.get_logger().info('Humanoid Path Planner initialized')

    def goal_callback(self, msg):
        """Plan footsteps to reach goal position"""
        self.get_logger().info(f'Planning footsteps to goal: ({msg.pose.position.x}, {msg.pose.position.y})')

        # Calculate footstep plan
        footstep_plan = self.calculate_footstep_plan(msg)

        # Publish plan
        self.publish_footstep_plan(footstep_plan)

    def calculate_footstep_plan(self, goal):
        """Calculate footstep plan for humanoid robot"""
        if self.current_pose is None:
            return []

        # Simplified footstep planning algorithm
        steps = []
        current_pos = np.array([
            self.current_pose.pose.position.x,
            self.current_pose.pose.position.y,
            self.current_pose.pose.position.z
        ])

        goal_pos = np.array([
            goal.pose.position.x,
            goal.pose.position.y,
            goal.pose.position.z
        ])

        # Calculate direction to goal
        direction = goal_pos - current_pos
        distance = np.linalg.norm(direction)
        direction = direction / distance if distance > 0 else direction

        # Generate footsteps
        num_steps = int(distance / self.step_length) + 1

        for i in range(num_steps):
            step_pos = current_pos + direction * self.step_length * i

            # Alternate feet
            if i % 2 == 0:
                foot_name = 'left' if self.support_foot == 'right' else 'right'
            else:
                foot_name = 'right' if self.support_foot == 'right' else 'left'

            step = PoseStamped()
            step.header.frame_id = 'map'
            step.header.stamp = self.get_clock().now().to_msg()
            step.pose.position.x = step_pos[0]
            step.pose.position.y = step_pos[1]
            step.pose.position.z = 0.0  # Ground level
            step.pose.orientation.w = 1.0  # Identity quaternion

            steps.append(step)

        self.get_logger().info(f'Generated {len(steps)} footsteps')

        return steps

    def calculate_com_trajectory(self, footsteps):
        """Calculate center of mass trajectory"""
        com_trajectory = []

        for i, step in enumerate(footsteps):
            # Simplified CoM trajectory calculation
            # In practice, this would use more sophisticated methods like ZMP control
            com_point = PoseStamped()
            com_point.header.frame_id = 'map'
            com_point.header.stamp = self.get_clock().now().to_msg()

            # CoM position: between the feet
            if i > 0:
                prev_step = footsteps[i-1]
                # Interpolate CoM position between previous and current footstep
                alpha = 0.5  # Simplified: CoM halfway between feet
                com_point.pose.position.x = alpha * step.pose.position.x + (1-alpha) * prev_step.pose.position.x
                com_point.pose.position.y = alpha * step.pose.position.y + (1-alpha) * prev_step.pose.position.y
                com_point.pose.position.z = self.com_height  # Keep CoM at constant height

            com_trajectory.append(com_point)

        return com_trajectory

    def publish_footstep_plan(self, footsteps):
        """Publish the footstep plan"""
        path_msg = Path()
        path_msg.header.frame_id = 'map'
        path_msg.header.stamp = self.get_clock().now().to_msg()
        path_msg.poses = [step for step in footsteps]

        self.footstep_plan_pub.publish(path_msg)

        # Also publish CoM trajectory
        com_trajectory = self.calculate_com_trajectory(footsteps)
        com_path_msg = Path()
        com_path_msg.header.frame_id = 'map'
        com_path_msg.header.stamp = self.get_clock().now().to_msg()
        com_path_msg.poses = [step for step in com_trajectory]

        self.com_trajectory_pub.publish(com_path_msg)

    def joint_state_callback(self, msg):
        """Update joint positions"""
        self.current_joints = msg

    def validate_footstep(self, foot_pos, map_data=None):
        """Validate if a footstep is safe"""
        # Check for obstacles, uneven terrain, etc.
        # This is a simplified validation
        return True

def main(args=None):
    rclpy.init(args=args)
    planner = HumanoidPathPlanner()

    try:
        rclpy.spin(planner)
    except KeyboardInterrupt:
        planner.get_logger().info('Shutting down Humanoid Path Planner')
    finally:
        planner.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()
```

## Behavior Trees for Complex Navigation

Nav2 uses behavior trees for complex navigation tasks:

```python
import rclpy
from rclpy.node import Node
from geometry_msgs.msg import PoseStamped
from std_msgs.msg import String
from action_msgs.msg import GoalStatus
from rclpy.action import ActionClient
import time

class HumanoidBehaviorTree(Node):
    def __init__(self):
        super().__init__('humanoid_behavior_tree')

        # Publishers and subscribers
        self.nav_status_pub = self.create_publisher(String, '/nav_status', 10)

        # Navigation actions
        self.nav_to_pose_client = ActionClient(self, 'nav2_msgs/action/NavigateToPose', 'navigate_to_pose')

        # Behavior tree state
        self.current_task = None
        self.task_queue = []
        self.nav_status = 'IDLE'

        # Timer for behavior execution
        self.bt_timer = self.create_timer(0.1, self.execute_behavior)

        self.get_logger().info('Humanoid Behavior Tree initialized')

    def add_navigation_task(self, goal_pose):
        """Add a navigation task to the queue"""
        task = {
            'type': 'navigate',
            'goal': goal_pose,
            'status': 'PENDING',
            'start_time': time.time()
        }
        self.task_queue.append(task)
        self.get_logger().info(f'Added navigation task to queue')

    def add_inspection_task(self, location_list):
        """Add an inspection task to visit multiple locations"""
        task = {
            'type': 'inspect',
            'locations': location_list,
            'current_index': 0,
            'status': 'PENDING'
        }
        self.task_queue.append(task)
        self.get_logger().info(f'Added inspection task with {len(location_list)} locations')

    def execute_behavior(self):
        """Execute current behavior based on task queue"""
        if not self.task_queue or self.nav_status == 'BUSY':
            return

        current_task = self.task_queue[0]

        if current_task['status'] == 'PENDING':
            if current_task['type'] == 'navigate':
                self.execute_navigation_task(current_task)
            elif current_task['type'] == 'inspect':
                self.execute_inspection_task(current_task)

        elif current_task['status'] == 'SUCCESS':
            # Task completed, remove from queue
            self.task_queue.pop(0)
            self.nav_status = 'IDLE'
            self.get_logger().info(f'Task completed, {len(self.task_queue)} tasks remaining')

        elif current_task['status'] == 'FAILED':
            # Handle failure - maybe try again or skip
            self.get_logger().warn('Navigation task failed, skipping to next task')
            self.task_queue.pop(0)
            self.nav_status = 'IDLE'

    def execute_navigation_task(self, task):
        """Execute a navigation task"""
        goal_msg = task['goal']

        # Send navigation goal
        if self.nav_to_pose_client.wait_for_server(timeout_sec=1.0):
            send_goal_future = self.nav_to_pose_client.send_goal_async(goal_msg)
            send_goal_future.add_done_callback(self.nav_goal_response_callback)

            task['status'] = 'IN_PROGRESS'
            self.nav_status = 'BUSY'
        else:
            self.get_logger().error('Navigation action server not available')
            task['status'] = 'FAILED'

    def execute_inspection_task(self, task):
        """Execute an inspection task (visit multiple locations)"""
        if task['current_index'] >= len(task['locations']):
            # All locations visited
            task['status'] = 'SUCCESS'
            return

        # Navigate to current location
        current_location = task['locations'][task['current_index']]
        goal_msg = PoseStamped()
        goal_msg.header.frame_id = 'map'
        goal_msg.pose = current_location

        if self.nav_to_pose_client.wait_for_server(timeout_sec=1.0):
            send_goal_future = self.nav_to_pose_client.send_goal_async(goal_msg)
            send_goal_future.add_done_callback(lambda future: self.inspection_goal_response(future, task))

            task['status'] = 'IN_PROGRESS'
            self.nav_status = 'BUSY'
        else:
            self.get_logger().error('Navigation action server not available')
            task['status'] = 'FAILED'

    def nav_goal_response_callback(self, future):
        """Handle navigation goal response"""
        goal_handle = future.result()
        if not goal_handle.accepted:
            self.get_logger().error('Navigation goal rejected')
            return

        # Get result
        get_result_future = goal_handle.get_result_async()
        get_result_future.add_done_callback(self.nav_result_callback)

    def nav_result_callback(self, future):
        """Handle navigation result"""
        if not self.task_queue:
            return

        current_task = self.task_queue[0]
        result = future.result().result
        status = future.result().status

        if status == GoalStatus.STATUS_SUCCEEDED:
            current_task['status'] = 'SUCCESS'
            self.get_logger().info('Navigation task completed successfully')
        else:
            current_task['status'] = 'FAILED'
            self.get_logger().warn(f'Navigation task failed with status: {status}')

    def inspection_goal_response(self, future, task):
        """Handle inspection goal response"""
        goal_handle = future.result()
        if not goal_handle.accepted:
            self.get_logger().error('Inspection goal rejected')
            task['status'] = 'FAILED'
            return

        # Get result
        get_result_future = goal_handle.get_result_async()
        get_result_future.add_done_callback(lambda result_future: self.inspection_result(result_future, task))

    def inspection_result(self, future, task):
        """Handle inspection result"""
        result = future.result().result
        status = future.result().status

        if status == GoalStatus.STATUS_SUCCEEDED:
            # Move to next location
            task['current_index'] += 1
            if task['current_index'] >= len(task['locations']):
                task['status'] = 'SUCCESS'
            else:
                # Continue with next location
                task['status'] = 'PENDING'
        else:
            task['status'] = 'FAILED'
            self.get_logger().warn(f'Inspection goal failed with status: {status}')

def main(args=None):
    rclpy.init(args=args)
    bt_node = HumanoidBehaviorTree()

    try:
        rclpy.spin(bt_node)
    except KeyboardInterrupt:
        bt_node.get_logger().info('Shutting down Humanoid Behavior Tree')
    finally:
        bt_node.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()
```

## Humanoid-Specific Recovery Behaviors

Humanoid robots need specialized recovery behaviors:

```python
import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist, PoseStamped
from sensor_msgs.msg import LaserScan
from std_msgs.msg import String
import numpy as np
from math import pi, atan2

class HumanoidRecoveryBehaviors(Node):
    def __init__(self):
        super().__init__('humanoid_recovery_behaviors')

        # Publishers
        self.cmd_vel_pub = self.create_publisher(Twist, '/cmd_vel', 10)
        self.recovery_status_pub = self.create_publisher(String, '/recovery_status', 10)

        # Subscribers
        self.laser_sub = self.create_subscription(
            LaserScan, '/scan', self.laser_callback, 10
        )
        self.nav_status_sub = self.create_subscription(
            String, '/nav_status', self.nav_status_callback, 10
        )

        # Recovery state
        self.recovery_active = False
        self.current_recovery = None
        self.obstacle_data = None
        self.nav_status = 'IDLE'

        # Timer for recovery execution
        self.recovery_timer = self.create_timer(0.1, self.execute_recovery)

        self.get_logger().info('Humanoid Recovery Behaviors initialized')

    def laser_callback(self, msg):
        """Process laser data for obstacle detection"""
        self.obstacle_data = msg

    def nav_status_callback(self, msg):
        """Monitor navigation status for recovery triggers"""
        self.nav_status = msg.data
        if msg.data == 'STUCK' or msg.data == 'OBSTACLE_DETECTED':
            self.trigger_recovery()

    def trigger_recovery(self):
        """Determine and trigger appropriate recovery behavior"""
        if self.recovery_active:
            return  # Already executing recovery

        # Analyze obstacle data to determine recovery strategy
        if self.obstacle_data:
            recovery_type = self.analyze_obstacle_and_select_recovery()
            if recovery_type:
                self.execute_recovery_behavior(recovery_type)

    def analyze_obstacle_and_select_recovery(self):
        """Analyze obstacles and select recovery behavior"""
        if not self.obstacle_data:
            return None

        # Divide scan into regions
        scan = self.obstacle_data
        front_scan = scan.ranges[len(scan.ranges)//2 - 30:len(scan.ranges)//2 + 30]  # Front 60 degrees
        left_scan = scan.ranges[:len(scan.ranges)//4]  # Left quarter
        right_scan = scan.ranges[-len(scan.ranges)//4:]  # Right quarter

        front_clear = min(front_scan) > 1.0  # 1m clearance
        left_clear = min(left_scan) > 1.0
        right_clear = min(right_scan) > 1.0

        # Determine recovery strategy based on environment
        if front_clear:
            return 'FORWARD_JITTER'  # Try going forward again
        elif left_clear and right_clear:
            return 'RANDOM_TURN'  # Choose randomly
        elif left_clear:
            return 'TURN_LEFT'  # Turn left
        elif right_clear:
            return 'TURN_RIGHT'  # Turn right
        else:
            return 'SPIN_IN_PLACE'  # Turn around

    def execute_recovery_behavior(self, recovery_type):
        """Execute selected recovery behavior"""
        self.current_recovery = recovery_type
        self.recovery_active = True

        self.get_logger().info(f'Executing recovery behavior: {recovery_type}')

        if recovery_type == 'FORWARD_JITTER':
            self.execute_forward_jitter()
        elif recovery_type == 'TURN_LEFT':
            self.execute_turn_left()
        elif recovery_type == 'TURN_RIGHT':
            self.execute_turn_right()
        elif recovery_type == 'SPIN_IN_PLACE':
            self.execute_spin_in_place()
        elif recovery_type == 'RANDOM_TURN':
            self.execute_random_turn()

    def execute_forward_jitter(self):
        """Execute forward movement with small random adjustments"""
        cmd = Twist()
        cmd.linear.x = 0.2  # Slow forward
        cmd.angular.z = np.random.uniform(-0.2, 0.2)  # Small random turn
        self.cmd_vel_pub.publish(cmd)

    def execute_turn_left(self):
        """Execute turn left behavior"""
        cmd = Twist()
        cmd.angular.z = 0.3  # Turn left
        cmd.linear.x = 0.0
        self.cmd_vel_pub.publish(cmd)

    def execute_turn_right(self):
        """Execute turn right behavior"""
        cmd = Twist()
        cmd.angular.z = -0.3  # Turn right
        cmd.linear.x = 0.0
        self.cmd_vel_pub.publish(cmd)

    def execute_spin_in_place(self):
        """Execute spin in place behavior"""
        cmd = Twist()
        cmd.angular.z = 0.5  # Spin right
        cmd.linear.x = 0.0
        self.cmd_vel_pub.publish(cmd)

    def execute_random_turn(self):
        """Execute random turn behavior"""
        cmd = Twist()
        cmd.angular.z = np.random.uniform(-0.5, 0.5)  # Random turn
        cmd.linear.x = 0.0
        self.cmd_vel_pub.publish(cmd)

    def execute_recovery(self):
        """Main recovery execution loop"""
        if not self.recovery_active or not self.current_recovery:
            return

        # Check if recovery should continue
        if self.nav_status == 'ACTIVE':  # Navigation resumed
            self.recovery_active = False
            self.current_recovery = None
            # Stop robot
            stop_cmd = Twist()
            self.cmd_vel_pub.publish(stop_cmd)
            self.get_logger().info('Recovery completed, navigation resumed')
            return

        # Continue current recovery behavior (will be repeated by timer)
        pass

def main(args=None):
    rclpy.init(args=args)
    recovery_node = HumanoidRecoveryBehaviors()

    try:
        rclpy.spin(recovery_node)
    except KeyboardInterrupt:
        recovery_node.get_logger().info('Shutting down Humanoid Recovery Behaviors')
    finally:
        recovery_node.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()
```

## Integration with VSLAM and Perception

Integrating Nav2 with VSLAM systems:

```python
import rclpy
from rclpy.node import Node
from geometry_msgs.msg import PoseStamped
from nav_msgs.msg import OccupancyGrid
from sensor_msgs.msg import Image, PointCloud2
from geometry_msgs.msg import Twist
from tf2_ros import Buffer, TransformListener
import tf2_geometry_msgs
import numpy as np
from scipy.ndimage import binary_dilation
import threading

class IntegratedNavigation(Node):
    def __init__(self):
        super().__init__('integrated_navigation')

        # Publishers
        self.local_map_pub = self.create_publisher(OccupancyGrid, '/local_costmap/costmap', 10)
        self.vslam_goal_pub = self.create_publisher(PoseStamped, '/vslam_goal', 10)

        # Subscribers
        self.vslam_pose_sub = self.create_subscription(
            PoseStamped, '/visual_pose', self.vslam_pose_callback, 10
        )
        self.rgb_sub = self.create_subscription(
            Image, '/camera/rgb/image_raw', self.rgb_callback, 10
        )
        self.depth_sub = self.create_subscription(
            Image, '/camera/depth/image_raw', self.depth_callback, 10
        )

        # TF2 for coordinate transformations
        self.tf_buffer = Buffer()
        self.tf_listener = TransformListener(self.tf_buffer, self)

        # Integration state
        self.vslam_pose = None
        self.latest_rgb = None
        self.latest_depth = None
        self.local_map = None
        self.update_lock = threading.Lock()

        # Navigation parameters
        self.map_resolution = 0.05  # 5cm resolution
        self.map_width = 200  # 10m x 10m map
        self.map_height = 200

        # Timer for map updates
        self.map_update_timer = self.create_timer(0.5, self.update_local_map)

        self.get_logger().info('Integrated Navigation system initialized')

    def vslam_pose_callback(self, msg):
        """Update pose from VSLAM system"""
        self.vslam_pose = msg

    def rgb_callback(self, msg):
        """Process RGB image from camera"""
        # Store latest RGB image
        self.latest_rgb = msg

    def depth_callback(self, msg):
        """Process depth image for obstacle detection"""
        # Store latest depth image
        self.latest_depth = msg

    def update_local_map(self):
        """Update local occupancy grid using depth data and VSLAM pose"""
        if not self.vslam_pose or not self.latest_depth:
            return

        with self.update_lock:
            # Create local map based on depth data
            self.local_map = self.create_local_occupancy_map(
                self.latest_depth,
                self.vslam_pose
            )

            # Publish local map
            if self.local_map is not None:
                self.local_map_pub.publish(self.local_map)

    def create_local_occupancy_map(self, depth_msg, robot_pose):
        """Create occupancy grid from depth data centered on robot"""
        # In practice, this would process the depth image to detect obstacles
        # For this example, we'll create a dummy map

        map_msg = OccupancyGrid()
        map_msg.header.stamp = self.get_clock().now().to_msg()
        map_msg.header.frame_id = 'map'
        map_msg.info.resolution = self.map_resolution
        map_msg.info.width = self.map_width
        map_msg.info.height = self.map_height

        # Set origin to robot position
        map_msg.info.origin.position.x = robot_pose.pose.position.x - (self.map_width * self.map_resolution / 2)
        map_msg.info.origin.position.y = robot_pose.pose.position.y - (self.map_height * self.map_resolution / 2)

        # Create dummy occupancy data (0 = free, 100 = occupied)
        occupancy_data = np.zeros(self.map_width * self.map_height, dtype=np.int8)

        # Add some dummy obstacles
        for i in range(20):
            x = np.random.randint(0, self.map_width)
            y = np.random.randint(0, self.map_height)
            idx = y * self.map_width + x
            if 0 <= idx < len(occupancy_data):
                occupancy_data[idx] = 100

        map_msg.data = occupancy_data.tolist()

        return map_msg

    def transform_goal_to_map_frame(self, goal_pose):
        """Transform goal to map frame using TF"""
        try:
            transform = self.tf_buffer.lookup_transform(
                'map',
                goal_pose.header.frame_id,
                rclpy.time.Time(),
                rclpy.time.Duration(seconds=1.0)
            )
            transformed_goal = tf2_geometry_msgs.do_transform_pose(goal_pose, transform)
            return transformed_goal
        except Exception as e:
            self.get_logger().error(f'Transform failed: {e}')
            return None

def main(args=None):
    rclpy.init(args=args)
    integrated_nav = IntegratedNavigation()

    try:
        rclpy.spin(integrated_nav)
    except KeyboardInterrupt:
        integrated_nav.get_logger().info('Shutting down Integrated Navigation')
    finally:
        integrated_nav.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()
```

## Best Practices for Humanoid Navigation

1. **Stability Considerations**: Ensure paths maintain robot stability
2. **Kinematic Constraints**: Respect joint limits and movement constraints
3. **Terrain Analysis**: Consider terrain passability for bipedal locomotion
4. **Dynamic Planning**: Adapt plans based on changing environment
5. **Safety Margins**: Include larger safety margins than wheeled robots
6. **Balance Recovery**: Integrate with balance recovery systems

## Configuration for Humanoid Robots

Nav2 configuration for humanoid robots typically requires:

### Costmap Parameters

```yaml
local_costmap:
  local_costmap:
    ros__parameters:
      update_frequency: 5.0
      publish_frequency: 2.0
      global_frame: map
      robot_base_frame: base_link
      use_rollout_costs: true
      always_send_full_costmap: true
      footprint: [ [0.3, 0.2], [0.3, -0.2], [-0.3, -0.2], [-0.3, 0.2] ]
      footprint_padding: 0.02
      resolution: 0.05
      robot_radius: 0.3
      plugins: ["obstacle_layer", "voxel_layer", "inflation_layer"]

      obstacle_layer:
        plugin: "nav2_costmap_2d::ObstacleLayer"
        enabled: True
        observation_sources: scan
        scan:
          topic: /scan
          max_obstacle_height: 2.0
          clearing: True
          marking: True
          data_type: "LaserScan"
          raytrace_max_range: 3.0
          raytrace_min_range: 0.0
          obstacle_max_range: 2.5
          obstacle_min_range: 0.0

      inflation_layer:
        plugin: "nav2_costmap_2d::InflationLayer"
        enabled: True
        cost_scaling_factor: 3.0
        inflation_radius: 0.5  # Larger than typical wheeled robots
        inflate_unknown: false

global_costmap:
  global_costmap:
    ros__parameters:
      update_frequency: 1.0
      publish_frequency: 1.0
      global_frame: map
      robot_base_frame: base_link
      robot_radius: 0.3
      resolution: 0.05
      track_unknown_space: true
      plugins: ["static_layer", "obstacle_layer", "inflation_layer"]
```

## Hands-on Exercise

Create a complete navigation system for a humanoid robot that:
1. Integrates with your VSLAM system from Module 3
2. Implements footstep planning for bipedal locomotion
3. Includes humanoid-specific recovery behaviors
4. Uses behavior trees for complex navigation tasks
5. Incorporates sensor data for dynamic obstacle avoidance

This exercise will help you understand how to adapt navigation systems for the unique challenges of humanoid robots.