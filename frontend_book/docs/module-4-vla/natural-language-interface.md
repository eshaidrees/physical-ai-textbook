---
sidebar_position: 3
---

# Natural Language Interface for Robotics

This section covers building natural language interfaces that allow humans to interact with robots using voice and text commands. You'll learn to implement speech recognition, natural language understanding, and command execution systems that enable intuitive human-robot interaction.

## Understanding Natural Language Interfaces

Natural language interfaces enable robots to:
- Understand spoken or written commands
- Interpret intent from natural language
- Execute appropriate robotic actions
- Provide feedback through speech or text
- Maintain conversational context

### Components of a Natural Language Interface

A complete natural language interface consists of:
1. **Speech Recognition** (if voice-based)
2. **Natural Language Understanding** (NLU)
3. **Intent Classification**
4. **Entity Extraction**
5. **Action Mapping**
6. **Response Generation**

## Implementing Speech Recognition

### Voice Command Processing

```python
import speech_recognition as sr
import pyttsx3
import rospy
from std_msgs.msg import String
import json

class VoiceCommandProcessor:
    def __init__(self):
        # Initialize speech recognition
        self.recognizer = sr.Recognizer()
        self.microphone = sr.Microphone()

        # Initialize text-to-speech
        self.tts_engine = pyttsx3.init()
        self.tts_engine.setProperty('rate', 150)  # Speed of speech
        self.tts_engine.setProperty('volume', 0.9)  # Volume level

        # Set microphone calibration
        with self.microphone as source:
            self.recognizer.adjust_for_ambient_noise(source)

        # Publishers for commands
        self.command_publisher = rospy.Publisher('/robot/command', String, queue_size=10)
        self.response_publisher = rospy.Publisher('/robot/response', String, queue_size=10)

    def listen_for_command(self):
        """
        Listen for voice command and return recognized text
        """
        try:
            with self.microphone as source:
                print("Listening for command...")
                audio = self.recognizer.listen(source, timeout=5, phrase_time_limit=10)

            # Recognize speech using Google's speech recognition
            command_text = self.recognizer.recognize_google(audio)
            print(f"Recognized command: {command_text}")
            return command_text

        except sr.WaitTimeoutError:
            print("No speech detected within timeout")
            return None
        except sr.UnknownValueError:
            print("Could not understand audio")
            return None
        except sr.RequestError as e:
            print(f"Error with speech recognition service: {e}")
            return None

    def speak_response(self, text):
        """
        Speak a response to the user
        """
        print(f"Speaking: {text}")
        self.tts_engine.say(text)
        self.tts_engine.runAndWait()

    def process_command(self, command_text):
        """
        Process the recognized command and execute appropriate action
        """
        if not command_text:
            return "I didn't understand that command."

        # Parse and execute command
        intent, entities = self.parse_command(command_text)

        if intent:
            # Execute the command based on intent
            response = self.execute_command(intent, entities)
            return response
        else:
            return f"I don't know how to {command_text}"

    def parse_command(self, command_text):
        """
        Parse command to extract intent and entities
        """
        command_lower = command_text.lower()

        # Define command patterns
        command_patterns = {
            'navigation': [
                'go to', 'move to', 'navigate to', 'go to the', 'move to the',
                'go to location', 'move to location'
            ],
            'manipulation': [
                'pick up', 'grasp', 'take', 'grab', 'place', 'put down',
                'move object', 'lift object'
            ],
            'action': [
                'stop', 'start', 'pause', 'resume', 'look', 'turn',
                'rotate', 'spin', 'dance', 'wave', 'greet'
            ],
            'information': [
                'what is', 'where is', 'how many', 'tell me about',
                'describe', 'find', 'locate', 'search for'
            ]
        }

        # Identify intent based on keywords
        for intent, patterns in command_patterns.items():
            for pattern in patterns:
                if pattern in command_lower:
                    # Extract target entity
                    target = command_lower.replace(pattern, '').strip()
                    if target.startswith('the '):
                        target = target[4:]  # Remove 'the ' prefix

                    return intent, {'target': target, 'full_command': command_text}

        # If no pattern matches, return unknown
        return 'unknown', {'command': command_text}

    def execute_command(self, intent, entities):
        """
        Execute the command based on intent and entities
        """
        target = entities.get('target', '')

        if intent == 'navigation':
            return self.execute_navigation_command(target)
        elif intent == 'manipulation':
            return self.execute_manipulation_command(target)
        elif intent == 'action':
            return self.execute_action_command(target)
        elif intent == 'information':
            return self.execute_information_command(target)
        else:
            return f"Unknown command intent: {intent}"

    def execute_navigation_command(self, target):
        """
        Execute navigation command
        """
        # Publish navigation command
        nav_command = {
            'action': 'navigate',
            'target': target,
            'type': 'navigation'
        }

        command_msg = String()
        command_msg.data = json.dumps(nav_command)
        self.command_publisher.publish(command_msg)

        return f"Moving to {target}"

    def execute_manipulation_command(self, target):
        """
        Execute manipulation command
        """
        # Publish manipulation command
        manip_command = {
            'action': 'manipulate',
            'target': target,
            'type': 'manipulation'
        }

        command_msg = String()
        command_msg.data = json.dumps(manip_command)
        self.command_publisher.publish(command_msg)

        return f"Attempting to manipulate {target}"

    def execute_action_command(self, target):
        """
        Execute action command
        """
        # Publish action command
        action_command = {
            'action': target,
            'type': 'action'
        }

        command_msg = String()
        command_msg.data = json.dumps(action_command)
        self.command_publisher.publish(command_msg)

        return f"Performing action: {target}"

    def execute_information_command(self, target):
        """
        Execute information command
        """
        # Publish information command
        info_command = {
            'action': 'get_info',
            'target': target,
            'type': 'information'
        }

        command_msg = String()
        command_msg.data = json.dumps(info_command)
        self.command_publisher.publish(command_msg)

        return f"Looking for information about {target}"

# ROS Node implementation
import rclpy
from rclpy.node import Node

class NaturalLanguageNode(Node):
    def __init__(self):
        super().__init__('natural_language_interface')

        # Initialize voice command processor
        self.voice_processor = VoiceCommandProcessor()

        # Publishers and subscribers
        self.response_publisher = self.create_publisher(String, '/natural_language/response', 10)
        self.command_sub = self.create_subscription(
            String, '/natural_language/command', self.command_callback, 10)

        # Timer for continuous listening
        self.listen_timer = self.create_timer(2.0, self.continuous_listen)

        self.get_logger().info('Natural Language Interface Node initialized')

    def command_callback(self, msg):
        """
        Handle incoming text commands
        """
        try:
            command_text = msg.data
            response = self.voice_processor.process_command(command_text)

            response_msg = String()
            response_msg.data = response
            self.response_publisher.publish(response_msg)

            self.get_logger().info(f'Processed command: {command_text}, Response: {response}')

        except Exception as e:
            self.get_logger().error(f'Error processing command: {e}')

    def continuous_listen(self):
        """
        Continuously listen for voice commands
        """
        # This method could be enhanced to continuously listen for voice commands
        # For now, we'll just process any queued text commands
        pass

def main(args=None):
    rclpy.init(args=args)
    node = NaturalLanguageNode()

    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        node.get_logger().info('Shutting down natural language interface')
    finally:
        node.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()
```

## Natural Language Understanding with Transformers

Using transformer-based models for more sophisticated language understanding:

```python
import torch
from transformers import AutoTokenizer, AutoModelForSequenceClassification
from transformers import pipeline
import rospy
from std_msgs.msg import String
import json

class TransformerNLU:
    def __init__(self):
        # Load pre-trained model for intent classification
        self.tokenizer = AutoTokenizer.from_pretrained("microsoft/DialoGPT-medium")

        # For intent classification, we could use a model like:
        # "microsoft/DialoGPT-medium" or a specialized intent classification model
        self.intent_classifier = pipeline(
            "text-classification",
            model="microsoft/DialoGPT-medium",
            tokenizer="microsoft/DialoGPT-medium"
        )

        # Define intent-action mapping
        self.intent_action_map = {
            'navigation': self.execute_navigation,
            'manipulation': self.execute_manipulation,
            'information': self.execute_information,
            'action': self.execute_action
        }

    def classify_intent(self, text):
        """
        Classify the intent of the given text
        """
        # This is a simplified approach - in practice, you'd train a specific intent classifier
        text_lower = text.lower()

        # Simple keyword-based classification (should be replaced with proper ML model)
        if any(keyword in text_lower for keyword in ['go to', 'move to', 'navigate', 'location']):
            return 'navigation'
        elif any(keyword in text_lower for keyword in ['pick', 'grasp', 'take', 'grab', 'place', 'put']):
            return 'manipulation'
        elif any(keyword in text_lower for keyword in ['what', 'where', 'how', 'find', 'locate', 'search']):
            return 'information'
        elif any(keyword in text_lower for keyword in ['stop', 'start', 'dance', 'wave', 'greet']):
            return 'action'
        else:
            return 'unknown'

    def extract_entities(self, text):
        """
        Extract named entities from the text
        """
        # Simple entity extraction based on keywords and context
        entities = {}

        # This is a simplified approach - in practice, use NER models
        if 'navigation' in text.lower():
            # Extract location entities
            for word in text.split():
                if word.lower() in ['kitchen', 'bedroom', 'living room', 'office', 'hallway', 'table', 'chair']:
                    entities['location'] = word

        elif 'manipulation' in text.lower():
            # Extract object entities
            for word in text.split():
                if word.lower() in ['cup', 'bottle', 'book', 'remote', 'box', 'object']:
                    entities['object'] = word

        return entities

    def process_command(self, command_text):
        """
        Process command using transformer-based NLU
        """
        intent = self.classify_intent(command_text)
        entities = self.extract_entities(command_text)

        if intent != 'unknown' and intent in self.intent_action_map:
            return self.intent_action_map[intent](entities)
        else:
            return f"I don't understand the command: {command_text}"

    def execute_navigation(self, entities):
        """
        Execute navigation action
        """
        location = entities.get('location', 'unknown location')
        return f"Navigating to {location}"

    def execute_manipulation(self, entities):
        """
        Execute manipulation action
        """
        obj = entities.get('object', 'unknown object')
        return f"Attempting to manipulate {obj}"

    def execute_information(self, entities):
        """
        Execute information action
        """
        target = entities.get('target', 'unknown target')
        return f"Looking for information about {target}"

    def execute_action(self, entities):
        """
        Execute general action
        """
        return f"Performing requested action"
```

## Context-Aware Dialogue Management

Creating a more sophisticated dialogue system that maintains context:

```python
class ContextualDialogueManager:
    def __init__(self):
        self.context = {}
        self.conversation_history = []
        self.max_history = 10  # Keep last 10 exchanges

    def update_context(self, user_input, system_response, action_result):
        """
        Update the dialogue context based on interaction
        """
        # Add current exchange to history
        current_exchange = {
            'user_input': user_input,
            'system_response': system_response,
            'action_result': action_result,
            'timestamp': rospy.Time.now().to_sec()
        }

        self.conversation_history.append(current_exchange)

        # Keep only recent history
        if len(self.conversation_history) > self.max_history:
            self.conversation_history.pop(0)

        # Update context variables based on conversation
        if user_input and 'location' in user_input:
            self.context['last_location'] = user_input

        if user_input and any(word in user_input.lower() for word in ['this', 'that', 'it']):
            # Reference resolution - find what "it" refers to
            if self.conversation_history:
                # Look for recently mentioned objects
                for exchange in reversed(self.conversation_history[:-1]):
                    if 'object' in str(exchange):
                        self.context['pronoun_reference'] = exchange.get('user_input', '')

    def resolve_references(self, command):
        """
        Resolve pronouns and references in the command
        """
        resolved_command = command.lower()

        # Resolve "it" - find what it refers to
        if 'it' in resolved_command and 'pronoun_reference' in self.context:
            resolved_command = resolved_command.replace('it', self.context['pronoun_reference'])

        # Resolve "there" - based on last known location
        if 'there' in resolved_command and 'last_location' in self.context:
            resolved_command = resolved_command.replace('there', self.context['last_location'])

        return resolved_command

    def generate_response(self, intent, entities, action_result):
        """
        Generate appropriate response based on action result
        """
        if action_result.get('success', False):
            if intent == 'navigation':
                return f"I have reached {entities.get('target', 'the location')}."
            elif intent == 'manipulation':
                return f"I have successfully manipulated {entities.get('target', 'the object')}."
            else:
                return f"Action completed successfully."
        else:
            error_msg = action_result.get('error', 'Unknown error occurred')
            return f"I couldn't complete the action: {error_msg}"
```

## Voice User Interface Best Practices

### Design Principles

1. **Natural Language**: Use conversational language patterns
2. **Feedback**: Always acknowledge user commands
3. **Error Handling**: Gracefully handle misunderstandings
4. **Context Awareness**: Remember previous interactions
5. **Robustness**: Handle ambiguous or incomplete commands

### Error Handling

```python
class RobustVoiceInterface:
    def __init__(self):
        self.retry_count = 0
        self.max_retries = 3

    def handle_recognition_error(self, error_type, original_command=None):
        """
        Handle different types of recognition errors
        """
        if error_type == "unknown_command":
            responses = [
                "I didn't understand that command. Could you repeat it?",
                "I'm not sure what you mean. Can you rephrase that?",
                "I couldn't process that command. Please try again."
            ]
            return responses[self.retry_count % len(responses)]

        elif error_type == "unclear_reference":
            return "I'm not sure what you're referring to. Can you be more specific?"

        elif error_type == "unavailable_action":
            return "I can't perform that action right now. Is there something else I can help with?"

        else:
            return "I encountered an error. Could you please repeat your command?"

    def confirm_critical_commands(self, command):
        """
        Confirm critical or potentially dangerous commands
        """
        critical_actions = ['stop', 'emergency', 'shut down', 'power off', 'reset']

        if any(action in command.lower() for action in critical_actions):
            return True
        return False
```

## Integration with ROS 2

Complete ROS 2 node for natural language interface:

```python
import rclpy
from rclpy.node import Node
from std_msgs.msg import String
from builtin_interfaces.msg import Time
import speech_recognition as sr
import pyttsx3
import json

class NaturalLanguageInterfaceNode(Node):
    def __init__(self):
        super().__init__('natural_language_interface')

        # Initialize speech components
        self.recognizer = sr.Recognizer()
        self.microphone = sr.Microphone()
        self.tts_engine = pyttsx3.init()

        # Calibrate microphone
        with self.microphone as source:
            self.recognizer.adjust_for_ambient_noise(source)

        # Publishers and subscribers
        self.command_pub = self.create_publisher(String, '/robot/structured_command', 10)
        self.response_pub = self.create_publisher(String, '/natural_language/response', 10)
        self.status_sub = self.create_subscription(
            String, '/robot/status', self.status_callback, 10)

        # Timer for continuous listening
        self.listen_timer = self.create_timer(3.0, self.check_for_voice_command)

        # Command queue for processing
        self.command_queue = []

        self.get_logger().info('Natural Language Interface initialized')

    def check_for_voice_command(self):
        """
        Check for and process voice commands
        """
        try:
            with self.microphone as source:
                # Listen for command with timeout
                audio = self.recognizer.listen(source, timeout=2.0, phrase_time_limit=8.0)

            # Recognize speech
            command_text = self.recognizer.recognize_google(audio)
            self.get_logger().info(f'Recognized: {command_text}')

            # Process command
            response = self.process_command(command_text)

            # Publish response
            response_msg = String()
            response_msg.data = response
            self.response_pub.publish(response_msg)

            # Speak response
            self.tts_engine.say(response)
            self.tts_engine.runAndWait()

        except sr.WaitTimeoutError:
            # No command detected, which is normal
            pass
        except sr.UnknownValueError:
            response = "Sorry, I couldn't understand that command."
            self.tts_engine.say(response)
            self.tts_engine.runAndWait()
        except sr.RequestError as e:
            self.get_logger().error(f'Speech recognition error: {e}')
        except Exception as e:
            self.get_logger().error(f'Error in voice command processing: {e}')

    def process_command(self, command_text):
        """
        Process natural language command and convert to structured command
        """
        # Parse command
        intent, entities = self.parse_command(command_text)

        if intent and intent != 'unknown':
            # Create structured command
            structured_cmd = {
                'intent': intent,
                'entities': entities,
                'raw_command': command_text,
                'timestamp': self.get_clock().now().to_msg()
            }

            # Publish structured command
            cmd_msg = String()
            cmd_msg.data = json.dumps(structured_cmd)
            self.command_pub.publish(cmd_msg)

            return f"I will {intent} to {entities.get('target', 'the target')}."
        else:
            return f"I don't understand how to '{command_text}'. Can you rephrase that?"

    def parse_command(self, command_text):
        """
        Parse command text to extract intent and entities
        """
        command_lower = command_text.lower()

        # Define intent patterns
        patterns = {
            'navigation': ['go to', 'move to', 'navigate to', 'go to the', 'move to the'],
            'manipulation': ['pick up', 'grasp', 'take', 'grab', 'place', 'put'],
            'action': ['stop', 'start', 'dance', 'wave', 'greet', 'look'],
            'information': ['what', 'where', 'find', 'locate', 'search']
        }

        for intent, intent_patterns in patterns.items():
            for pattern in intent_patterns:
                if pattern in command_lower:
                    target = command_lower.replace(pattern, '').strip()
                    if target.startswith('the '):
                        target = target[4:]
                    return intent, {'target': target}

        return 'unknown', {'command': command_text}

    def status_callback(self, msg):
        """
        Handle robot status updates
        """
        try:
            status_data = json.loads(msg.data)
            # Update context based on robot status if needed
        except json.JSONDecodeError:
            self.get_logger().error('Invalid status message format')

def main(args=None):
    rclpy.init(args=args)
    node = NaturalLanguageInterfaceNode()

    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        node.get_logger().info('Shutting down natural language interface')
    finally:
        node.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()
```

## Hands-on Exercise

Create a complete natural language interface for your robot that:
1. Implements speech recognition to capture voice commands
2. Uses natural language understanding to interpret commands
3. Maps recognized commands to appropriate robotic actions
4. Provides spoken feedback to the user
5. Handles errors and ambiguous commands gracefully

This exercise will help you build an intuitive interface that allows natural interaction with your humanoid robot.