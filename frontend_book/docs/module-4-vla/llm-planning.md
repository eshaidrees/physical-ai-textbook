---
sidebar_position: 3
---

# LLM-Based Planning for Robotics

This section covers implementing Large Language Model (LLM)-based planning for robotics applications. You'll learn to use LLMs for high-level task planning, reasoning, and decision-making in robotic systems.

## Understanding LLM-Based Planning

Large Language Models have revolutionized AI planning by enabling:
- Natural language task specification
- Commonsense reasoning
- Multi-step planning with contextual awareness
- Adaptation to novel situations
- Integration of diverse knowledge sources

### Key Capabilities

1. **Task Decomposition**: Breaking complex tasks into manageable steps
2. **Contextual Reasoning**: Understanding situational context
3. **Knowledge Integration**: Using world knowledge for planning
4. **Adaptive Planning**: Adjusting plans based on feedback
5. **Natural Language Interface**: Planning from human instructions

## Implementing LLM Planning Systems

### Basic LLM Integration

```python
import openai
import json
import time
from typing import Dict, List, Any, Optional
import asyncio

class LLMPlanner:
    def __init__(self, api_key: str = None, model: str = "gpt-3.5-turbo"):
        """
        Initialize LLM-based planner
        """
        if api_key:
            openai.api_key = api_key
        self.model = model
        self.max_retries = 3
        self.retry_delay = 1.0

    def plan_task(self, task_description: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Generate a plan for a given task description
        """
        if context is None:
            context = {}

        # Construct the prompt for the LLM
        prompt = self._construct_planning_prompt(task_description, context)

        for attempt in range(self.max_retries):
            try:
                response = openai.ChatCompletion.create(
                    model=self.model,
                    messages=[
                        {"role": "system", "content": self._get_system_prompt()},
                        {"role": "user", "content": prompt}
                    ],
                    temperature=0.3,  # Lower temperature for more consistent planning
                    max_tokens=1000
                )

                plan_text = response.choices[0].message.content.strip()

                # Parse the plan
                plan = self._parse_plan(plan_text)
                return plan

            except Exception as e:
                print(f"Attempt {attempt + 1} failed: {e}")
                if attempt < self.max_retries - 1:
                    time.sleep(self.retry_delay * (2 ** attempt))  # Exponential backoff
                else:
                    raise e

    def _construct_planning_prompt(self, task_description: str, context: Dict[str, Any]) -> str:
        """
        Construct the planning prompt for the LLM
        """
        prompt = f"""
        Task: {task_description}

        Context: {json.dumps(context, indent=2)}

        Please create a detailed step-by-step plan to accomplish this task. The plan should be in JSON format with the following structure:
        {{
            "task": "brief description of the task",
            "steps": [
                {{
                    "step_number": 1,
                    "action": "action to perform",
                    "description": "detailed description of the action",
                    "parameters": {{"param1": "value1", "param2": "value2"}},
                    "preconditions": ["list of preconditions"],
                    "expected_outcomes": ["list of expected outcomes"]
                }}
            ],
            "estimated_duration": "estimated time in seconds",
            "safety_considerations": ["list of safety considerations"]
        }}

        Make sure the plan is executable by a robot system and includes appropriate error handling considerations.
        """

        return prompt

    def _get_system_prompt(self) -> str:
        """
        Get the system prompt for the LLM
        """
        return """
        You are an expert robotic task planner. Generate detailed, executable plans for robot systems.
        Consider safety, feasibility, and the physical constraints of robotic systems.
        """

    def _parse_plan(self, plan_text: str) -> Dict[str, Any]:
        """
        Parse the LLM response into a structured plan
        """
        try:
            # Try to extract JSON from the response
            start_idx = plan_text.find('{')
            end_idx = plan_text.rfind('}') + 1

            if start_idx != -1 and end_idx != 0:
                json_str = plan_text[start_idx:end_idx]
                plan = json.loads(json_str)
                return plan
            else:
                raise ValueError("No valid JSON found in response")
        except json.JSONDecodeError:
            # If JSON parsing fails, try to extract key information differently
            return {
                "task": "Parsed from text",
                "steps": [{"step_number": 1, "action": plan_text, "description": "LLM response as single step"}],
                "estimated_duration": 0,
                "safety_considerations": []
            }

# Example usage
def main():
    # Initialize planner (you'll need to provide your OpenAI API key)
    # planner = LLMPlanner(api_key="your-api-key")

    # For demonstration, we'll show the structure
    task_description = "Navigate to the kitchen, find a red cup, and bring it to the table"
    context = {
        "robot_capabilities": ["navigation", "object_detection", "manipulation"],
        "environment_map": ["kitchen", "living_room", "dining_area"],
        "current_location": "living_room"
    }

    print(f"Planning task: {task_description}")
    print(f"Context: {context}")

    # plan = planner.plan_task(task_description, context)
    # print(f"Generated plan: {json.dumps(plan, indent=2)}")

if __name__ == "__main__":
    main()
```

## Advanced LLM Planning with Context Awareness

### Context-Aware Planning

```python
class ContextAwareLLMPlanner(LLMPlanner):
    def __init__(self, api_key: str = None, model: str = "gpt-3.5-turbo"):
        super().__init__(api_key, model)
        self.context_history = []
        self.max_context_length = 10

    def plan_with_context(self,
                         task_description: str,
                         current_state: Dict[str, Any],
                         previous_actions: List[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Plan with awareness of current state and previous actions
        """
        context = {
            "current_state": current_state,
            "previous_actions": previous_actions or [],
            "environment_knowledge": self._get_environment_knowledge(),
            "robot_capabilities": self._get_robot_capabilities()
        }

        # Add to context history
        self.context_history.append({
            "task": task_description,
            "context": context,
            "timestamp": time.time()
        })

        # Keep only recent context
        if len(self.context_history) > self.max_context_length:
            self.context_history = self.context_history[-self.max_context_length:]

        return self.plan_task(task_description, context)

    def _get_environment_knowledge(self) -> Dict[str, Any]:
        """
        Get current environment knowledge
        """
        return {
            "known_locations": ["kitchen", "living_room", "bedroom", "office", "dining_area"],
            "object_types": ["cup", "bottle", "book", "remote", "phone", "box"],
            "navigation_constraints": {
                "obstacles": [],
                "forbidden_areas": [],
                "preferred_paths": []
            }
        }

    def _get_robot_capabilities(self) -> Dict[str, Any]:
        """
        Get robot capabilities
        """
        return {
            "locomotion": ["navigation", "obstacle_avoidance"],
            "manipulation": ["grasping", "placement", "lifting_5kg"],
            "perception": ["object_detection", "pose_estimation", "mapping"],
            "communication": ["text_to_speech", "speech_recognition"]
        }

    def adapt_plan(self, original_plan: Dict[str, Any], feedback: Dict[str, Any]) -> Dict[str, Any]:
        """
        Adapt plan based on feedback and new information
        """
        adaptation_prompt = f"""
        Original Plan: {json.dumps(original_plan, indent=2)}

        Feedback: {json.dumps(feedback, indent=2)}

        Please adapt the plan based on the feedback. Consider:
        1. What went wrong or needs to be changed
        2. How to modify the plan to address the issues
        3. Whether to continue with the original goal or modify it
        4. Any new constraints or opportunities

        Return the adapted plan in the same JSON format.
        """

        for attempt in range(self.max_retries):
            try:
                response = openai.ChatCompletion.create(
                    model=self.model,
                    messages=[
                        {"role": "system", "content": self._get_system_prompt()},
                        {"role": "user", "content": adaptation_prompt}
                    ],
                    temperature=0.4,
                    max_tokens=1000
                )

                adapted_plan_text = response.choices[0].message.content.strip()
                adapted_plan = self._parse_plan(adapted_plan_text)
                return adapted_plan

            except Exception as e:
                print(f"Adaptation attempt {attempt + 1} failed: {e}")
                if attempt < self.max_retries - 1:
                    time.sleep(self.retry_delay * (2 ** attempt))
                else:
                    # Return original plan if adaptation fails
                    return original_plan
```

## Integration with Robot Execution Systems

### ROS 2 Integration

```python
import rclpy
from rclpy.node import Node
from std_msgs.msg import String
from action_msgs.msg import GoalStatus
import json
import threading

class LLMPlanningNode(Node):
    def __init__(self):
        super().__init__('llm_planning_node')

        # Initialize LLM planner
        self.llm_planner = ContextAwareLLMPlanner()

        # Publishers and subscribers
        self.plan_request_sub = self.create_subscription(
            String, '/llm_plan/request', self.plan_request_callback, 10)
        self.plan_pub = self.create_publisher(String, '/llm_plan/result', 10)
        self.execution_feedback_sub = self.create_subscription(
            String, '/execution_feedback', self.execution_feedback_callback, 10)

        # Plan execution tracking
        self.current_plan = None
        self.plan_execution_status = {}  # Track execution of each step

        # Thread for handling plan execution
        self.execution_thread = None
        self.execution_active = False

        self.get_logger().info('LLM Planning Node initialized')

    def plan_request_callback(self, msg):
        """
        Handle plan requests
        """
        try:
            request_data = json.loads(msg.data)
            task_description = request_data.get('task', '')
            context = request_data.get('context', {})

            self.get_logger().info(f'Received plan request: {task_description}')

            # Generate plan using LLM
            plan = self.llm_planner.plan_with_context(task_description, context)

            # Publish the plan
            plan_msg = String()
            plan_msg.data = json.dumps({
                'plan': plan,
                'task': task_description,
                'timestamp': time.time()
            })
            self.plan_pub.publish(plan_msg)

            self.get_logger().info('Plan published successfully')

        except json.JSONDecodeError:
            self.get_logger().error('Invalid JSON in plan request')
        except Exception as e:
            self.get_logger().error(f'Error generating plan: {e}')

    def execution_feedback_callback(self, msg):
        """
        Handle feedback from plan execution
        """
        try:
            feedback_data = json.loads(msg.data)
            step_id = feedback_data.get('step_id')
            status = feedback_data.get('status')  # 'success', 'failure', 'partial'
            details = feedback_data.get('details', {})

            # Update execution status
            if step_id in self.plan_execution_status:
                self.plan_execution_status[step_id]['status'] = status
                self.plan_execution_status[step_id]['details'] = details

            # If step failed, consider plan adaptation
            if status == 'failure':
                self.handle_plan_failure(step_id, details)

        except json.JSONDecodeError:
            self.get_logger().error('Invalid JSON in feedback message')
        except Exception as e:
            self.get_logger().error(f'Error processing feedback: {e}')

    def handle_plan_failure(self, failed_step_id: str, details: Dict[str, Any]):
        """
        Handle plan failure and consider adaptation
        """
        if self.current_plan:
            feedback = {
                'failed_step': failed_step_id,
                'failure_details': details,
                'current_plan': self.current_plan,
                'execution_status': self.plan_execution_status
            }

            # Adapt the plan
            adapted_plan = self.llm_planner.adapt_plan(self.current_plan, feedback)

            # Publish adapted plan
            plan_msg = String()
            plan_msg.data = json.dumps({
                'plan': adapted_plan,
                'task': 'Adapted plan due to execution failure',
                'timestamp': time.time(),
                'adaptation_reason': 'Original plan step failed'
            })
            self.plan_pub.publish(plan_msg)

            self.get_logger().info(f'Adapted plan published due to failure in step {failed_step_id}')

    def start_plan_execution(self, plan: Dict[str, Any]):
        """
        Start executing a plan in a separate thread
        """
        self.current_plan = plan
        self.execution_active = True

        # Initialize execution status for each step
        for step in plan.get('steps', []):
            step_id = f"step_{step.get('step_number', 0)}"
            self.plan_execution_status[step_id] = {
                'status': 'pending',
                'start_time': time.time(),
                'details': {}
            }

        # Start execution thread
        self.execution_thread = threading.Thread(target=self._execute_plan, args=(plan,))
        self.execution_thread.start()

    def _execute_plan(self, plan: Dict[str, Any]):
        """
        Execute the plan step by step
        """
        steps = plan.get('steps', [])

        for i, step in enumerate(steps):
            if not self.execution_active:
                break

            step_id = f"step_{step.get('step_number', i)}"

            # Update status
            self.plan_execution_status[step_id]['status'] = 'executing'
            self.plan_execution_status[step_id]['start_time'] = time.time()

            # Execute the step
            success = self._execute_step(step)

            # Update status
            self.plan_execution_status[step_id]['status'] = 'success' if success else 'failure'
            self.plan_execution_status[step_id]['end_time'] = time.time()

            if not success:
                self.get_logger().error(f'Step {step_id} failed')
                break

        self.execution_active = False
        self.get_logger().info('Plan execution completed')

    def _execute_step(self, step: Dict[str, Any]) -> bool:
        """
        Execute a single step of the plan
        This is a placeholder - actual implementation would depend on the robot system
        """
        action = step.get('action', '')
        parameters = step.get('parameters', {})

        self.get_logger().info(f'Executing step: {action} with params: {parameters}')

        # Simulate step execution
        # In a real system, this would call robot action services
        time.sleep(1)  # Simulate execution time

        # For now, return success
        return True

    def cancel_execution(self):
        """
        Cancel current plan execution
        """
        self.execution_active = False
        if self.execution_thread:
            self.execution_thread.join()
```

## Specialized Planning Domains

### Navigation Planning with LLM

```python
class NavigationLLMPlanner(LLMPlanner):
    def __init__(self, api_key: str = None, model: str = "gpt-3.5-turbo"):
        super().__init__(api_key, model)
        self.map_data = {}  # Would contain actual map information

    def plan_navigation(self, start_location: str, goal_location: str, constraints: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Plan navigation route using LLM
        """
        if constraints is None:
            constraints = {}

        navigation_context = {
            "start_location": start_location,
            "goal_location": goal_location,
            "map_data": self.map_data,
            "constraints": constraints,
            "robot_capabilities": {
                "max_speed": "0.5 m/s",
                "turning_radius": "0.3 m",
                "obstacle_detection_range": "3.0 m"
            }
        }

        task_description = f"Navigate from {start_location} to {goal_location}"
        return self.plan_task(task_description, navigation_context)

    def plan_complex_navigation(self, waypoints: List[str], preferences: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Plan navigation with multiple waypoints
        """
        if preferences is None:
            preferences = {}

        task_description = f"Navigate through waypoints: {', '.join(waypoints)}"
        context = {
            "waypoints": waypoints,
            "preferences": preferences,
            "environment": {
                "known_obstacles": [],
                "preferred_paths": [],
                "forbidden_areas": []
            }
        }

        return self.plan_task(task_description, context)
```

### Manipulation Planning with LLM

```python
class ManipulationLLMPlanner(LLMPlanner):
    def __init__(self, api_key: str = None, model: str = "gpt-3.5-turbo"):
        super().__init__(api_key, model)

    def plan_manipulation(self, object_description: str, action: str, environment_context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Plan manipulation task using LLM
        """
        task_description = f"{action} {object_description}"
        context = {
            "object_description": object_description,
            "desired_action": action,
            "environment_context": environment_context,
            "robot_manipulator": {
                "degrees_of_freedom": 7,
                "gripper_type": "parallel_jaw",
                "max_payload": "5 kg",
                "reach": "1.2 m"
            }
        }

        return self.plan_task(task_description, context)

    def plan_complex_manipulation(self, task_sequence: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Plan complex manipulation sequences
        """
        task_descriptions = []
        for task in task_sequence:
            task_descriptions.append(f"{task['action']} {task['object']}")

        task_description = f"Execute manipulation sequence: {' -> '.join(task_descriptions)}"
        context = {
            "task_sequence": task_sequence,
            "spatial_relations": ["on", "in", "next_to", "above", "below"],
            "grasping_strategies": ["top_grasp", "side_grasp", "pinch_grasp"]
        }

        return self.plan_task(task_description, context)
```

## Performance Optimization

### Caching and Optimization

```python
import functools
import hashlib
from typing import Tuple

class OptimizedLLMPlanner(LLMPlanner):
    def __init__(self, api_key: str = None, model: str = "gpt-3.5-turbo"):
        super().__init__(api_key, model)
        self.plan_cache = {}
        self.max_cache_size = 100

    def _get_cache_key(self, task_description: str, context: Dict[str, Any]) -> str:
        """
        Generate a cache key for the given task and context
        """
        cache_input = f"{task_description}_{json.dumps(context, sort_keys=True)}"
        return hashlib.md5(cache_input.encode()).hexdigest()

    def plan_task(self, task_description: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Plan task with caching
        """
        if context is None:
            context = {}

        cache_key = self._get_cache_key(task_description, context)

        # Check cache first
        if cache_key in self.plan_cache:
            self.get_logger().info('Retrieved plan from cache')
            return self.plan_cache[cache_key]

        # Generate new plan
        plan = super().plan_task(task_description, context)

        # Add to cache
        if len(self.plan_cache) >= self.max_cache_size:
            # Remove oldest entry (simple FIFO)
            oldest_key = next(iter(self.plan_cache))
            del self.plan_cache[oldest_key]

        self.plan_cache[cache_key] = plan

        return plan

    def get_logger(self):
        """
        Simple logger for the optimized planner
        """
        class Logger:
            def info(self, msg):
                print(f"INFO: {msg}")
            def error(self, msg):
                print(f"ERROR: {msg}")
        return Logger()
```

## Safety and Validation

### Plan Validation and Safety Checks

```python
class SafeLLMPlanner(LLMPlanner):
    def __init__(self, api_key: str = None, model: str = "gpt-3.5-turbo"):
        super().__init__(api_key, model)
        self.safety_rules = self._define_safety_rules()

    def _define_safety_rules(self) -> List[Dict[str, Any]]:
        """
        Define safety rules for plan validation
        """
        return [
            {
                "rule": "no_dangerous_actions",
                "description": "Avoid actions that could harm humans or robot",
                "actions_to_avoid": ["high_speed_navigation", "forceful_grasping", "uncontrolled_movement"]
            },
            {
                "rule": "no_forbidden_areas",
                "description": "Avoid navigating to restricted areas",
                "forbidden_areas": ["stairs", "cliff_edges", "construction_zones"]
            },
            {
                "rule": "feasibility_check",
                "description": "Ensure actions are physically possible",
                "constraints": {
                    "weight_limits": "5kg",
                    "reach_limits": "1.2m",
                    "precision_limits": "1cm"
                }
            }
        ]

    def validate_plan(self, plan: Dict[str, Any]) -> Tuple[bool, List[str]]:
        """
        Validate plan against safety rules
        """
        issues = []

        # Check each step in the plan
        for step in plan.get('steps', []):
            action = step.get('action', '').lower()

            # Check for dangerous actions
            for rule in self.safety_rules:
                if rule['rule'] == 'no_dangerous_actions':
                    for dangerous_action in rule['actions_to_avoid']:
                        if dangerous_action in action:
                            issues.append(f"Dangerous action detected: {action}")

        # Check if plan is empty
        if not plan.get('steps'):
            issues.append("Plan contains no steps")

        # Check estimated duration
        estimated_duration = plan.get('estimated_duration', 0)
        if estimated_duration <= 0:
            issues.append("Invalid estimated duration")

        return len(issues) == 0, issues

    def plan_task(self, task_description: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Plan task with safety validation
        """
        plan = super().plan_task(task_description, context)

        # Validate the plan
        is_valid, issues = self.validate_plan(plan)

        if not is_valid:
            self.get_logger().error(f"Plan validation failed with issues: {issues}")

            # Try to fix the plan by asking LLM to revise it
            revised_plan = self.revise_plan(plan, issues)
            return revised_plan

        return plan

    def revise_plan(self, original_plan: Dict[str, Any], issues: List[str]) -> Dict[str, Any]:
        """
        Revise plan to address safety issues
        """
        revision_prompt = f"""
        Original Plan: {json.dumps(original_plan, indent=2)}

        Safety Issues: {', '.join(issues)}

        Please revise the plan to address these safety issues while still accomplishing the original task.
        Make sure the revised plan follows safety guidelines and is executable by a robot system.
        """

        for attempt in range(self.max_retries):
            try:
                response = openai.ChatCompletion.create(
                    model=self.model,
                    messages=[
                        {"role": "system", "content": self._get_system_prompt()},
                        {"role": "user", "content": revision_prompt}
                    ],
                    temperature=0.3,
                    max_tokens=1000
                )

                revised_plan_text = response.choices[0].message.content.strip()
                revised_plan = self._parse_plan(revised_plan_text)

                # Validate the revised plan
                is_valid, new_issues = self.validate_plan(revised_plan)
                if is_valid:
                    return revised_plan
                else:
                    # If still not valid, try again (but limit retries to avoid infinite loop)
                    if attempt < 1:  # Only try to revise once more
                        continue
                    else:
                        return revised_plan  # Return what we have

            except Exception as e:
                print(f"Revision attempt {attempt + 1} failed: {e}")
                if attempt < self.max_retries - 1:
                    time.sleep(self.retry_delay * (2 ** attempt))
                else:
                    return original_plan  # Return original if revision fails
```

## Hands-on Exercise

Create an LLM-based planning system for your robot that:
1. Implements basic task planning using an LLM
2. Includes context awareness and plan adaptation
3. Integrates with your robot's execution system
4. Includes safety validation and error handling
5. Optimizes for performance through caching

This exercise will help you create an intelligent planning system that can generate complex robot behaviors from natural language commands.