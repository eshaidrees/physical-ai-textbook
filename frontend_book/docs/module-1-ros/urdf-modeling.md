---
sidebar_position: 4
---

# URDF Humanoid Modeling

This section covers creating Unified Robot Description Format (URDF) models for humanoid robots. URDF is XML-based format that describes robot models including kinematic structure, visual and collision properties, and physical properties.

## Introduction to URDF

URDF (Unified Robot Description Format) is an XML format used in ROS to describe robot models. It defines the robot's physical structure, including:

- Links (rigid bodies)
- Joints (connections between links)
- Visual and collision properties
- Inertial properties

## Basic URDF Structure

A basic URDF file follows this structure:

```xml
<?xml version="1.0"?>
<robot name="humanoid_robot">
  <!-- Define links -->
  <link name="base_link">
    <visual>
      <geometry>
        <box size="0.5 0.2 0.2"/>
      </geometry>
      <material name="blue">
        <color rgba="0 0 1 1"/>
      </material>
    </visual>
    <collision>
      <geometry>
        <box size="0.5 0.2 0.2"/>
      </geometry>
    </collision>
    <inertial>
      <mass value="1"/>
      <inertia ixx="0.01" ixy="0" ixz="0" iyy="0.01" iyz="0" izz="0.01"/>
    </inertial>
  </link>

  <!-- Additional links and joints would go here -->
</robot>
```

## Link Properties

Links represent rigid bodies in the robot. Each link has several components:

### Visual Properties
- `geometry`: Shape of the link for visualization
  - `<box size="x y z"/>`
  - `<cylinder radius="r" length="l"/>`
  - `<sphere radius="r"/>`
  - `<mesh filename="path/to/mesh.dae"/>`
- `material`: Color and texture properties

### Collision Properties
- Similar to visual but defines collision boundaries
- Often simpler geometry for performance

### Inertial Properties
- Mass and inertia tensor
- Used for physics simulation

## Joint Properties

Joints connect links together and define how they can move relative to each other:

```xml
<joint name="joint_name" type="joint_type">
  <parent link="parent_link_name"/>
  <child link="child_link_name"/>
  <origin xyz="x y z" rpy="roll pitch yaw"/>
  <axis xyz="x y z"/>
  <limit lower="min" upper="max" effort="effort" velocity="vel"/>
</joint>
```

Joint types include:
- `revolute`: Rotational joint with limits
- `continuous`: Rotational joint without limits
- `prismatic`: Linear sliding joint
- `fixed`: No movement (rigid connection)
- `floating`: 6DOF with no constraints
- `planar`: Movement on a plane

## Complete Humanoid Robot Example

Here's a simplified humanoid robot URDF:

```xml
<?xml version="1.0"?>
<robot name="simple_humanoid">

  <!-- Base link -->
  <link name="base_link">
    <visual>
      <geometry>
        <box size="0.3 0.3 0.3"/>
      </geometry>
      <material name="gray">
        <color rgba="0.5 0.5 0.5 1"/>
      </material>
    </visual>
    <collision>
      <geometry>
        <box size="0.3 0.3 0.3"/>
      </geometry>
    </collision>
    <inertial>
      <mass value="5"/>
      <inertia ixx="0.1" ixy="0" ixz="0" iyy="0.1" iyz="0" izz="0.1"/>
    </inertial>
  </link>

  <!-- Torso -->
  <link name="torso">
    <visual>
      <geometry>
        <box size="0.25 0.2 0.5"/>
      </geometry>
      <material name="red">
        <color rgba="1 0 0 1"/>
      </material>
    </visual>
    <collision>
      <geometry>
        <box size="0.25 0.2 0.5"/>
      </geometry>
    </collision>
    <inertial>
      <mass value="3"/>
      <inertia ixx="0.05" ixy="0" ixz="0" iyy="0.05" iyz="0" izz="0.05"/>
    </inertial>
  </link>

  <joint name="base_to_torso" type="fixed">
    <parent link="base_link"/>
    <child link="torso"/>
    <origin xyz="0 0 0.4"/>
  </joint>

  <!-- Head -->
  <link name="head">
    <visual>
      <geometry>
        <sphere radius="0.1"/>
      </geometry>
      <material name="white">
        <color rgba="1 1 1 1"/>
      </material>
    </visual>
    <collision>
      <geometry>
        <sphere radius="0.1"/>
      </geometry>
    </collision>
    <inertial>
      <mass value="1"/>
      <inertia ixx="0.004" ixy="0" ixz="0" iyy="0.004" iyz="0" izz="0.004"/>
    </inertial>
  </link>

  <joint name="torso_to_head" type="revolute">
    <parent link="torso"/>
    <child link="head"/>
    <origin xyz="0 0 0.3"/>
    <axis xyz="0 0 1"/>
    <limit lower="-1.57" upper="1.57" effort="10" velocity="1"/>
  </joint>

  <!-- Left Arm -->
  <link name="left_upper_arm">
    <visual>
      <geometry>
        <cylinder radius="0.05" length="0.3"/>
      </geometry>
      <material name="blue">
        <color rgba="0 0 1 1"/>
      </material>
    </visual>
    <collision>
      <geometry>
        <cylinder radius="0.05" length="0.3"/>
      </geometry>
    </collision>
    <inertial>
      <mass value="0.8"/>
      <inertia ixx="0.01" ixy="0" ixz="0" iyy="0.01" iyz="0" izz="0.001"/>
    </inertial>
  </link>

  <joint name="torso_to_left_shoulder" type="revolute">
    <parent link="torso"/>
    <child link="left_upper_arm"/>
    <origin xyz="0.15 0 0.1" rpy="0 0 0"/>
    <axis xyz="0 1 0"/>
    <limit lower="-1.57" upper="1.57" effort="10" velocity="1"/>
  </joint>

  <link name="left_lower_arm">
    <visual>
      <geometry>
        <cylinder radius="0.04" length="0.25"/>
      </geometry>
      <material name="blue">
        <color rgba="0 0 1 1"/>
      </material>
    </visual>
    <collision>
      <geometry>
        <cylinder radius="0.04" length="0.25"/>
      </geometry>
    </collision>
    <inertial>
      <mass value="0.5"/>
      <inertia ixx="0.005" ixy="0" ixz="0" iyy="0.005" iyz="0" izz="0.0005"/>
    </inertial>
  </link>

  <joint name="left_elbow" type="revolute">
    <parent link="left_upper_arm"/>
    <child link="left_lower_arm"/>
    <origin xyz="0 0 -0.25" rpy="0 0 0"/>
    <axis xyz="0 1 0"/>
    <limit lower="0" upper="1.57" effort="10" velocity="1"/>
  </joint>

  <!-- Right Arm (similar structure to left arm) -->
  <link name="right_upper_arm">
    <visual>
      <geometry>
        <cylinder radius="0.05" length="0.3"/>
      </geometry>
      <material name="blue">
        <color rgba="0 0 1 1"/>
      </material>
    </visual>
    <collision>
      <geometry>
        <cylinder radius="0.05" length="0.3"/>
      </geometry>
    </collision>
    <inertial>
      <mass value="0.8"/>
      <inertia ixx="0.01" ixy="0" ixz="0" iyy="0.01" iyz="0" izz="0.001"/>
    </inertial>
  </link>

  <joint name="torso_to_right_shoulder" type="revolute">
    <parent link="torso"/>
    <child link="right_upper_arm"/>
    <origin xyz="-0.15 0 0.1" rpy="0 0 0"/>
    <axis xyz="0 1 0"/>
    <limit lower="-1.57" upper="1.57" effort="10" velocity="1"/>
  </joint>

  <link name="right_lower_arm">
    <visual>
      <geometry>
        <cylinder radius="0.04" length="0.25"/>
      </geometry>
      <material name="blue">
        <color rgba="0 0 1 1"/>
      </material>
    </visual>
    <collision>
      <geometry>
        <cylinder radius="0.04" length="0.25"/>
      </geometry>
    </collision>
    <inertial>
      <mass value="0.5"/>
      <inertia ixx="0.005" ixy="0" ixz="0" iyy="0.005" iyz="0" izz="0.0005"/>
    </inertial>
  </link>

  <joint name="right_elbow" type="revolute">
    <parent link="right_upper_arm"/>
    <child link="right_lower_arm"/>
    <origin xyz="0 0 -0.25" rpy="0 0 0"/>
    <axis xyz="0 1 0"/>
    <limit lower="0" upper="1.57" effort="10" velocity="1"/>
  </joint>

</robot>
```

## Xacro for Complex Models

For complex humanoid models, it's common to use Xacro (XML Macros), which allows for:
- Parameterization
- Reusable macros
- Cleaner, more maintainable code

```xml
<?xml version="1.0"?>
<robot xmlns:xacro="http://www.ros.org/wiki/xacro" name="humanoid_with_xacro">

  <!-- Define properties -->
  <xacro:property name="M_PI" value="3.1415926535897931" />
  <xacro:property name="base_size" value="0.3 0.3 0.3" />

  <!-- Macro for creating arm links -->
  <xacro:macro name="arm_link" params="name parent xyz rpy joint_axis joint_limit_lower joint_limit_upper">
    <link name="${name}_upper_arm">
      <visual>
        <geometry>
          <cylinder radius="0.05" length="0.3"/>
        </geometry>
        <material name="blue">
          <color rgba="0 0 1 1"/>
        </material>
      </visual>
      <collision>
        <geometry>
          <cylinder radius="0.05" length="0.3"/>
        </geometry>
      </collision>
      <inertial>
        <mass value="0.8"/>
        <inertia ixx="0.01" ixy="0" ixz="0" iyy="0.01" iyz="0" izz="0.001"/>
      </inertial>
    </link>

    <joint name="${parent}_to_${name}_shoulder" type="revolute">
      <parent link="${parent}"/>
      <child link="${name}_upper_arm"/>
      <origin xyz="${xyz}" rpy="${rpy}"/>
      <axis xyz="${joint_axis}"/>
      <limit lower="${joint_limit_lower}" upper="${joint_limit_upper}" effort="10" velocity="1"/>
    </joint>
  </xacro:macro>

  <!-- Create base link -->
  <link name="base_link">
    <visual>
      <geometry>
        <box size="${base_size}"/>
      </geometry>
      <material name="gray">
        <color rgba="0.5 0.5 0.5 1"/>
      </material>
    </visual>
    <collision>
      <geometry>
        <box size="${base_size}"/>
      </geometry>
    </collision>
    <inertial>
      <mass value="5"/>
      <inertia ixx="0.1" ixy="0" ixz="0" iyy="0.1" iyz="0" izz="0.1"/>
    </inertial>
  </link>

  <!-- Use the macro to create arms -->
  <xacro:arm_link name="left" parent="base_link"
                   xyz="0.15 0 0" rpy="0 0 0"
                   joint_axis="0 1 0"
                   joint_limit_lower="-1.57" joint_limit_upper="1.57"/>

  <xacro:arm_link name="right" parent="base_link"
                   xyz="-0.15 0 0" rpy="0 0 0"
                   joint_axis="0 1 0"
                   joint_limit_lower="-1.57" joint_limit_upper="1.57"/>

</robot>
```

## Validating URDF Models

Before using a URDF model in simulation, validate it:

```bash
# Check if URDF is valid
check_urdf path/to/your/model.urdf

# Convert Xacro to URDF
ros2 run xacro xacro path/to/your/model.xacro > output.urdf

# Visualize in RViz
ros2 run rviz2 rviz2
# In RViz, add RobotModel display and set the URDF file
```

## Best Practices

1. **Start Simple**: Begin with a basic model and add complexity gradually
2. **Use Consistent Units**: Stick to meters for distances, radians for angles
3. **Validate Inertias**: Make sure inertia values are reasonable
4. **Collision vs Visual**: Use simpler shapes for collision to improve performance
5. **Origin Conventions**: Use consistent coordinate frame conventions
6. **Naming Consistency**: Use descriptive, consistent names for links and joints

## Hands-on Exercise

Create a URDF model for a simple humanoid robot with:
- A base/torso link
- Head with neck joint
- Two arms with shoulder and elbow joints
- Two legs with hip, knee, and ankle joints

Test your model using `check_urdf` and visualize it in RViz. Then create a simple launch file to spawn your robot in Gazebo simulation.