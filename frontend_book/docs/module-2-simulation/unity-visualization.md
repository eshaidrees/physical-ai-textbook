---
sidebar_position: 3
---

# Unity Visualization

This section covers creating high-quality visualizations for robotic systems using Unity. Unity provides advanced rendering capabilities that complement Gazebo's physics simulation, offering realistic visual representations of robots and environments.

## Introduction to Unity for Robotics

Unity is a powerful game engine that has found significant application in robotics for creating high-fidelity visualizations. While Gazebo excels at physics simulation, Unity provides superior visual rendering, making it ideal for creating compelling visualizations and user interfaces for robotic systems.

## Setting up Unity for Robotics

Unity can be integrated with ROS 2 through several methods:

1. **Unity Robotics Hub**: A collection of tools and packages for robotics simulation
2. **ROS-TCP-Connector**: A Unity package for connecting Unity to ROS networks
3. **Custom TCP/IP interfaces**: For specific use cases

## Basic Unity Robotics Setup

### Installing Unity Robotics Packages

To set up Unity for robotics applications, install the Unity Robotics packages:

1. Open Unity Hub and create a new 3D project
2. In the Package Manager, install:
   - Unity Robotics Hub
   - ROS TCP Connector
   - Unity Simulation (if available)

### Basic ROS Connection Script

Here's a basic script to connect Unity to ROS:

```csharp
using System.Collections;
using System.Collections.Generic;
using UnityEngine;
using Unity.Robotics.ROSTCPConnector;
using RosMessageTypes.Sensor;

public class RobotVisualizer : MonoBehaviour
{
    // ROS Connection
    ROSConnection ros;

    // Robot joint transforms
    public Transform headJoint;
    public Transform leftShoulder;
    public Transform rightShoulder;
    public Transform leftElbow;
    public Transform rightElbow;
    public Transform leftHip;
    public Transform rightHip;
    public Transform leftKnee;
    public Transform rightKnee;

    // Joint states topic
    string jointStatesTopic = "/joint_states";

    // Start is called before the first frame update
    void Start()
    {
        // Get the ROS connection static instance
        ros = ROSConnection.GetOrCreateInstance();
        ros.RegisterPublisher<JointStateMsg>(jointStatesTopic);

        // Subscribe to joint states
        ros.Subscribe<JointStateMsg>(jointStatesTopic, UpdateRobotJoints);
    }

    // Callback function to handle joint state messages
    void UpdateRobotJoints(JointStateMsg jointState)
    {
        // Update each joint based on the received joint states
        for (int i = 0; i < jointState.name.Count; i++)
        {
            string jointName = jointState.name[i];
            float jointPosition = jointState.position[i];

            switch (jointName)
            {
                case "head_joint":
                    if (headJoint != null)
                        headJoint.localRotation = Quaternion.Euler(0, jointPosition * Mathf.Rad2Deg, 0);
                    break;
                case "left_shoulder_joint":
                    if (leftShoulder != null)
                        leftShoulder.localRotation = Quaternion.Euler(0, 0, jointPosition * Mathf.Rad2Deg);
                    break;
                case "right_shoulder_joint":
                    if (rightShoulder != null)
                        rightShoulder.localRotation = Quaternion.Euler(0, 0, jointPosition * Mathf.Rad2Deg);
                    break;
                // Add more joints as needed
            }
        }
    }

    // Update is called once per frame
    void Update()
    {
        // Additional visualization updates can go here
    }
}
```

## Creating a Humanoid Robot Model in Unity

### Basic Humanoid Structure

A humanoid robot in Unity typically consists of:

1. **Root Object**: The main body/torso
2. **Limbs**: Arms and legs with appropriate joints
3. **Sensors**: Cameras, LiDAR, etc. as GameObjects
4. **Materials**: For realistic appearance

### Example Humanoid Robot Hierarchy

```
HumanoidRobot (Root)
├── Torso
│   ├── Head
│   │   └── Camera (for vision)
│   ├── LeftShoulder
│   │   ├── LeftUpperArm
│   │   │   └── LeftLowerArm
│   │   │       └── LeftHand
│   ├── RightShoulder
│   │   ├── RightUpperArm
│   │   │   └── RightLowerArm
│   │   │       └── RightHand
│   ├── LeftHip
│   │   ├── LeftUpperLeg
│   │   │   └── LeftLowerLeg
│   │   │       └── LeftFoot
│   └── RightHip
│       ├── RightUpperLeg
│       │   └── RightLowerLeg
│       │       └── RightFoot
```

### Joint Configuration Script

```csharp
using UnityEngine;

public class HumanoidJointController : MonoBehaviour
{
    [Header("Joint Limits")]
    public float headYawMin = -45f;
    public float headYawMax = 45f;
    public float shoulderMin = -90f;
    public float shoulderMax = 90f;
    public float elbowMin = 0f;
    public float elbowMax = 120f;

    [Header("Joint Transforms")]
    public Transform head;
    public Transform leftShoulder;
    public Transform rightShoulder;
    public Transform leftElbow;
    public Transform rightElbow;

    void Start()
    {
        // Initialize joint positions
    }

    public void SetHeadYaw(float angle)
    {
        if (head != null)
        {
            float clampedAngle = Mathf.Clamp(angle * Mathf.Rad2Deg, headYawMin, headYawMax);
            head.localRotation = Quaternion.Euler(0, clampedAngle, 0);
        }
    }

    public void SetShoulderAngle(float leftAngle, float rightAngle)
    {
        if (leftShoulder != null)
        {
            float clampedLeft = Mathf.Clamp(leftAngle * Mathf.Rad2Deg, shoulderMin, shoulderMax);
            leftShoulder.localEulerAngles = new Vector3(0, 0, clampedLeft);
        }

        if (rightShoulder != null)
        {
            float clampedRight = Mathf.Clamp(rightAngle * Mathf.Rad2Deg, shoulderMin, shoulderMax);
            rightShoulder.localEulerAngles = new Vector3(0, 0, clampedRight);
        }
    }

    public void SetElbowAngle(float leftAngle, float rightAngle)
    {
        if (leftElbow != null)
        {
            float clampedLeft = Mathf.Clamp(leftAngle * Mathf.Rad2Deg, elbowMin, elbowMax);
            leftElbow.localEulerAngles = new Vector3(0, 0, clampedLeft);
        }

        if (rightElbow != null)
        {
            float clampedRight = Mathf.Clamp(rightAngle * Mathf.Rad2Deg, elbowMin, elbowMax);
            rightElbow.localEulerAngles = new Vector3(0, 0, clampedRight);
        }
    }
}
```

## Visualization of Sensor Data

Unity can visualize sensor data from ROS in real-time:

### LiDAR Point Cloud Visualization

```csharp
using System.Collections.Generic;
using UnityEngine;
using Unity.Robotics.ROSTCPConnector;
using RosMessageTypes.Sensor;

public class LidarVisualizer : MonoBehaviour
{
    public GameObject pointPrefab; // Small sphere prefab for points
    private List<GameObject> pointObjects = new List<GameObject>();
    private int maxPoints = 1000; // Limit for performance

    void Start()
    {
        ROSConnection.GetOrCreateInstance().Subscribe<LaserScanMsg>(
            "/scan",
            ReceiveLaserScan
        );
    }

    void ReceiveLaserScan(LaserScanMsg scan)
    {
        // Clear previous points
        foreach (GameObject point in pointObjects)
        {
            DestroyImmediate(point);
        }
        pointObjects.Clear();

        // Create new points based on laser scan
        for (int i = 0; i < scan.ranges.Count; i += 10) // Sample every 10th point for performance
        {
            float range = scan.ranges[i];
            if (range >= scan.range_min && range <= scan.range_max)
            {
                float angle = scan.angle_min + i * scan.angle_increment;

                float x = range * Mathf.Cos(angle);
                float y = range * Mathf.Sin(angle);

                Vector3 pointPos = new Vector3(x, 0.1f, y); // Slightly above ground

                GameObject pointObj = Instantiate(pointPrefab, pointPos, Quaternion.identity);
                pointObjects.Add(pointObj);

                if (pointObjects.Count >= maxPoints)
                    break;
            }
        }
    }
}
```

## Creating a Digital Twin Interface

A digital twin interface combines real-time data with visualization:

```csharp
using UnityEngine;
using UnityEngine.UI;
using Unity.Robotics.ROSTCPConnector;
using RosMessageTypes.Nav;

public class DigitalTwinInterface : MonoBehaviour
{
    [Header("UI Elements")]
    public Text robotStatusText;
    public Text batteryLevelText;
    public Text positionText;
    public Image batteryFill;

    [Header("Robot Visualization")]
    public GameObject robotModel;
    public Transform robotPosition;

    // ROS topics
    private string batteryTopic = "/battery_status";
    private string poseTopic = "/current_pose";

    void Start()
    {
        ROSConnection.GetOrCreateInstance();

        // Subscribe to robot status topics
        ROSConnection.GetOrCreateInstance().Subscribe<BatteryStateMsg>(
            batteryTopic,
            UpdateBatteryStatus
        );

        ROSConnection.GetOrCreateInstance().Subscribe<OdometryMsg>(
            poseTopic,
            UpdateRobotPosition
        );
    }

    void UpdateBatteryStatus(BatteryStateMsg battery)
    {
        if (batteryLevelText != null)
        {
            batteryLevelText.text = $"Battery: {(int)(battery.percentage * 100)}%";
        }

        if (batteryFill != null)
        {
            batteryFill.fillAmount = battery.percentage;
        }
    }

    void UpdateRobotPosition(OdometryMsg pose)
    {
        Vector3 position = new Vector3(
            (float)pose.pose.pose.position.x,
            (float)pose.pose.pose.position.y,
            (float)pose.pose.pose.position.z
        );

        if (robotPosition != null)
        {
            robotPosition.position = position;
        }

        if (positionText != null)
        {
            positionText.text = $"Position: {position.x:F2}, {position.y:F2}, {position.z:F2}";
        }
    }

    void UpdateRobotStatus(string status)
    {
        if (robotStatusText != null)
        {
            robotStatusText.text = $"Status: {status}";
        }
    }
}
```

## Best Practices for Unity Visualization

1. **Performance Optimization**: Use object pooling for frequently instantiated objects
2. **LOD Systems**: Implement Level of Detail for complex models at distance
3. **Occlusion Culling**: Hide objects not visible to the camera
4. **Lighting**: Use baked lighting for static environments
5. **Materials**: Optimize shaders for real-time performance
6. **Physics**: Use simplified collision meshes separate from visual meshes

## Unity-Gazebo Synchronization

For complete digital twin functionality, you can synchronize Unity with Gazebo:

1. **Shared Coordinate Systems**: Ensure both systems use the same coordinate conventions
2. **Real-time Data Streaming**: Stream sensor data and robot states from Gazebo to Unity
3. **Synchronized Clocks**: Maintain synchronized time between both systems
4. **Feedback Loop**: Optionally send Unity user interactions back to Gazebo

## Hands-on Exercise

Create a Unity scene that:

1. Connects to a ROS network
2. Visualizes a simple humanoid robot model
3. Updates the robot's joint positions based on ROS joint state messages
4. Displays sensor data (LiDAR points or camera feed)
5. Shows robot status information in a UI overlay

This exercise will help you understand how to create high-quality visualizations that complement physics-based simulation.