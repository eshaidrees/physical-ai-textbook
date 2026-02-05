---
sidebar_position: 2
---

# Whisper Voice Recognition and Processing

This section covers implementing voice recognition and processing capabilities for your humanoid robot using OpenAI's Whisper model and related technologies. You'll learn to create robust voice interfaces that enable natural interaction with your robot.

## Understanding Whisper for Robotics

Whisper is a state-of-the-art speech recognition model that can transcribe speech to text with high accuracy. For robotics applications, Whisper provides:

- Multilingual support for global deployment
- Robustness to background noise and accents
- Real-time processing capabilities
- Integration with other AI systems

### Key Benefits for Robotics

1. **Natural Interaction**: Enables conversational interfaces
2. **Accessibility**: Supports users with different abilities
3. **Hands-Free Operation**: Allows operation without physical input
4. **Multimodal Integration**: Combines with vision and action systems

## Implementing Whisper Integration

### Basic Whisper Setup

```python
import whisper
import torch
import pyaudio
import wave
import numpy as np
import threading
import queue
import time

class WhisperVoiceInterface:
    def __init__(self, model_size="base"):
        """
        Initialize Whisper voice interface
        """
        # Load Whisper model
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.model = whisper.load_model(model_size).to(self.device)

        # Audio parameters
        self.format = pyaudio.paInt16
        self.channels = 1
        self.rate = 16000  # Whisper works best at 16kHz
        self.chunk = 1024
        self.record_seconds = 5

        # Audio stream
        self.audio = pyaudio.PyAudio()

        # Processing queue
        self.audio_queue = queue.Queue()
        self.transcription_queue = queue.Queue()

        # Control flags
        self.listening = False
        self.recording_thread = None

    def start_listening(self):
        """
        Start continuous listening for voice commands
        """
        self.listening = True
        self.recording_thread = threading.Thread(target=self._record_audio, daemon=True)
        self.recording_thread.start()

        # Start processing thread
        processing_thread = threading.Thread(target=self._process_audio, daemon=True)
        processing_thread.start()

        print("Whisper voice interface started")

    def stop_listening(self):
        """
        Stop listening and clean up resources
        """
        self.listening = False
        if self.recording_thread:
            self.recording_thread.join(timeout=1.0)

    def _record_audio(self):
        """
        Record audio in a separate thread
        """
        stream = self.audio.open(
            format=self.format,
            channels=self.channels,
            rate=self.rate,
            input=True,
            frames_per_buffer=self.chunk
        )

        while self.listening:
            # Record a chunk of audio
            frames = []
            for _ in range(0, int(self.rate / self.chunk * 1)):
                data = stream.read(self.chunk)
                frames.append(data)

            # Add audio data to queue
            audio_data = b''.join(frames)
            self.audio_queue.put(audio_data)

        stream.stop_stream()
        stream.close()

    def _process_audio(self):
        """
        Process audio data and generate transcriptions
        """
        while self.listening:
            try:
                # Get audio data from queue
                audio_data = self.audio_queue.get(timeout=1.0)

                # Convert to numpy array
                audio_array = np.frombuffer(audio_data, dtype=np.int16)
                audio_float = audio_array.astype(np.float32) / 32768.0  # Normalize to [-1, 1]

                # Transcribe using Whisper
                result = self.model.transcribe(audio_float, fp16=False if self.device == "cpu" else True)
                transcription = result["text"].strip()

                if transcription:  # Only add non-empty transcriptions
                    self.transcription_queue.put({
                        'text': transcription,
                        'timestamp': time.time(),
                        'confidence': result.get('avg_logprob', -0.5)  # Rough confidence measure
                    })

            except queue.Empty:
                continue
            except Exception as e:
                print(f"Error processing audio: {e}")

    def get_transcription(self):
        """
        Get the next available transcription
        """
        try:
            return self.transcription_queue.get_nowait()
        except queue.Empty:
            return None

    def transcribe_audio_file(self, audio_file_path):
        """
        Transcribe an audio file
        """
        result = self.model.transcribe(audio_file_path)
        return result["text"]

# Example usage
def main():
    # Initialize Whisper interface
    whisper_interface = WhisperVoiceInterface(model_size="base")

    # Start listening
    whisper_interface.start_listening()

    try:
        # Listen for commands for 30 seconds
        start_time = time.time()
        while time.time() - start_time < 30:
            transcription = whisper_interface.get_transcription()
            if transcription:
                print(f"Transcribed: {transcription['text']} (confidence: {transcription['confidence']:.2f})")

            time.sleep(0.1)  # Small delay to prevent busy waiting

    except KeyboardInterrupt:
        print("Stopping voice interface...")
    finally:
        whisper_interface.stop_listening()
        whisper_interface.audio.terminate()

if __name__ == "__main__":
    main()
```

## Advanced Voice Processing

### Voice Activity Detection (VAD)

```python
import webrtcvad
import collections

class VoiceActivityDetector:
    def __init__(self, aggressiveness=3):
        """
        Initialize Voice Activity Detector
        aggressiveness: 0-3, where 3 is the most aggressive
        """
        self.vad = webrtcvad.Vad(aggressiveness)
        self.rate = 16000  # VAD requires 8000, 16000, 32000, or 48000 Hz
        self.frame_duration = 30  # Duration of a frame in ms (10, 20, or 30)
        self.frame_size = int(self.rate * self.frame_duration / 1000) * 2  # 2 bytes per sample

    def is_speech(self, audio_frame):
        """
        Check if the audio frame contains speech
        audio_frame: bytes, 16-bit PCM audio
        """
        try:
            return self.vad.is_speech(audio_frame, self.rate)
        except:
            return False

class AdvancedWhisperInterface(WhisperVoiceInterface):
    def __init__(self, model_size="base"):
        super().__init__(model_size)

        # Add VAD for more efficient processing
        self.vad = VoiceActivityDetector(aggressiveness=2)
        self.speech_buffer = collections.deque(maxlen=4)  # Store last 4 frames
        self.is_speaking = False
        self.speech_start_time = None
        self.min_speech_duration = 0.5  # Minimum speech duration in seconds

    def _record_audio(self):
        """
        Record audio with VAD for efficient processing
        """
        stream = self.audio.open(
            format=self.format,
            channels=self.channels,
            rate=self.rate,
            input=True,
            frames_per_buffer=self.chunk
        )

        while self.listening:
            # Read audio in VAD-compatible chunks
            frames = []
            for _ in range(0, int(self.rate / self.chunk * 0.02)):  # 20ms chunks for VAD
                data = stream.read(self.chunk)
                frames.append(data)

                # Process for VAD
                if len(data) == self.frame_size:
                    is_speech = self.vad.is_speech(data)

                    if is_speech and not self.is_speaking:
                        # Speech started
                        self.is_speaking = True
                        self.speech_start_time = time.time()
                        self.speech_buffer.clear()
                        # Add previous frames to buffer
                        for prev_frame in list(self.speech_buffer):
                            frames.append(prev_frame)

                    elif not is_speech and self.is_speaking:
                        # Speech ended - check if it was long enough
                        if time.time() - self.speech_start_time >= self.min_speech_duration:
                            # Send accumulated speech for transcription
                            speech_data = b''.join(frames)
                            self.audio_queue.put(speech_data)

                        self.is_speaking = False
                        self.speech_start_time = None

                    # Store frame for potential pre-speech buffering
                    self.speech_buffer.append(data)

        stream.stop_stream()
        stream.close()
```

## Integration with Robot Systems

### Voice Command Processing for Robotics

```python
import rclpy
from rclpy.node import Node
from std_msgs.msg import String
from builtin_interfaces.msg import Time
import json

class VoiceCommandProcessorNode(Node):
    def __init__(self):
        super().__init__('voice_command_processor')

        # Initialize Whisper interface
        self.whisper_interface = AdvancedWhisperInterface(model_size="base")

        # Publishers for different command types
        self.navigation_pub = self.create_publisher(String, '/navigation/command', 10)
        self.manipulation_pub = self.create_publisher(String, '/manipulation/command', 10)
        self.system_pub = self.create_publisher(String, '/system/command', 10)
        self.response_pub = self.create_publisher(String, '/voice/response', 10)

        # Timer to check for new transcriptions
        self.transcription_timer = self.create_timer(0.1, self.check_transcriptions)

        # Start listening
        self.whisper_interface.start_listening()

        self.get_logger().info('Voice Command Processor initialized')

    def check_transcriptions(self):
        """
        Check for new transcriptions and process them
        """
        transcription = self.whisper_interface.get_transcription()
        if transcription:
            command_text = transcription['text']
            confidence = transcription['confidence']

            self.get_logger().info(f'Heard: "{command_text}" (confidence: {confidence:.2f})')

            # Only process if confidence is high enough
            if confidence > -0.8:  # Adjust threshold as needed
                self.process_command(command_text)
            else:
                self.get_logger().warn(f'Low confidence transcription ignored: {confidence:.2f}')

    def process_command(self, command_text):
        """
        Process the transcribed command
        """
        # Parse the command to determine intent
        command_data = self.parse_command(command_text.lower())

        if command_data:
            command_type = command_data.get('type')
            command_params = command_data.get('params', {})

            # Publish command to appropriate subsystem
            if command_type == 'navigation':
                self.publish_navigation_command(command_params)
            elif command_type == 'manipulation':
                self.publish_manipulation_command(command_params)
            elif command_type == 'system':
                self.publish_system_command(command_params)
            else:
                self.get_logger().warn(f'Unknown command type: {command_type}')

            # Send response back to user
            response = self.generate_response(command_data)
            self.publish_response(response)
        else:
            # Command not recognized
            response = f"Sorry, I didn't understand '{command_text}'. Could you repeat that?"
            self.publish_response(response)

    def parse_command(self, command_text):
        """
        Parse natural language command into structured data
        """
        # Navigation commands
        navigation_keywords = [
            'go to', 'move to', 'navigate to', 'go to the', 'move to the',
            'walk to', 'drive to', 'head to', 'go into', 'enter'
        ]

        # Manipulation commands
        manipulation_keywords = [
            'pick up', 'grasp', 'take', 'grab', 'lift', 'get',
            'put', 'place', 'drop', 'release', 'hold'
        ]

        # System commands
        system_keywords = [
            'stop', 'start', 'pause', 'resume', 'shutdown',
            'power off', 'turn off', 'hello', 'hi', 'greet'
        ]

        # Check for navigation commands
        for keyword in navigation_keywords:
            if keyword in command_text:
                # Extract target location
                target = command_text.replace(keyword, '').strip()
                if target.startswith('the '):
                    target = target[4:]

                return {
                    'type': 'navigation',
                    'params': {
                        'target': target,
                        'original': command_text
                    }
                }

        # Check for manipulation commands
        for keyword in manipulation_keywords:
            if keyword in command_text:
                # Extract target object
                target = command_text.replace(keyword, '').strip()
                if target.startswith('the '):
                    target = target[4:]

                action = 'grasp' if any(grasp_word in keyword for grasp_word in ['pick', 'grasp', 'take', 'grab', 'lift', 'get']) else 'place'

                return {
                    'type': 'manipulation',
                    'params': {
                        'action': action,
                        'target': target,
                        'original': command_text
                    }
                }

        # Check for system commands
        for keyword in system_keywords:
            if keyword in command_text:
                return {
                    'type': 'system',
                    'params': {
                        'command': keyword,
                        'original': command_text
                    }
                }

        # If no known command found
        return None

    def publish_navigation_command(self, params):
        """
        Publish navigation command
        """
        nav_command = {
            'action': 'navigate',
            'target': params.get('target', ''),
            'timestamp': self.get_clock().now().nanoseconds / 1e9
        }

        msg = String()
        msg.data = json.dumps(nav_command)
        self.navigation_pub.publish(msg)

        self.get_logger().info(f'Published navigation command: {params.get("target")}')

    def publish_manipulation_command(self, params):
        """
        Publish manipulation command
        """
        manip_command = {
            'action': params.get('action', 'grasp'),
            'target': params.get('target', ''),
            'timestamp': self.get_clock().now().nanoseconds / 1e9
        }

        msg = String()
        msg.data = json.dumps(manip_command)
        self.manipulation_pub.publish(msg)

        self.get_logger().info(f'Published manipulation command: {params.get("action")} {params.get("target")}')

    def publish_system_command(self, params):
        """
        Publish system command
        """
        system_command = {
            'command': params.get('command', ''),
            'timestamp': self.get_clock().now().nanoseconds / 1e9
        }

        msg = String()
        msg.data = json.dumps(system_command)
        self.system_pub.publish(msg)

        self.get_logger().info(f'Published system command: {params.get("command")}')

    def publish_response(self, response_text):
        """
        Publish voice response
        """
        response_msg = String()
        response_msg.data = response_text
        self.response_pub.publish(response_msg)

    def generate_response(self, command_data):
        """
        Generate appropriate response for the command
        """
        command_type = command_data.get('type', 'unknown')
        params = command_data.get('params', {})

        if command_type == 'navigation':
            target = params.get('target', 'unknown location')
            return f"Okay, I'm navigating to {target}."
        elif command_type == 'manipulation':
            action = params.get('action', 'manipulate')
            target = params.get('target', 'object')
            return f"Okay, I'll {action} the {target}."
        elif command_type == 'system':
            command = params.get('command', 'unknown')
            if command in ['hello', 'hi']:
                return "Hello! How can I help you?"
            else:
                return f"Okay, I'll {command}."
        else:
            return "I understand the command."

def main(args=None):
    rclpy.init(args=args)

    node = VoiceCommandProcessorNode()

    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        node.get_logger().info('Shutting down voice command processor')
    finally:
        node.whisper_interface.stop_listening()
        node.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()
```

## Real-time Voice Processing Optimization

### Optimized Real-time Processing

```python
import asyncio
import threading
from concurrent.futures import ThreadPoolExecutor
import time

class OptimizedWhisperInterface:
    def __init__(self, model_size="base"):
        # Load model
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.model = whisper.load_model(model_size).to(self.device)

        # Audio parameters
        self.rate = 16000
        self.chunk_size = 1024

        # Threading and async setup
        self.executor = ThreadPoolExecutor(max_workers=2)
        self.loop = asyncio.new_event_loop()

        # Audio buffer for continuous processing
        self.audio_buffer = np.array([])
        self.buffer_size = self.rate * 2  # 2 seconds of audio

        # Processing flags
        self.processing = False
        self.should_process = threading.Event()

        # Callback for transcriptions
        self.transcription_callback = None

    def set_transcription_callback(self, callback):
        """
        Set callback function for new transcriptions
        """
        self.transcription_callback = callback

    def add_audio_chunk(self, audio_chunk):
        """
        Add audio chunk to buffer for processing
        """
        # Convert to float32
        audio_float = np.frombuffer(audio_chunk, dtype=np.int16).astype(np.float32) / 32768.0

        # Add to buffer
        self.audio_buffer = np.concatenate([self.audio_buffer, audio_float])

        # Keep only the most recent buffer size
        if len(self.audio_buffer) > self.buffer_size:
            self.audio_buffer = self.audio_buffer[-self.buffer_size:]

        # Signal that processing is needed
        if len(self.audio_buffer) > self.rate * 0.5:  # At least 0.5 seconds of audio
            self.should_process.set()

    def process_audio_async(self):
        """
        Process audio buffer asynchronously
        """
        if not self.should_process.is_set():
            return

        if len(self.audio_buffer) < self.rate * 0.5:  # Less than 0.5 seconds
            return

        # Copy buffer to avoid modification during processing
        audio_to_process = self.audio_buffer.copy()

        # Submit transcription task to thread pool
        future = self.executor.submit(self._transcribe_audio, audio_to_process)
        future.add_done_callback(self._on_transcription_complete)

        # Clear the event
        self.should_process.clear()

    def _transcribe_audio(self, audio_data):
        """
        Transcribe audio data using Whisper
        """
        try:
            # Transcribe the audio
            result = self.model.transcribe(audio_data, fp16=False if self.device == "cpu" else True)
            return result["text"].strip()
        except Exception as e:
            print(f"Transcription error: {e}")
            return ""

    def _on_transcription_complete(self, future):
        """
        Handle completed transcription
        """
        try:
            transcription = future.result()
            if transcription and self.transcription_callback:
                self.transcription_callback(transcription)
        except Exception as e:
            print(f"Error in transcription callback: {e}")

    def continuous_processing(self):
        """
        Run continuous audio processing
        """
        while True:
            self.process_audio_async()
            time.sleep(0.1)  # Process every 100ms

# Integration with the robot system
class RealTimeVoiceInterface:
    def __init__(self):
        # Initialize components
        self.whisper = OptimizedWhisperInterface(model_size="base")
        self.audio_stream = None
        self.listening = False

        # Initialize PyAudio
        self.pyaudio = pyaudio.PyAudio()

    def start_listening(self, callback=None):
        """
        Start real-time listening with callback
        """
        if callback:
            self.whisper.set_transcription_callback(callback)

        # Open audio stream
        self.audio_stream = self.pyaudio.open(
            format=pyaudio.paInt16,
            channels=1,
            rate=16000,
            input=True,
            frames_per_buffer=1024
        )

        self.listening = True

        # Start processing thread
        processing_thread = threading.Thread(target=self.whisper.continuous_processing, daemon=True)
        processing_thread.start()

        # Start audio capture thread
        capture_thread = threading.Thread(target=self._capture_audio, daemon=True)
        capture_thread.start()

        print("Real-time voice interface started")

    def _capture_audio(self):
        """
        Capture audio in a separate thread
        """
        while self.listening:
            try:
                # Read audio chunk
                data = self.audio_stream.read(1024, exception_on_overflow=False)

                # Add to Whisper interface
                self.whisper.add_audio_chunk(data)

                time.sleep(0.01)  # Small delay
            except Exception as e:
                print(f"Audio capture error: {e}")
                break

    def stop_listening(self):
        """
        Stop listening and clean up
        """
        self.listening = False

        if self.audio_stream:
            self.audio_stream.stop_stream()
            self.audio_stream.close()

        self.pyaudio.terminate()
```

## Best Practices for Voice Interfaces

### Robust Voice Command Design

```python
class RobustVoiceCommandProcessor:
    def __init__(self):
        self.command_history = []
        self.max_history = 10
        self.confidence_threshold = 0.7

    def preprocess_command(self, command_text):
        """
        Preprocess command text for better recognition
        """
        # Remove common filler words
        fillers = ['um', 'uh', 'like', 'you know', 'so', 'well']

        processed = command_text.lower()
        for filler in fillers:
            processed = processed.replace(filler, '')

        # Clean up extra spaces
        processed = ' '.join(processed.split())

        return processed

    def validate_command(self, command_text, confidence):
        """
        Validate if the command is reliable enough to execute
        """
        # Check confidence
        if confidence < self.confidence_threshold:
            return False, "Low confidence transcription"

        # Check for common misrecognitions
        if len(command_text.strip()) < 3:
            return False, "Command too short"

        # Check if command contains actionable words
        actionable_patterns = [
            'go', 'move', 'take', 'pick', 'put', 'place', 'stop', 'start',
            'turn', 'rotate', 'look', 'find', 'search', 'navigate'
        ]

        has_actionable = any(pattern in command_text.lower() for pattern in actionable_patterns)
        if not has_actionable:
            return False, "Command doesn't contain actionable words"

        return True, "Valid command"

    def handle_command_error(self, error_type, original_command):
        """
        Handle different types of command errors
        """
        error_responses = {
            'low_confidence': "I didn't catch that clearly. Could you repeat your command?",
            'invalid_format': "I'm not sure how to process that command.",
            'unknown_intent': "I don't know how to perform that action.",
            'missing_parameters': "Your command is missing required information."
        }

        return error_responses.get(error_type, "I encountered an error processing your command.")
```

## Hands-on Exercise

Create a complete voice interface for your robot that:
1. Implements Whisper-based speech recognition
2. Uses Voice Activity Detection to reduce processing load
3. Integrates with your robot's command system
4. Provides appropriate feedback to the user
5. Handles errors and ambiguous commands gracefully

This exercise will help you create a natural, responsive voice interface for your humanoid robot.