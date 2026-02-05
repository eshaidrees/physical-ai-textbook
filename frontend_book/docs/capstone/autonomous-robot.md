---
sidebar_position: 2
---

# Capstone Project Implementation Guide

This guide provides a step-by-step implementation approach for the capstone project, helping you build a complete autonomous humanoid robot system that integrates all course concepts.

## Project Setup and Environment

### Prerequisites

Before starting the capstone project, ensure you have:

- ROS 2 Humble Hawksbill installed
- Gazebo Garden for simulation
- Unity 2022.3 LTS for visualization
- NVIDIA Isaac Sim (if using Isaac modules)
- Python 3.8+ with required packages
- Appropriate hardware or cloud resources

### Initial Project Structure

```bash
capstone_project/
├── src/
│   ├── robot_system/
│   │   ├── __init__.py
│   │   ├── main.py
│   │   ├── perception/
│   │   ├── navigation/
│   │   ├── manipulation/
│   │   └── interfaces/
│   ├── simulation/
│   │   ├── gazebo/
│   │   ├── unity/
│   │   └── digital_twin/
│   └── ai_models/
│       ├── vision/
│       ├── nlp/
│       └── planning/
├── config/
├── launch/
├── worlds/
├── models/
├── test/
└── docs/
```

### Environment Configuration

```python
# config/environment.py
"""
Environment configuration for capstone project
"""

import os
from dataclasses import dataclass
from typing import Dict, Any

@dataclass
class RobotConfig:
    """Configuration for the humanoid robot"""
    robot_name: str = "humanoid_robot"
    joint_names: list = None
    base_frame: str = "base_link"
    camera_frame: str = "camera_link"
    gripper_frame: str = "gripper_link"

    def __post_init__(self):
        if self.joint_names is None:
            self.joint_names = [
                'left_hip_joint', 'left_knee_joint', 'left_ankle_joint',
                'right_hip_joint', 'right_knee_joint', 'right_ankle_joint',
                'left_shoulder_joint', 'left_elbow_joint', 'left_wrist_joint',
                'right_shoulder_joint', 'right_elbow_joint', 'right_wrist_joint',
                'head_joint'
            ]

@dataclass
class SystemConfig:
    """System-wide configuration"""
    ros_domain_id: int = 0
    simulation_mode: bool = True
    debug_mode: bool = False
    log_level: str = "INFO"
    max_threads: int = 8

    # Performance thresholds
    max_navigation_time: float = 60.0  # seconds
    min_detection_accuracy: float = 0.85
    max_command_response_time: float = 5.0  # seconds

class CapstoneEnvironment:
    """Environment manager for the capstone project"""

    def __init__(self):
        self.robot_config = RobotConfig()
        self.system_config = SystemConfig()
        self._setup_environment()

    def _setup_environment(self):
        """Setup environment variables and configurations"""
        # Set ROS domain ID
        os.environ['ROS_DOMAIN_ID'] = str(self.system_config.ros_domain_id)

        # Set log level
        os.environ['RCUTILS_LOGGING_SEVERITY_THRESHOLD'] = self.system_config.log_level

        # Create necessary directories
        directories = [
            'logs',
            'data',
            'models',
            'config',
            'results'
        ]

        for directory in directories:
            os.makedirs(directory, exist_ok=True)

    def get_config(self) -> Dict[str, Any]:
        """Get complete system configuration"""
        return {
            'robot': self.robot_config.__dict__,
            'system': self.system_config.__dict__
        }

# Initialize environment
ENVIRONMENT = CapstoneEnvironment()
```

## Implementation Phase 1: Core System Integration

### Main System Node

```python
#!/usr/bin/env python3
"""
Main capstone system node
"""

import rclpy
from rclpy.node import Node
from rclpy.qos import QoSProfile, DurabilityPolicy
from std_msgs.msg import String, Bool, Float32
from sensor_msgs.msg import JointState, Image, LaserScan
from geometry_msgs.msg import Pose, Twist, Point
from nav_msgs.msg import Odometry
from builtin_interfaces.msg import Time
import json
import threading
import time
import logging
from typing import Dict, List, Optional, Any

from config.environment import ENVIRONMENT, RobotConfig, SystemConfig

class CapstoneSystemNode(Node):
    """Main node for the capstone robot system"""

    def __init__(self):
        super().__init__('capstone_system')

        # Get configuration
        self.config = ENVIRONMENT.get_config()
        self.robot_config = RobotConfig()
        self.system_config = SystemConfig()

        # Setup logging
        self.setup_logging()

        # Initialize subsystems
        self.subsystems = {
            'perception': PerceptionSubsystem(self),
            'navigation': NavigationSubsystem(self),
            'manipulation': ManipulationSubsystem(self),
            'nlp': NaturalLanguageSubsystem(self),
            'simulation': SimulationSubsystem(self)
        }

        # Setup communication
        self.setup_communication()

        # System state
        self.system_state = {
            'initialized': False,
            'active': False,
            'safety_status': 'nominal',
            'last_command_time': 0.0,
            'active_task': None
        }

        # Initialize the system
        self.initialize_system()

        self.get_logger().info('Capstone System Node initialized successfully')

    def setup_logging(self):
        """Setup logging configuration"""
        logging.basicConfig(
            level=getattr(logging, self.system_config.log_level),
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger(__name__)

    def setup_communication(self):
        """Setup ROS 2 communication interfaces"""
        # QoS profile for reliable communication
        qos_profile = QoSProfile(depth=10)
        qos_profile.durability = DurabilityPolicy.TRANSIENT_LOCAL

        # Publishers
        self.status_pub = self.create_publisher(String, '/capstone/status', qos_profile)
        self.command_pub = self.create_publisher(String, '/capstone/commands', qos_profile)
        self.action_pub = self.create_publisher(String, '/capstone/actions', qos_profile)
        self.feedback_pub = self.create_publisher(String, '/capstone/feedback', qos_profile)

        # Subscribers
        self.command_sub = self.create_subscription(
            String, '/capstone/commands', self.command_callback, qos_profile)
        self.status_sub = self.create_subscription(
            String, '/capstone/subsystem_status', self.subsystem_status_callback, qos_profile)

        # Timer for system monitoring
        self.monitor_timer = self.create_timer(1.0, self.system_monitor)

    def initialize_system(self):
        """Initialize all subsystems"""
        self.get_logger().info('Initializing subsystems...')

        initialization_success = True

        for name, subsystem in self.subsystems.items():
            try:
                success = subsystem.initialize()
                if success:
                    self.get_logger().info(f'{name} subsystem initialized successfully')
                else:
                    self.get_logger().error(f'{name} subsystem failed to initialize')
                    initialization_success = False
            except Exception as e:
                self.get_logger().error(f'Error initializing {name} subsystem: {e}')
                initialization_success = False

        if initialization_success:
            self.system_state['initialized'] = True
            self.get_logger().info('All subsystems initialized successfully')
        else:
            self.get_logger().error('System initialization failed')

    def command_callback(self, msg):
        """Handle incoming commands"""
        try:
            command_data = json.loads(msg.data)
            command_type = command_data.get('type', 'unknown')

            self.get_logger().info(f'Received command: {command_type}')
            self.system_state['last_command_time'] = self.get_clock().now().nanoseconds / 1e9

            # Route command to appropriate subsystem
            if command_type == 'natural_language':
                self.subsystems['nlp'].process_command(command_data)
            elif command_type == 'navigation':
                self.subsystems['navigation'].execute_command(command_data)
            elif command_type == 'manipulation':
                self.subsystems['manipulation'].execute_command(command_data)
            elif command_type == 'perception':
                self.subsystems['perception'].execute_command(command_data)
            else:
                self.get_logger().warn(f'Unknown command type: {command_type}')
                self.send_feedback(f'Unknown command type: {command_type}')

        except json.JSONDecodeError:
            self.get_logger().error('Invalid JSON command received')
        except Exception as e:
            self.get_logger().error(f'Error processing command: {e}')
            self.send_feedback(f'Command processing error: {e}')

    def subsystem_status_callback(self, msg):
        """Handle subsystem status updates"""
        try:
            status_data = json.loads(msg.data)
            subsystem_name = status_data.get('subsystem', 'unknown')

            # Update system state based on subsystem status
            if status_data.get('status') == 'error':
                self.system_state['safety_status'] = 'degraded'
                self.emergency_stop()
        except json.JSONDecodeError:
            self.get_logger().error('Invalid JSON status message')
        except Exception as e:
            self.get_logger().error(f'Error processing status: {e}')

    def system_monitor(self):
        """Monitor system health and safety"""
        if not self.system_state['initialized']:
            return

        # Check subsystem health
        all_healthy = all(subsystem.is_healthy() for subsystem in self.subsystems.values())

        # Update system state
        self.system_state['subsystems_healthy'] = all_healthy
        self.system_state['timestamp'] = self.get_clock().now().nanoseconds / 1e9

        # Safety checks
        if not all_healthy:
            self.system_state['safety_status'] = 'degraded'
            self.emergency_stop()
        else:
            self.system_state['safety_status'] = 'nominal'

        # Publish system status
        status_msg = String()
        status_msg.data = json.dumps(self.system_state)
        self.status_pub.publish(status_msg)

    def emergency_stop(self):
        """Emergency stop procedure"""
        self.get_logger().warn('Emergency stop activated!')

        # Send stop commands to all subsystems
        stop_command = {
            'type': 'emergency_stop',
            'reason': 'system_safety_check_failed',
            'timestamp': time.time()
        }

        stop_msg = String()
        stop_msg.data = json.dumps(stop_command)
        self.command_pub.publish(stop_msg)

        # Stop any active tasks
        if self.system_state['active_task']:
            self.get_logger().info(f'Cancelling active task: {self.system_state["active_task"]}')
            self.system_state['active_task'] = None

    def send_feedback(self, message: str):
        """Send feedback message"""
        feedback_msg = String()
        feedback_msg.data = json.dumps({
            'message': message,
            'timestamp': time.time()
        })
        self.feedback_pub.publish(feedback_msg)

class BaseSubsystem:
    """Base class for all subsystems"""

    def __init__(self, parent_node: CapstoneSystemNode):
        self.parent_node = parent_node
        self.node = parent_node
        self.initialized = False

    def initialize(self) -> bool:
        """Initialize the subsystem"""
        raise NotImplementedError

    def is_healthy(self) -> bool:
        """Check if subsystem is healthy"""
        return self.initialized

    def execute_command(self, command_data: Dict[str, Any]):
        """Execute a command"""
        raise NotImplementedError

class PerceptionSubsystem(BaseSubsystem):
    """Perception subsystem for vision and sensing"""

    def __init__(self, parent_node: CapstoneSystemNode):
        super().__init__(parent_node)
        self.vision_processor = None
        self.slam_system = None
        self.object_detector = None

    def initialize(self) -> bool:
        """Initialize perception subsystem"""
        try:
            # Initialize vision processing components
            self.vision_processor = VisionProcessor()
            self.slam_system = SLAMSystem()
            self.object_detector = ObjectDetector()

            # Setup ROS interfaces
            qos_profile = self.node.get_publisher_qos_profile_by_topic('/camera/image_raw')
            self.image_sub = self.node.create_subscription(
                Image, '/camera/image_raw', self.image_callback, qos_profile)

            self.initialized = True
            return True
        except Exception as e:
            self.node.get_logger().error(f'Perception subsystem initialization failed: {e}')
            return False

    def image_callback(self, msg: Image):
        """Handle incoming camera images"""
        try:
            # Process image for perception tasks
            results = self.vision_processor.process_image(msg)

            # Update SLAM system
            self.slam_system.update_with_image(msg, results)

            # Detect objects
            objects = self.object_detector.detect(msg, results)

            # Publish perception results
            perception_msg = String()
            perception_msg.data = json.dumps({
                'objects': objects,
                'features': results,
                'timestamp': self.node.get_clock().now().nanoseconds / 1e9
            })
            # self.perception_pub.publish(perception_msg)  # Would need to create publisher

        except Exception as e:
            self.node.get_logger().error(f'Error in perception processing: {e}')

    def execute_command(self, command_data: Dict[str, Any]):
        """Execute perception command"""
        command = command_data.get('command', '')

        if command == 'detect_objects':
            # Trigger object detection
            pass
        elif command == 'build_map':
            # Trigger SLAM mapping
            pass
        elif command == 'localize':
            # Trigger localization
            pass

class NavigationSubsystem(BaseSubsystem):
    """Navigation subsystem for path planning and movement"""

    def __init__(self, parent_node: CapstoneSystemNode):
        super().__init__(parent_node)
        self.path_planner = None
        self.localizer = None
        self.controller = None

    def initialize(self) -> bool:
        """Initialize navigation subsystem"""
        try:
            self.path_planner = PathPlanner()
            self.localizer = Localizer()
            self.controller = MotionController()

            self.initialized = True
            return True
        except Exception as e:
            self.node.get_logger().error(f'Navigation subsystem initialization failed: {e}')
            return False

    def execute_command(self, command_data: Dict[str, Any]):
        """Execute navigation command"""
        target = command_data.get('target', {})

        if 'pose' in target:
            self.navigate_to_pose(target['pose'])
        elif 'location_name' in target:
            self.navigate_to_location(target['location_name'])

    def navigate_to_pose(self, pose: Dict[str, float]):
        """Navigate to specific pose"""
        current_pose = self.localizer.get_current_pose()
        path = self.path_planner.plan_path(current_pose, pose)
        self.controller.follow_path(path)

    def navigate_to_location(self, location_name: str):
        """Navigate to named location"""
        location_pose = self.get_predefined_location(location_name)
        if location_pose:
            self.navigate_to_pose(location_pose)

    def get_predefined_location(self, name: str) -> Optional[Dict[str, float]]:
        """Get predefined location by name"""
        locations = {
            'kitchen': {'x': 1.0, 'y': 2.0, 'theta': 0.0},
            'living_room': {'x': -1.0, 'y': 1.0, 'theta': 1.57},
            'bedroom': {'x': 0.0, 'y': -2.0, 'theta': 3.14},
            'office': {'x': 2.0, 'y': 0.0, 'theta': -1.57}
        }
        return locations.get(name)

class ManipulationSubsystem(BaseSubsystem):
    """Manipulation subsystem for arm control and object interaction"""

    def __init__(self, parent_node: CapstoneSystemNode):
        super().__init__(parent_node)
        self.kinematics = None
        self.gripper_controller = None
        self.motion_planner = None

    def initialize(self) -> bool:
        """Initialize manipulation subsystem"""
        try:
            self.kinematics = KinematicsSolver()
            self.gripper_controller = GripperController()
            self.motion_planner = MotionPlanner()

            self.initialized = True
            return True
        except Exception as e:
            self.node.get_logger().error(f'Manipulation subsystem initialization failed: {e}')
            return False

    def execute_command(self, command_data: Dict[str, Any]):
        """Execute manipulation command"""
        action = command_data.get('action', '')
        target = command_data.get('target', {})

        if action == 'grasp':
            self.grasp_object(target)
        elif action == 'place':
            self.place_object(target)
        elif action == 'move_to':
            self.move_to_pose(target)

class NaturalLanguageSubsystem(BaseSubsystem):
    """Natural language processing subsystem"""

    def __init__(self, parent_node: CapstoneSystemNode):
        super().__init__(parent_node)
        self.nlp_engine = None
        self.command_parser = None

    def initialize(self) -> bool:
        """Initialize NLP subsystem"""
        try:
            self.nlp_engine = NLPEngine()
            self.command_parser = CommandParser()

            self.initialized = True
            return True
        except Exception as e:
            self.node.get_logger().error(f'NLP subsystem initialization failed: {e}')
            return False

    def process_command(self, command_data: Dict[str, Any]):
        """Process natural language command"""
        text = command_data.get('text', '')

        # Parse command
        structured_command = self.command_parser.parse(text)

        if structured_command:
            # Route to appropriate subsystem
            intent = structured_command.get('intent', '')

            if intent == 'navigation':
                self.parent_node.subsystems['navigation'].execute_command(structured_command)
            elif intent == 'manipulation':
                self.parent_node.subsystems['manipulation'].execute_command(structured_command)
            elif intent == 'perception':
                self.parent_node.subsystems['perception'].execute_command(structured_command)

    def execute_command(self, command_data: Dict[str, Any]):
        """Execute NLP command"""
        self.process_command(command_data)

class SimulationSubsystem(BaseSubsystem):
    """Simulation interface subsystem"""

    def __init__(self, parent_node: CapstoneSystemNode):
        super().__init__(parent_node)
        self.gazebo_interface = None
        self.unity_bridge = None

    def initialize(self) -> bool:
        """Initialize simulation subsystem"""
        try:
            self.gazebo_interface = GazeboInterface()
            self.unity_bridge = UnityBridge()

            self.initialized = True
            return True
        except Exception as e:
            self.node.get_logger().error(f'Simulation subsystem initialization failed: {e}')
            return False

    def execute_command(self, command_data: Dict[str, Any]):
        """Execute simulation command"""
        command = command_data.get('command', '')

        if command == 'sync_state':
            self.synchronize_with_simulation()
        elif command == 'reset_world':
            self.reset_simulation_world()

def main(args=None):
    """Main entry point for the capstone system"""
    rclpy.init(args=args)

    try:
        node = CapstoneSystemNode()

        # Spin the node
        rclpy.spin(node)

    except KeyboardInterrupt:
        print('Interrupted by user')
    finally:
        node.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()
```

## Implementation Phase 2: Testing and Validation

### Comprehensive Test Suite

```python
import unittest
import rclpy
from rclpy.node import Node
from std_msgs.msg import String
import json
import time
from typing import Dict, Any

class TestCapstoneSystem(unittest.TestCase):
    """Test suite for the capstone robot system"""

    @classmethod
    def setUpClass(cls):
        """Setup for all tests"""
        rclpy.init()
        cls.test_node = rclpy.create_node('capstone_test_node')

        # Create publishers and subscribers for testing
        cls.command_publisher = cls.test_node.create_publisher(
            String, '/capstone/commands', 10)
        cls.status_subscriber = cls.test_node.create_subscription(
            String, '/capstone/status', cls.status_callback, 10)

        cls.received_status = None
        cls.status_received = False

    @classmethod
    def status_callback(cls, msg):
        """Callback to receive system status"""
        cls.received_status = msg.data
        cls.status_received = True

    def setUp(self):
        """Setup before each test"""
        self.received_status = None
        self.status_received = False

    def test_system_initialization(self):
        """Test that the system initializes correctly"""
        # Check that system status is published
        timeout = time.time() + 10.0  # 10 second timeout
        while not self.status_received and time.time() < timeout:
            rclpy.spin_once(self.test_node, timeout_sec=0.1)

        self.assertTrue(self.status_received, "System status not received")

        if self.received_status:
            status_data = json.loads(self.received_status)
            self.assertTrue(status_data.get('initialized', False), "System not initialized")

    def test_natural_language_navigation(self):
        """Test navigation through natural language command"""
        # Send natural language navigation command
        command = {
            'type': 'natural_language',
            'text': 'go to the kitchen',
            'timestamp': time.time()
        }

        command_msg = String()
        command_msg.data = json.dumps(command)
        self.command_publisher.publish(command_msg)

        # Wait for system response
        timeout = time.time() + 30.0  # 30 second timeout
        while not self.status_received and time.time() < timeout:
            rclpy.spin_once(self.test_node, timeout_sec=0.1)

        self.assertTrue(self.status_received, "No status received after navigation command")

    def test_perception_pipeline(self):
        """Test the perception pipeline"""
        # Send perception command
        command = {
            'type': 'perception',
            'command': 'detect_objects',
            'parameters': {'sensor': 'camera'},
            'timestamp': time.time()
        }

        command_msg = String()
        command_msg.data = json.dumps(command)
        self.command_publisher.publish(command_msg)

        # Wait for response
        timeout = time.time() + 15.0
        while not self.status_received and time.time() < timeout:
            rclpy.spin_once(self.test_node, timeout_sec=0.1)

        self.assertTrue(self.status_received, "No status received after perception command")

    def test_manipulation_pipeline(self):
        """Test the manipulation pipeline"""
        # Send manipulation command
        command = {
            'type': 'manipulation',
            'command': 'grasp',
            'target': {'object': 'cup', 'pose': {'x': 0.5, 'y': 0.3, 'z': 0.8}},
            'timestamp': time.time()
        }

        command_msg = String()
        command_msg.data = json.dumps(command)
        self.command_publisher.publish(command_msg)

        # Wait for response
        timeout = time.time() + 25.0
        while not self.status_received and time.time() < timeout:
            rclpy.spin_once(self.test_node, timeout_sec=0.1)

        self.assertTrue(self.status_received, "No status received after manipulation command")

    def test_system_safety(self):
        """Test system safety mechanisms"""
        # Test emergency stop functionality
        command = {
            'type': 'emergency_stop',
            'reason': 'test_safety',
            'timestamp': time.time()
        }

        command_msg = String()
        command_msg.data = json.dumps(command)
        self.command_publisher.publish(command_msg)

        # Wait for safety response
        timeout = time.time() + 10.0
        while not self.status_received and time.time() < timeout:
            rclpy.spin_once(self.test_node, timeout_sec=0.1)

        self.assertTrue(self.status_received, "No status received after safety command")

    @classmethod
    def tearDownClass(cls):
        """Cleanup after all tests"""
        cls.test_node.destroy_node()
        rclpy.shutdown()

class PerformanceTestSuite(unittest.TestCase):
    """Performance tests for the capstone system"""

    def test_navigation_performance(self):
        """Test navigation performance metrics"""
        # This would involve measuring navigation accuracy, time, etc.
        # Implementation would depend on simulation environment
        pass

    def test_perception_accuracy(self):
        """Test perception system accuracy"""
        # This would involve running perception tests with known objects
        pass

    def test_command_response_time(self):
        """Test system response time to commands"""
        start_time = time.time()

        # Send a simple command
        command = {
            'type': 'status_check',
            'timestamp': start_time
        }

        # Measure response time
        response_time = time.time() - start_time

        # Assert response time is within acceptable bounds
        self.assertLess(response_time, 5.0, "Command response time too slow")

def run_all_tests():
    """Run all test suites"""
    print("Running Capstone System Tests...")

    # Create test suite
    test_suite = unittest.TestSuite()

    # Add tests
    test_suite.addTest(unittest.makeSuite(TestCapstoneSystem))
    test_suite.addTest(unittest.makeSuite(PerformanceTestSuite))

    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(test_suite)

    # Print results
    print(f"\nTests run: {result.testsRun}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    print(f"Success: {result.wasSuccessful()}")

    return result.wasSuccessful()

if __name__ == '__main__':
    success = run_all_tests()
    exit(0 if success else 1)
```

## Implementation Phase 3: Performance Optimization

### Performance Monitoring and Optimization

```python
import psutil
import time
from collections import deque, defaultdict
import threading
import statistics
from dataclasses import dataclass
from typing import Dict, List, Optional, Callable
import json

@dataclass
class PerformanceMetric:
    """Data class for performance metrics"""
    name: str
    value: float
    unit: str
    timestamp: float
    source: str

class PerformanceMonitor:
    """Monitor system performance in real-time"""

    def __init__(self):
        self.metrics_history = defaultdict(lambda: deque(maxlen=1000))
        self.system_metrics = {}
        self.process = psutil.Process()
        self.running = False
        self.monitor_thread = None

        # Performance thresholds
        self.thresholds = {
            'cpu_percent': 80.0,  # percent
            'memory_percent': 85.0,  # percent
            'response_time': 5.0,  # seconds
            'throughput': 10.0  # operations per second
        }

    def start_monitoring(self):
        """Start performance monitoring in a separate thread"""
        if not self.running:
            self.running = True
            self.monitor_thread = threading.Thread(target=self._monitor_loop, daemon=True)
            self.monitor_thread.start()

    def stop_monitoring(self):
        """Stop performance monitoring"""
        self.running = False
        if self.monitor_thread:
            self.monitor_thread.join()

    def _monitor_loop(self):
        """Main monitoring loop"""
        while self.running:
            # Collect system metrics
            cpu_percent = self.process.cpu_percent()
            memory_percent = self.process.memory_percent()
            memory_info = self.process.memory_info()

            # Record metrics
            self.record_metric('cpu_percent', cpu_percent, '%', 'system')
            self.record_metric('memory_percent', memory_percent, '%', 'system')
            self.record_metric('memory_rss', memory_info.rss, 'bytes', 'system')
            self.record_metric('memory_vms', memory_info.vms, 'bytes', 'system')

            # Sleep for 1 second
            time.sleep(1.0)

    def record_metric(self, name: str, value: float, unit: str, source: str):
        """Record a performance metric"""
        metric = PerformanceMetric(
            name=name,
            value=value,
            unit=unit,
            timestamp=time.time(),
            source=source
        )
        self.metrics_history[name].append(metric)

    def get_current_metrics(self) -> Dict[str, float]:
        """Get current system metrics"""
        if self.metrics_history['cpu_percent']:
            latest_cpu = self.metrics_history['cpu_percent'][-1].value
            latest_memory = self.metrics_history['memory_percent'][-1].value
        else:
            latest_cpu = self.process.cpu_percent()
            latest_memory = self.process.memory_percent()

        return {
            'cpu_percent': latest_cpu,
            'memory_percent': latest_memory,
            'process_id': self.process.pid,
            'num_threads': self.process.num_threads(),
            'connections': len(self.process.connections())
        }

    def get_historical_metrics(self, metric_name: str, window_seconds: int = 60) -> List[PerformanceMetric]:
        """Get historical metrics for a specific metric within a time window"""
        current_time = time.time()
        cutoff_time = current_time - window_seconds

        return [m for m in self.metrics_history[metric_name] if m.timestamp > cutoff_time]

    def check_thresholds(self) -> Dict[str, bool]:
        """Check if any metrics are exceeding thresholds"""
        current = self.get_current_metrics()
        violations = {}

        for metric, threshold in self.thresholds.items():
            if metric in current and current[metric] > threshold:
                violations[metric] = True

        return violations

    def generate_performance_report(self) -> Dict[str, Any]:
        """Generate a comprehensive performance report"""
        report = {
            'timestamp': time.time(),
            'system_metrics': self.get_current_metrics(),
            'threshold_violations': self.check_thresholds(),
            'historical_summary': {}
        }

        # Generate summary statistics for each metric
        for metric_name in self.metrics_history:
            values = [m.value for m in self.metrics_history[metric_name]]
            if values:
                report['historical_summary'][metric_name] = {
                    'mean': statistics.mean(values),
                    'median': statistics.median(values),
                    'min': min(values),
                    'max': max(values),
                    'std_dev': statistics.stdev(values) if len(values) > 1 else 0.0
                }

        return report

class OptimizedActionExecutor:
    """Optimized executor for robot actions with performance considerations"""

    def __init__(self):
        self.performance_monitor = PerformanceMonitor()
        self.performance_monitor.start_monitoring()

        # Action execution statistics
        self.execution_stats = {
            'total_executions': 0,
            'successful_executions': 0,
            'failed_executions': 0,
            'execution_times': deque(maxlen=100),
            'throughput': 0.0
        }

        # Optimization settings
        self.optimization_enabled = True
        self.adaptive_timeout = True
        self.resource_management = True

    def execute_action(self, action_plan: List[Dict], timeout: float = 30.0) -> Dict[str, Any]:
        """Execute an action plan with performance optimization"""
        start_time = time.time()
        result = {
            'success': False,
            'execution_time': 0.0,
            'steps_completed': 0,
            'error': None
        }

        try:
            # Check system resources before execution
            if self.resource_management:
                if not self._check_resources_before_execution():
                    result['error'] = 'Insufficient system resources'
                    return result

            # Execute each step in the plan
            steps_completed = 0
            for i, step in enumerate(action_plan):
                step_start = time.time()

                # Adaptive timeout based on system load
                if self.adaptive_timeout:
                    current_timeout = self._calculate_adaptive_timeout(timeout)
                else:
                    current_timeout = timeout

                # Execute the step
                step_success = self._execute_single_step(step, current_timeout)

                if step_success:
                    steps_completed += 1
                    self.performance_monitor.record_metric(
                        'step_execution_time',
                        time.time() - step_start,
                        'seconds',
                        f'step_{i}'
                    )
                else:
                    result['error'] = f'Step {i} failed: {step.get("action", "unknown")}'
                    break

            # Record execution results
            execution_time = time.time() - start_time
            result['success'] = steps_completed == len(action_plan)
            result['execution_time'] = execution_time
            result['steps_completed'] = steps_completed

            # Update statistics
            self.execution_stats['total_executions'] += 1
            if result['success']:
                self.execution_stats['successful_executions'] += 1
            else:
                self.execution_stats['failed_executions'] += 1

            self.execution_stats['execution_times'].append(execution_time)

            # Calculate throughput
            if len(self.execution_stats['execution_times']) > 0:
                avg_time = statistics.mean(self.execution_stats['execution_times'])
                self.execution_stats['throughput'] = 1.0 / avg_time if avg_time > 0 else 0.0

            # Record performance metric
            self.performance_monitor.record_metric(
                'action_execution_time',
                execution_time,
                'seconds',
                'action_executor'
            )

        except Exception as e:
            result['error'] = f'Execution error: {str(e)}'

        return result

    def _check_resources_before_execution(self) -> bool:
        """Check if system has sufficient resources for execution"""
        current_metrics = self.performance_monitor.get_current_metrics()

        # Check CPU usage
        if current_metrics.get('cpu_percent', 100) > 90:
            return False

        # Check memory usage
        if current_metrics.get('memory_percent', 100) > 95:
            return False

        return True

    def _calculate_adaptive_timeout(self, base_timeout: float) -> float:
        """Calculate adaptive timeout based on system load"""
        current_metrics = self.performance_monitor.get_current_metrics()

        cpu_load = current_metrics.get('cpu_percent', 50) / 100.0
        memory_load = current_metrics.get('memory_percent', 50) / 100.0

        # Increase timeout based on system load
        load_factor = (cpu_load + memory_load) / 2.0
        adaptive_timeout = base_timeout * (1.0 + load_factor)

        return min(adaptive_timeout, base_timeout * 2.0)  # Cap at 2x base timeout

    def _execute_single_step(self, step: Dict, timeout: float) -> bool:
        """Execute a single action step"""
        # This is a placeholder - actual implementation would depend on the specific action
        # For simulation purposes, we'll simulate the execution

        action_type = step.get('action', 'unknown')
        parameters = step.get('parameters', {})

        # Simulate different action types
        if action_type == 'navigate_to_pose':
            return self._execute_navigation_step(parameters, timeout)
        elif action_type == 'grasp_object':
            return self._execute_grasp_step(parameters, timeout)
        elif action_type == 'execute_behavior':
            return self._execute_behavior_step(parameters, timeout)
        else:
            # Simulate generic action execution
            time.sleep(0.1)  # Simulate work
            return True

    def _execute_navigation_step(self, params: Dict, timeout: float) -> bool:
        """Execute navigation step"""
        # Simulate navigation execution
        time.sleep(0.5)  # Simulate navigation time
        return True

    def _execute_grasp_step(self, params: Dict, timeout: float) -> bool:
        """Execute grasping step"""
        # Simulate grasping execution
        time.sleep(0.3)  # Simulate grasping time
        return True

    def _execute_behavior_step(self, params: Dict, timeout: float) -> bool:
        """Execute behavior step"""
        # Simulate behavior execution
        time.sleep(0.2)  # Simulate behavior time
        return True

    def get_performance_report(self) -> Dict[str, Any]:
        """Get performance report for the action executor"""
        return {
            'execution_stats': self.execution_stats,
            'system_performance': self.performance_monitor.generate_performance_report()
        }

    def optimize_execution(self):
        """Apply optimizations based on performance data"""
        if not self.optimization_enabled:
            return

        report = self.get_performance_report()
        system_performance = report['system_performance']

        # Adjust optimization parameters based on performance
        cpu_usage = system_performance['system_metrics'].get('cpu_percent', 50)
        memory_usage = system_performance['system_metrics'].get('memory_percent', 50)

        if cpu_usage > 80 or memory_usage > 85:
            # System is under high load, reduce parallelism
            self.adaptive_timeout = True
            self.resource_management = True
        else:
            # System has resources, can optimize for speed
            self.adaptive_timeout = False
            self.resource_management = False

# Integration with the main system
class OptimizedCapstoneSystemNode(CapstoneSystemNode):
    """Capstone system node with performance optimization"""

    def __init__(self):
        super().__init__()

        # Initialize performance optimization
        self.performance_monitor = PerformanceMonitor()
        self.action_executor = OptimizedActionExecutor()

        # Start monitoring
        self.performance_monitor.start_monitoring()

        # Performance monitoring timer
        self.performance_timer = self.create_timer(5.0, self.performance_callback)

        self.get_logger().info('Optimized Capstone System Node initialized')

    def performance_callback(self):
        """Callback for performance monitoring"""
        # Check for performance issues
        violations = self.performance_monitor.check_thresholds()

        if violations:
            self.get_logger().warn(f'Performance threshold violations: {violations}')
            self.action_executor.optimize_execution()

        # Publish performance metrics
        performance_data = self.action_executor.get_performance_report()

        performance_msg = String()
        performance_msg.data = json.dumps({
            'type': 'performance_metrics',
            'data': performance_data,
            'timestamp': self.get_clock().now().nanoseconds / 1e9
        })
        # Would need to create a publisher for performance data
        # self.performance_pub.publish(performance_msg)

    def destroy_node(self):
        """Cleanup when node is destroyed"""
        self.performance_monitor.stop_monitoring()
        super().destroy_node()

def main_optimized(args=None):
    """Main entry point for the optimized capstone system"""
    rclpy.init(args=args)

    try:
        node = OptimizedCapstoneSystemNode()

        # Spin the node
        rclpy.spin(node)

    except KeyboardInterrupt:
        print('Interrupted by user')
    finally:
        node.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main_optimized()
```

## Final Implementation and Deployment

### Complete Deployment Script

```python
#!/usr/bin/env python3
"""
Complete deployment script for the capstone project
"""

import subprocess
import sys
import os
import time
import json
import signal
import threading
from pathlib import Path
from typing import List, Dict, Any

class CapstoneDeployer:
    """Deployment manager for the capstone project"""

    def __init__(self):
        self.deployment_dir = Path.cwd()
        self.processes = []
        self.deployment_config = self._load_config()

    def _load_config(self) -> Dict[str, Any]:
        """Load deployment configuration"""
        config = {
            'nodes': [
                'capstone_system',
                'perception_node',
                'navigation_node',
                'manipulation_node',
                'simulation_bridge'
            ],
            'launch_files': [
                'capstone_system.launch.py',
                'perception_system.launch.py',
                'navigation_system.launch.py'
            ],
            'environment': {
                'ROS_DOMAIN_ID': '0',
                'RCUTILS_LOGGING_SEVERITY_THRESHOLD': 'INFO'
            }
        }
        return config

    def setup_environment(self):
        """Setup the deployment environment"""
        print("Setting up deployment environment...")

        # Create necessary directories
        directories = [
            'logs',
            'config',
            'data',
            'models',
            'results'
        ]

        for directory in directories:
            dir_path = self.deployment_dir / directory
            dir_path.mkdir(exist_ok=True)
            print(f"Created directory: {dir_path}")

        # Setup environment variables
        for var, value in self.deployment_config['environment'].items():
            os.environ[var] = value
            print(f"Set environment variable: {var}={value}")

        print("Environment setup complete")

    def start_nodes(self):
        """Start all ROS 2 nodes"""
        print("Starting ROS 2 nodes...")

        for node_name in self.deployment_config['nodes']:
            try:
                # Construct the command to run the node
                cmd = ['ros2', 'run', 'capstone_pkg', node_name]

                # Start the process
                process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                self.processes.append((node_name, process))

                print(f"Started node: {node_name} (PID: {process.pid})")

                # Give some time between starting nodes
                time.sleep(2)

            except Exception as e:
                print(f"Failed to start node {node_name}: {e}")

    def start_launch_files(self):
        """Start launch files"""
        print("Starting launch files...")

        for launch_file in self.deployment_config['launch_files']:
            try:
                launch_path = self.deployment_dir / 'launch' / launch_file
                if launch_path.exists():
                    cmd = ['ros2', 'launch', str(launch_path)]
                    process = subprocess.Popen(cmd)
                    self.processes.append((f"launch_{launch_file}", process))
                    print(f"Started launch file: {launch_file}")
                else:
                    print(f"Launch file not found: {launch_file}")
            except Exception as e:
                print(f"Failed to start launch file {launch_file}: {e}")

    def monitor_system(self):
        """Monitor the deployed system"""
        print("Monitoring system...")

        while True:
            active_processes = []
            for name, process in self.processes:
                if process.poll() is None:  # Process is still running
                    active_processes.append((name, process))
                else:
                    print(f"Process {name} has terminated with code: {process.returncode}")

            self.processes = active_processes

            if not self.processes:
                print("All processes have terminated")
                break

            time.sleep(5)  # Check every 5 seconds

    def stop_all(self):
        """Stop all running processes"""
        print("Stopping all processes...")

        for name, process in self.processes:
            print(f"Stopping {name} (PID: {process.pid})...")
            process.terminate()

            try:
                process.wait(timeout=5)  # Wait up to 5 seconds
            except subprocess.TimeoutExpired:
                print(f"Force killing {name}...")
                process.kill()

        self.processes.clear()
        print("All processes stopped")

    def deploy(self, with_monitoring=True):
        """Deploy the complete system"""
        print("Starting capstone project deployment...")

        try:
            # Setup environment
            self.setup_environment()

            # Start nodes
            self.start_nodes()

            # Start launch files
            self.start_launch_files()

            print("Deployment complete!")
            print(f"Started {len(self.processes)} processes")

            if with_monitoring:
                print("Starting system monitoring (Press Ctrl+C to stop)...")
                try:
                    self.monitor_system()
                except KeyboardInterrupt:
                    print("\nReceived interrupt signal")

        except Exception as e:
            print(f"Deployment error: {e}")
        finally:
            self.stop_all()
            print("Deployment finished")

def main():
    """Main deployment function"""
    if len(sys.argv) > 1 and sys.argv[1] == 'deploy':
        deployer = CapstoneDeployer()
        deployer.deploy()
    else:
        print("Usage: python deploy_capstone.py deploy")
        print("This will deploy the complete capstone robot system")

if __name__ == '__main__':
    main()
```

This completes the implementation guide for the capstone project. The guide provides a comprehensive approach to building an integrated autonomous humanoid robot system that combines all the concepts learned throughout the course.