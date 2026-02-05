---
sidebar_position: 4
---

# Digital Twin Concepts

This section explores the integration of Gazebo simulation and Unity visualization to create comprehensive digital twins for robotic systems. A digital twin combines physics-accurate simulation with high-fidelity visualization to create a complete virtual representation of a physical system.

## What is a Digital Twin?

A digital twin is a virtual representation of a physical system that enables real-time monitoring, simulation, and analysis. In robotics, a digital twin typically combines:
- Physics-accurate simulation (Gazebo)
- High-fidelity visualization (Unity)
- Real-time data synchronization
- Predictive modeling capabilities

## Digital Twin Architecture for Robotics

A typical digital twin architecture for robotics includes:

```
Physical Robot
       ↓ (Sensor Data)
Simulation Engine (Gazebo)
       ↕ (Synchronization)
Visualization Engine (Unity)
       ↓ (Rendering)
User Interface
```

### Key Components

1. **Physical System**: The actual robot in the real world
2. **Simulation Engine**: Gazebo for physics and sensor simulation
3. **Visualization Engine**: Unity for high-quality rendering
4. **Data Interface**: ROS 2 for communication
5. **User Interface**: For monitoring and control

## Implementing Digital Twin Synchronization

### Real-time Data Flow

To maintain synchronization between the physical robot and its digital twin:

```python
import rclpy
from rclpy.node import Node
from sensor_msgs.msg import JointState, LaserScan
from nav_msgs.msg import Odometry
from std_msgs.msg import String
import time

class DigitalTwinBridge(Node):
    def __init__(self):
        super().__init__('digital_twin_bridge')

        # Publishers for Unity visualization
        self.joint_pub = self.create_publisher(JointState, '/unity/joint_states', 10)
        self.odom_pub = self.create_publisher(Odometry, '/unity/odometry', 10)
        self.scan_pub = self.create_publisher(LaserScan, '/unity/scan', 10)

        # Subscribers for real robot data
        self.real_joint_sub = self.create_subscription(
            JointState, '/real_robot/joint_states', self.joint_callback, 10)
        self.real_odom_sub = self.create_subscription(
            Odometry, '/real_robot/odometry', self.odom_callback, 10)
        self.real_scan_sub = self.create_subscription(
            LaserScan, '/real_robot/scan', self.scan_callback, 10)

        # Timer for synchronization
        self.sync_timer = self.create_timer(0.033, self.synchronization_callback)  # ~30 Hz

        self.get_logger().info('Digital Twin Bridge initialized')

    def joint_callback(self, msg):
        # Forward joint states to Unity visualization
        self.joint_pub.publish(msg)

    def odom_callback(self, msg):
        # Forward odometry to Unity visualization
        self.odom_pub.publish(msg)

    def scan_callback(self, msg):
        # Forward scan data to Unity visualization
        self.scan_pub.publish(msg)

    def synchronization_callback(self):
        # Additional synchronization logic if needed
        pass

def main(args=None):
    rclpy.init(args=args)
    bridge = DigitalTwinBridge()

    try:
        rclpy.spin(bridge)
    except KeyboardInterrupt:
        bridge.get_logger().info('Shutting down digital twin bridge')
    finally:
        bridge.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()
```

### Unity Visualization Update Script

```csharp
using System.Collections;
using System.Collections.Generic;
using UnityEngine;
using Unity.Robotics.ROSTCPConnector;
using RosMessageTypes.Sensor;
using RosMessageTypes.Nav;

public class DigitalTwinVisualizer : MonoBehaviour
{
    [Header("Robot Components")]
    public Transform robotRoot;
    public List<Transform> jointTransforms = new List<Transform>();

    [Header("Visualization Settings")]
    public GameObject laserPointPrefab;
    public List<GameObject> laserPoints = new List<GameObject>();
    public int maxLaserPoints = 1000;

    private ROSConnection ros;
    private Dictionary<string, float> jointPositions = new Dictionary<string, float>();

    void Start()
    {
        ros = ROSConnection.GetOrCreateInstance();

        // Subscribe to robot data
        ros.Subscribe<JointStateMsg>("/unity/joint_states", UpdateJoints);
        ros.Subscribe<OdometryMsg>("/unity/odometry", UpdatePosition);
        ros.Subscribe<LaserScanMsg>("/unity/scan", UpdateLaserScan);
    }

    void UpdateJoints(JointStateMsg jointState)
    {
        for (int i = 0; i < jointState.name.Count; i++)
        {
            jointPositions[jointState.name[i]] = (float)jointState.position[i];
        }

        ApplyJointPositions();
    }

    void UpdatePosition(OdometryMsg odom)
    {
        Vector3 position = new Vector3(
            (float)odom.pose.pose.position.x,
            (float)odom.pose.pose.position.z,  // Swap Y/Z for Unity coordinate system
            (float)odom.pose.pose.position.y
        );

        Quaternion rotation = new Quaternion(
            (float)odom.pose.pose.orientation.x,
            (float)odom.pose.pose.orientation.z,
            (float)odom.pose.pose.orientation.y,
            (float)odom.pose.pose.orientation.w
        );

        if (robotRoot != null)
        {
            robotRoot.position = position;
            robotRoot.rotation = rotation;
        }
    }

    void UpdateLaserScan(LaserScanMsg scan)
    {
        // Clear existing laser points
        foreach (GameObject point in laserPoints)
        {
            if (point != null)
                DestroyImmediate(point);
        }
        laserPoints.Clear();

        // Create new laser points
        for (int i = 0; i < scan.ranges.Count; i += 5)  // Sample every 5th point
        {
            float range = (float)scan.ranges[i];
            if (range >= scan.range_min && range <= scan.range_max)
            {
                float angle = (float)(scan.angle_min + i * scan.angle_increment);

                Vector3 pointPos = new Vector3(
                    range * Mathf.Cos(angle),
                    0.1f,  // Height above ground
                    range * Mathf.Sin(angle)
                );

                GameObject pointObj = Instantiate(laserPointPrefab, pointPos, Quaternion.identity);
                laserPoints.Add(pointObj);

                if (laserPoints.Count >= maxLaserPoints)
                    break;
            }
        }
    }

    void ApplyJointPositions()
    {
        foreach (var joint in jointPositions)
        {
            Transform jointTransform = jointTransforms.Find(t => t.name == joint.Key);
            if (jointTransform != null)
            {
                // Apply rotation based on joint position
                jointTransform.localRotation = Quaternion.Euler(0, joint.Value * Mathf.Rad2Deg, 0);
            }
        }
    }
}
```

## Simulation-to-Reality Transfer

Digital twins help bridge the gap between simulation and reality:

### Domain Randomization

```python
import numpy as np
import random

class DomainRandomizer:
    def __init__(self):
        self.randomization_params = {
            'friction': (0.1, 0.9),  # Range for friction coefficients
            'mass_variance': 0.1,     # 10% variance in mass
            'lighting': (0.5, 1.5),  # Range for lighting intensity
            'texture': ['metal', 'wood', 'plastic', 'concrete']  # Texture variations
        }

    def randomize_environment(self):
        """Apply randomizations to simulation environment"""
        # Randomize friction coefficients
        friction = random.uniform(
            self.randomization_params['friction'][0],
            self.randomization_params['friction'][1]
        )

        # Randomize object masses
        mass_variance = self.randomization_params['mass_variance']

        # Randomize lighting conditions
        lighting = random.uniform(
            self.randomization_params['lighting'][0],
            self.randomization_params['lighting'][1]
        )

        # Randomize textures
        texture = random.choice(self.randomization_params['texture'])

        return {
            'friction': friction,
            'mass_variance': mass_variance,
            'lighting': lighting,
            'texture': texture
        }

    def apply_randomization(self, gazebo_model):
        """Apply randomization to a Gazebo model"""
        # Example: Randomize friction
        random_params = self.randomize_environment()

        # Update model properties in Gazebo
        # This would involve Gazebo services or plugins
        pass
```

### System Identification

```python
import numpy as np
from scipy import signal
import matplotlib.pyplot as plt

class SystemIdentifier:
    def __init__(self):
        self.simulation_data = []
        self.real_world_data = []

    def collect_data(self, sim_data, real_data):
        """Collect data from both simulation and real world"""
        self.simulation_data.append(sim_data)
        self.real_world_data.append(real_data)

    def identify_differences(self):
        """Identify systematic differences between sim and real"""
        if len(self.simulation_data) < 2 or len(self.real_world_data) < 2:
            return {}

        # Calculate mean differences
        sim_array = np.array(self.simulation_data)
        real_array = np.array(self.real_world_data)

        differences = real_array - sim_array

        # Calculate statistics
        mean_diff = np.mean(differences, axis=0)
        std_diff = np.std(differences, axis=0)

        return {
            'mean_difference': mean_diff,
            'std_difference': std_diff,
            'bias_correction': -mean_diff  # To correct sim to match real
        }

    def update_simulation(self, correction_params):
        """Update simulation parameters based on real-world data"""
        # Apply corrections to simulation physics
        pass
```

## Digital Twin Applications

### Remote Monitoring and Control

A digital twin enables remote monitoring of robot systems:

```python
import rclpy
from rclpy.node import Node
from std_msgs.msg import String
from sensor_msgs.msg import JointState
from geometry_msgs.msg import Twist
import json

class RemoteMonitoringNode(Node):
    def __init__(self):
        super().__init__('remote_monitoring')

        # Publishers for remote interface
        self.status_pub = self.create_publisher(String, '/remote/status', 10)
        self.joint_pub = self.create_publisher(JointState, '/remote/joint_states', 10)

        # Subscriber for remote commands
        self.command_sub = self.create_subscription(
            String, '/remote/commands', self.command_callback, 10)

        # Timer for status updates
        self.status_timer = self.create_timer(1.0, self.publish_status)

        self.robot_status = {
            'position': [0, 0, 0],
            'battery_level': 100.0,
            'operational': True,
            'task_status': 'idle'
        }

    def publish_status(self):
        """Publish robot status to remote interface"""
        status_msg = String()
        status_msg.data = json.dumps(self.robot_status)
        self.status_pub.publish(status_msg)

    def command_callback(self, msg):
        """Handle remote commands"""
        try:
            command = json.loads(msg.data)

            if command['type'] == 'move_to':
                # Execute movement command
                self.execute_movement(command['target'])
            elif command['type'] == 'inspect':
                # Perform inspection task
                self.execute_inspection()
            elif command['type'] == 'return_home':
                # Return to home position
                self.return_home()

        except json.JSONDecodeError:
            self.get_logger().error('Invalid JSON command received')

    def execute_movement(self, target):
        """Execute movement to target position"""
        self.get_logger().info(f'Moving to position: {target}')
        # Implementation would send commands to robot
        pass

def main(args=None):
    rclpy.init(args=args)
    node = RemoteMonitoringNode()

    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        node.get_logger().info('Shutting down remote monitoring')
    finally:
        node.destroy_node()
        rclpy.shutdown()
```

### Predictive Maintenance

Digital twins can predict maintenance needs:

```python
import numpy as np
from datetime import datetime, timedelta
import json

class PredictiveMaintenance:
    def __init__(self):
        self.component_data = {}
        self.maintenance_schedule = {}

    def update_component_status(self, component_name, data):
        """Update status of a robot component"""
        if component_name not in self.component_data:
            self.component_data[component_name] = {
                'data_history': [],
                'failure_threshold': 0.8,
                'last_maintenance': datetime.now()
            }

        # Store new data point
        self.component_data[component_name]['data_history'].append({
            'timestamp': datetime.now(),
            'data': data,
            'health_score': self.calculate_health_score(component_name, data)
        })

        # Keep only recent data (last 30 days)
        cutoff = datetime.now() - timedelta(days=30)
        self.component_data[component_name]['data_history'] = [
            d for d in self.component_data[component_name]['data_history']
            if d['timestamp'] > cutoff
        ]

    def calculate_health_score(self, component_name, data):
        """Calculate health score based on sensor data"""
        # Example: Calculate health based on temperature, vibration, etc.
        temperature = data.get('temperature', 25.0)
        vibration = data.get('vibration', 0.0)

        # Normalize to 0-1 scale (0 = unhealthy, 1 = healthy)
        temp_score = max(0, 1 - abs(temperature - 25.0) / 50.0)  # Assume 25°C is ideal
        vibration_score = max(0, 1 - vibration / 10.0)  # Assume >10 is problematic

        return min(temp_score, vibration_score)

    def predict_maintenance(self, component_name):
        """Predict when maintenance is needed"""
        if component_name not in self.component_data:
            return None

        history = self.component_data[component_name]['data_history']
        if len(history) < 10:  # Need sufficient data
            return None

        # Calculate trend
        recent_scores = [d['health_score'] for d in history[-10:]]
        trend = np.polyfit(range(len(recent_scores)), recent_scores, 1)[0]

        # Predict when health will drop below threshold
        current_health = history[-1]['health_score']
        days_to_failure = int((self.component_data[component_name]['failure_threshold'] - current_health) / trend)

        return {
            'predicted_failure_date': datetime.now() + timedelta(days=days_to_failure),
            'current_health': current_health,
            'trend': trend,
            'maintenance_due': days_to_failure <= 7  # Due within a week
        }

    def generate_maintenance_report(self):
        """Generate comprehensive maintenance report"""
        report = {}

        for component in self.component_data:
            prediction = self.predict_maintenance(component)
            if prediction:
                report[component] = prediction

        return report
```

## Best Practices for Digital Twins

1. **Latency Management**: Minimize delay between real robot and digital twin
2. **Data Fidelity**: Ensure simulation parameters match real-world conditions
3. **Scalability**: Design systems that can handle multiple robots
4. **Security**: Protect communication channels between systems
5. **Validation**: Regularly validate that digital twin reflects reality
6. **Performance**: Optimize both simulation and visualization for real-time operation

## Hands-on Exercise

Create a complete digital twin system that:

1. Sets up a Gazebo simulation of your humanoid robot
2. Creates a Unity visualization that mirrors the Gazebo simulation
3. Implements real-time synchronization between both systems
4. Adds a simple predictive maintenance system
5. Creates a remote monitoring interface

This exercise will help you understand the complete pipeline from simulation to visualization to real-world application.