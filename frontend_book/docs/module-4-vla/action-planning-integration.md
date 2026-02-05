---
sidebar_position: 5
---

# Action Planning Integration

This section covers integrating vision-language understanding with robotic action planning, creating systems that can translate natural language commands into executable robotic behaviors. You'll learn to bridge the gap between high-level language commands and low-level robot control.

## Understanding Action Planning Integration

Action planning integration involves connecting natural language understanding with robotic execution systems. This requires:

- Mapping language concepts to robotic actions
- Creating executable plans from high-level commands
- Handling spatial and temporal reasoning
- Ensuring safe and feasible execution
- Providing feedback and monitoring

### Key Components

1. **Command Parser**: Interprets natural language commands
2. **Action Planner**: Creates executable sequences of actions
3. **Executor**: Carries out planned actions
4. **Monitor**: Tracks execution and handles failures
5. **Feedback System**: Reports results and handles corrections

## Implementing Language-to-Action Mapping

### Command Interpretation and Planning

```python
import rclpy
from rclpy.node import Node
from std_msgs.msg import String
from geometry_msgs.msg import Pose, Point
from sensor_msgs.msg import JointState
import json
import time

class LanguageActionMapper:
    def __init__(self):
        # Define action templates
        self.action_templates = {
            'navigation': {
                'keywords': ['go to', 'move to', 'navigate to', 'reach'],
                'required_params': ['target_location'],
                'action_sequence': ['plan_path', 'execute_navigation', 'verify_arrival']
            },
            'manipulation': {
                'keywords': ['pick up', 'grasp', 'take', 'grab', 'place', 'put'],
                'required_params': ['target_object', 'action_type'],
                'action_sequence': ['locate_object', 'plan_grasp', 'execute_grasp', 'verify_success']
            },
            'interaction': {
                'keywords': ['greet', 'wave', 'dance', 'turn', 'look'],
                'required_params': ['action_type'],
                'action_sequence': ['execute_behavior', 'verify_completion']
            }
        }

        # Define location mappings
        self.location_map = {
            'kitchen': {'x': 1.0, 'y': 2.0, 'theta': 0.0},
            'living room': {'x': -1.0, 'y': 1.0, 'theta': 1.57},
            'bedroom': {'x': 0.0, 'y': -2.0, 'theta': 3.14},
            'office': {'x': 2.0, 'y': 0.0, 'theta': -1.57}
        }

        # Define object mappings
        self.object_map = {
            'cup': 'cup_object',
            'bottle': 'bottle_object',
            'book': 'book_object',
            'remote': 'remote_object'
        }

    def parse_command(self, command_text):
        """
        Parse natural language command into structured action
        """
        command_lower = command_text.lower()

        # Identify action type
        action_type = None
        for action, data in self.action_templates.items():
            for keyword in data['keywords']:
                if keyword in command_lower:
                    action_type = action
                    break
            if action_type:
                break

        if not action_type:
            return None, "Unknown action type"

        # Extract parameters based on action type
        params = {}

        if action_type == 'navigation':
            # Extract target location
            for location in self.location_map.keys():
                if location in command_lower:
                    params['target_location'] = location
                    break
            if 'target_location' not in params:
                return None, "No target location specified"

        elif action_type == 'manipulation':
            # Extract target object and action type
            for obj in self.object_map.keys():
                if obj in command_lower:
                    params['target_object'] = obj
                    break

            if 'pick' in command_lower or 'grasp' in command_lower or 'take' in command_lower:
                params['action_type'] = 'pick'
            elif 'place' in command_lower or 'put' in command_lower:
                params['action_type'] = 'place'
            else:
                params['action_type'] = 'manipulate'

        elif action_type == 'interaction':
            params['action_type'] = command_lower.split()[0]  # First word is usually the action

        # Validate required parameters
        required = self.action_templates[action_type]['required_params']
        for param in required:
            if param not in params:
                return None, f"Missing required parameter: {param}"

        # Create structured action
        structured_action = {
            'action_type': action_type,
            'parameters': params,
            'sequence': self.action_templates[action_type]['action_sequence'],
            'timestamp': time.time()
        }

        return structured_action, "Success"

    def plan_action(self, structured_action):
        """
        Plan the sequence of actions needed to execute the command
        """
        action_type = structured_action['action_type']
        params = structured_action['parameters']

        plan = []

        if action_type == 'navigation':
            # Plan navigation to target location
            target_location = self.location_map[params['target_location']]
            plan.append({
                'action': 'navigate_to_pose',
                'parameters': {
                    'x': target_location['x'],
                    'y': target_location['y'],
                    'theta': target_location['theta']
                }
            })

        elif action_type == 'manipulation':
            # Plan manipulation sequence
            plan.extend([
                {
                    'action': 'locate_object',
                    'parameters': {'object_name': params['target_object']}
                },
                {
                    'action': 'plan_manipulation',
                    'parameters': {
                        'object_name': params['target_object'],
                        'action_type': params['action_type']
                    }
                },
                {
                    'action': 'execute_manipulation',
                    'parameters': {
                        'object_name': params['target_object'],
                        'action_type': params['action_type']
                    }
                }
            ])

        elif action_type == 'interaction':
            plan.append({
                'action': 'execute_behavior',
                'parameters': {'behavior_name': params['action_type']}
            })

        return plan

# ROS 2 Action Planning Node
class ActionPlanningNode(Node):
    def __init__(self):
        super().__init__('action_planning_node')

        # Initialize action mapper
        self.action_mapper = LanguageActionMapper()

        # Publishers and subscribers
        self.command_sub = self.create_subscription(
            String, '/natural_language/structured_command', self.command_callback, 10)
        self.action_pub = self.create_publisher(String, '/robot/action_plan', 10)
        self.feedback_pub = self.create_publisher(String, '/action_planning/feedback', 10)

        self.get_logger().info('Action Planning Node initialized')

    def command_callback(self, msg):
        """
        Handle incoming structured commands
        """
        try:
            command_data = json.loads(msg.data)
            command_text = command_data.get('raw_command', '')

            self.get_logger().info(f'Received command: {command_text}')

            # Parse command
            structured_action, status = self.action_mapper.parse_command(command_text)

            if structured_action is None:
                feedback_msg = String()
                feedback_msg.data = f"Command parsing failed: {status}"
                self.feedback_pub.publish(feedback_msg)
                return

            # Plan action sequence
            action_plan = self.action_mapper.plan_action(structured_action)

            # Publish action plan
            plan_msg = String()
            plan_msg.data = json.dumps({
                'plan': action_plan,
                'original_command': command_text,
                'timestamp': time.time()
            })
            self.action_pub.publish(plan_msg)

            self.get_logger().info(f'Published action plan with {len(action_plan)} steps')

        except json.JSONDecodeError:
            self.get_logger().error('Invalid JSON in command message')
        except Exception as e:
            self.get_logger().error(f'Error processing command: {e}')

def main(args=None):
    rclpy.init(args=args)
    node = ActionPlanningNode()

    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        node.get_logger().info('Shutting down action planning node')
    finally:
        node.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()
```

## Spatial and Temporal Reasoning

### Understanding Spatial Relationships

```python
class SpatialReasoner:
    def __init__(self):
        # Define spatial relationships
        self.spatial_relations = {
            'on': ['above', 'supported_by'],
            'in': ['inside', 'contained_by'],
            'next_to': ['adjacent', 'beside'],
            'above': ['over', 'higher_than'],
            'below': ['under', 'lower_than']
        }

    def parse_spatial_command(self, command_text):
        """
        Parse spatial relationships from command text
        """
        for relation, synonyms in self.spatial_relations.items():
            if relation in command_text.lower():
                # Extract target object and reference object
                parts = command_text.lower().split(relation)
                if len(parts) >= 2:
                    target = parts[0].strip().split()[-1]  # Last word before relation
                    reference = parts[1].strip().split()[0]  # First word after relation
                    return {
                        'target': target,
                        'relation': relation,
                        'reference': reference
                    }

        return None

    def plan_spatial_action(self, spatial_command):
        """
        Plan action based on spatial relationships
        """
        target = spatial_command['target']
        relation = spatial_command['relation']
        reference = spatial_command['reference']

        # Plan different actions based on spatial relation
        if relation in ['on', 'above']:
            # Plan to place target on reference
            return self.plan_placement(target, reference, 'on')
        elif relation == 'in':
            # Plan to place target inside reference
            return self.plan_placement(target, reference, 'in')
        elif relation in ['next_to', 'beside']:
            # Plan to place target next to reference
            return self.plan_placement(target, reference, 'next_to')
        else:
            return self.plan_simple_placement(target, reference)

    def plan_placement(self, target, reference, relation):
        """
        Plan placement action
        """
        plan = [
            {
                'action': 'locate_object',
                'parameters': {'object_name': reference}
            },
            {
                'action': 'calculate_placement_pose',
                'parameters': {
                    'target': target,
                    'reference': reference,
                    'relation': relation
                }
            },
            {
                'action': 'navigate_to_approach_pose',
                'parameters': {
                    'pose': self.calculate_approach_pose(reference, relation)
                }
            },
            {
                'action': 'execute_placement',
                'parameters': {
                    'target': target,
                    'reference': reference,
                    'relation': relation
                }
            }
        ]
        return plan

    def calculate_approach_pose(self, reference_object, relation):
        """
        Calculate approach pose based on spatial relation
        """
        # This would interface with the robot's perception system
        # to get the pose of the reference object
        return {
            'x': 0.5,  # Example coordinates
            'y': 0.0,
            'theta': 0.0
        }
```

## Integration with Execution Systems

### Plan Execution Interface

```python
class PlanExecutorInterface:
    def __init__(self, action_planning_node):
        self.planning_node = action_planning_node
        self.current_plan = None
        self.current_step = 0
        self.execution_active = False

    def execute_plan(self, plan):
        """
        Execute the given action plan
        """
        self.current_plan = plan
        self.current_step = 0
        self.execution_active = True

        # Execute each step in the plan
        for i, step in enumerate(plan):
            if not self.execution_active:
                break

            self.current_step = i
            success = self.execute_step(step)

            if not success:
                self.get_logger().error(f'Step {i} failed: {step["action"]}')
                return False

        return True

    def execute_step(self, step):
        """
        Execute a single step of the plan
        """
        action = step['action']
        parameters = step.get('parameters', {})

        # Route to appropriate execution function
        if action == 'navigate_to_pose':
            return self.execute_navigation_step(parameters)
        elif action == 'locate_object':
            return self.execute_perception_step(parameters)
        elif action == 'execute_manipulation':
            return self.execute_manipulation_step(parameters)
        elif action == 'execute_behavior':
            return self.execute_behavior_step(parameters)
        else:
            self.get_logger().error(f'Unknown action: {action}')
            return False

    def execute_navigation_step(self, parameters):
        """
        Execute navigation step
        """
        # This would interface with the navigation system
        x = parameters.get('x', 0.0)
        y = parameters.get('y', 0.0)
        theta = parameters.get('theta', 0.0)

        # Send navigation command
        # In a real system, this would call navigation action server
        time.sleep(1)  # Simulate navigation time
        return True

    def execute_perception_step(self, parameters):
        """
        Execute perception step
        """
        object_name = parameters.get('object_name', 'unknown')

        # This would interface with the perception system
        # In a real system, this would call object detection services
        time.sleep(0.5)  # Simulate perception time
        return True

    def execute_manipulation_step(self, parameters):
        """
        Execute manipulation step
        """
        object_name = parameters.get('object_name', 'unknown')
        action_type = parameters.get('action_type', 'grasp')

        # This would interface with the manipulation system
        # In a real system, this would call manipulation action server
        time.sleep(1.5)  # Simulate manipulation time
        return True

    def execute_behavior_step(self, parameters):
        """
        Execute behavior step
        """
        behavior_name = parameters.get('behavior_name', 'idle')

        # This would interface with the behavior system
        time.sleep(1)  # Simulate behavior execution time
        return True

    def get_logger(self):
        """
        Simple logger for the executor
        """
        class Logger:
            def info(self, msg):
                print(f"INFO: {msg}")
            def error(self, msg):
                print(f"ERROR: {msg}")
        return Logger()

    def cancel_execution(self):
        """
        Cancel current plan execution
        """
        self.execution_active = False
```

## Safety and Validation

### Plan Validation and Safety Checks

```python
class SafeActionPlanner:
    def __init__(self):
        self.safety_constraints = {
            'workspace_limits': {
                'x_min': -5.0, 'x_max': 5.0,
                'y_min': -5.0, 'y_max': 5.0,
                'z_min': 0.0, 'z_max': 2.0
            },
            'joint_limits': {
                'position': [-3.14, 3.14],  # Example joint limits
                'velocity': [-5.0, 5.0],
                'effort': [-100.0, 100.0]
            },
            'collision_checking': True,
            'force_limits': {'manipulation': 50.0}  # Newtons
        }

    def validate_plan(self, action_plan):
        """
        Validate the action plan for safety
        """
        issues = []

        for step in action_plan:
            action = step.get('action', '')
            params = step.get('parameters', {})

            # Check navigation targets are within workspace
            if action == 'navigate_to_pose':
                x = params.get('x', 0.0)
                y = params.get('y', 0.0)

                limits = self.safety_constraints['workspace_limits']
                if (x < limits['x_min'] or x > limits['x_max'] or
                    y < limits['y_min'] or y > limits['y_max']):
                    issues.append(f"Navigation target ({x}, {y}) outside workspace limits")

            # Check manipulation forces
            elif action == 'execute_manipulation':
                # Check if manipulation action is safe
                pass

        return len(issues) == 0, issues

    def validate_command(self, command_text):
        """
        Validate natural language command for safety
        """
        # Check for dangerous commands
        dangerous_keywords = [
            'harm', 'hurt', 'damage', 'break', 'destroy',
            'fast', 'quickly'  # In certain contexts
        ]

        command_lower = command_text.lower()
        for keyword in dangerous_keywords:
            if keyword in command_lower:
                return False, f"Dangerous keyword detected: {keyword}"

        return True, "Command is safe"

    def safe_parse_command(self, command_text):
        """
        Parse command with safety validation
        """
        # Validate command for safety
        is_safe, safety_msg = self.validate_command(command_text)
        if not is_safe:
            return None, f"Unsafe command: {safety_msg}"

        # Parse the command using the regular parser
        mapper = LanguageActionMapper()
        return mapper.parse_command(command_text)
```

## Real-time Adaptation

### Adaptive Planning System

```python
class AdaptivePlanningSystem:
    def __init__(self):
        self.original_plan = None
        self.current_step = 0
        self.execution_context = {}
        self.adaptation_rules = self._define_adaptation_rules()

    def _define_adaptation_rules(self):
        """
        Define rules for plan adaptation
        """
        return [
            {
                'condition': 'object_not_found',
                'action': 'search_alternative_object',
                'params': {'search_radius': 1.0}
            },
            {
                'condition': 'navigation_failed',
                'action': 'reroute_navigation',
                'params': {'max_attempts': 3}
            },
            {
                'condition': 'manipulation_failed',
                'action': 'retry_with_different_approach',
                'params': {'max_attempts': 2}
            }
        ]

    def execute_with_adaptation(self, action_plan):
        """
        Execute plan with real-time adaptation capabilities
        """
        self.original_plan = action_plan
        self.current_step = 0

        for i, step in enumerate(action_plan):
            self.current_step = i

            # Execute the step
            success = self.execute_step_with_monitoring(step)

            if not success:
                # Try to adapt the plan
                adapted_plan = self.adapt_plan(i, f"step_{i}_failed")

                if adapted_plan:
                    # Continue with adapted plan
                    remaining_steps = adapted_plan[i:]
                    for j, adapted_step in enumerate(remaining_steps):
                        if not self.execute_step_with_monitoring(adapted_step):
                            return False
                    return True
                else:
                    return False

        return True

    def execute_step_with_monitoring(self, step):
        """
        Execute a step with monitoring for failures
        """
        try:
            # This would interface with the actual execution system
            # For simulation, we'll just return True
            time.sleep(0.1)  # Simulate execution time
            return True
        except Exception as e:
            print(f"Step execution failed: {e}")
            return False

    def adapt_plan(self, failed_step_idx, failure_type):
        """
        Adapt the plan based on failure
        """
        for rule in self.adaptation_rules:
            if rule['condition'] == failure_type:
                # Apply adaptation rule
                return self._apply_adaptation_rule(rule, failed_step_idx)

        # If no specific rule applies, try general recovery
        return self._general_plan_recovery(failed_step_idx)

    def _apply_adaptation_rule(self, rule, failed_step_idx):
        """
        Apply a specific adaptation rule
        """
        action = rule['action']
        params = rule['params']

        if action == 'search_alternative_object':
            # Modify the plan to search for alternative objects
            new_plan = self.original_plan.copy()
            # Add search step before the failed step
            search_step = {
                'action': 'search_for_object',
                'parameters': params
            }
            new_plan.insert(failed_step_idx, search_step)
            return new_plan

        elif action == 'reroute_navigation':
            # Modify navigation plan
            new_plan = self.original_plan.copy()
            # This would involve replanning the navigation
            return new_plan

        return None

    def _general_plan_recovery(self, failed_step_idx):
        """
        General recovery when specific adaptation rules don't apply
        """
        # Try to skip the failed step if possible
        if failed_step_idx < len(self.original_plan) - 1:
            # Return plan starting from next step
            return self.original_plan[failed_step_idx + 1:]

        return None
```

## Integration Example

### Complete Integration Example

```python
class IntegratedActionPlanningSystem:
    def __init__(self):
        # Initialize all components
        self.language_mapper = LanguageActionMapper()
        self.spatial_reasoner = SpatialReasoner()
        self.plan_executor = PlanExecutorInterface(None)
        self.safety_validator = SafeActionPlanner()
        self.adaptive_system = AdaptivePlanningSystem()

    def process_natural_command(self, command_text):
        """
        Process a natural language command through the complete pipeline
        """
        # 1. Validate command for safety
        is_safe, safety_msg = self.safety_validator.validate_command(command_text)
        if not is_safe:
            return {'success': False, 'error': f'Safety validation failed: {safety_msg}'}

        # 2. Parse the command
        structured_action, parse_status = self.language_mapper.parse_command(command_text)
        if structured_action is None:
            return {'success': False, 'error': f'Command parsing failed: {parse_status}'}

        # 3. Plan the action sequence
        action_plan = self.language_mapper.plan_action(structured_action)

        # 4. Validate the plan for safety
        is_safe_plan, safety_issues = self.safety_validator.validate_plan(action_plan)
        if not is_safe_plan:
            return {'success': False, 'error': f'Plan safety validation failed: {safety_issues}'}

        # 5. Execute the plan with adaptation capabilities
        success = self.adaptive_system.execute_with_adaptation(action_plan)

        return {
            'success': success,
            'plan': action_plan,
            'original_command': command_text
        }

# Example usage
def main():
    system = IntegratedActionPlanningSystem()

    # Example commands
    commands = [
        "go to the kitchen",
        "pick up the red cup",
        "place the cup on the table"
    ]

    for command in commands:
        print(f"\nProcessing command: '{command}'")
        result = system.process_natural_command(command)
        print(f"Result: {result}")

if __name__ == "__main__":
    main()
```

## Hands-on Exercise

Create an integrated action planning system that:
1. Parses natural language commands into structured actions
2. Incorporates spatial reasoning for complex commands
3. Validates plans for safety before execution
4. Adapts plans in real-time when failures occur
5. Integrates with your robot's execution system

This exercise will help you build a complete system that can translate human commands into reliable robotic actions.