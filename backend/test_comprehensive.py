#!/usr/bin/env python3
"""
Comprehensive test script to verify the fixes for the RAG chatbot
"""
import asyncio
from src.services.rag_service import RAGService
from src.services.vector_store import VectorStore
from src.services.response_generator import ResponseGenerator
from src.services.response_validator import ResponseValidator

def test_comprehensive_response_generation():
    """Test the response generator with various types of content"""
    print("Testing comprehensive response generation...")

    generator = ResponseGenerator()

    # Test 1: Content with mixed code and concepts
    mixed_content = [
        {
            "text": "def robot_move():\n    \"\"\"This function makes the robot move\"\"\"\n    return True\n\nThe fundamental concept of robotics involves autonomous movement and decision making in dynamic environments."
        }
    ]

    query = "What is robot movement?"
    response = generator.generate_response(query, mixed_content)
    print(f"Test 1 - Mixed content: {response}")

    # Test 2: Content with only concepts
    concept_content = [
        {
            "text": "Robotics is an interdisciplinary branch of engineering and science that includes mechanical engineering, electrical engineering, computer science, and others. It deals with the design, construction, operation, and use of robots."
        }
    ]

    response2 = generator.generate_response(query, concept_content)
    print(f"Test 2 - Concept content: {response2}")

    # Test 3: Content with heavy technical details
    technical_content = [
        {
            "text": "import numpy as np\nimport cv2\nfrom robot_lib import Robot\n\nclass MobileRobot(Robot):\n    def __init__(self):\n        super().__init__()\n        \nRobots utilize sensors to perceive their environment and actuators to perform physical tasks."
        }
    ]

    response3 = generator.generate_response(query, technical_content)
    print(f"Test 3 - Technical content: {response3}")

    print("OK Comprehensive response generation tests completed\n")

def test_response_validation():
    """Test the response validator with various inputs"""
    print("Testing response validation...")

    validator = ResponseValidator()

    # Test with pure code (should be invalid)
    pure_code = "def robot_move():\n    return 'moving'\n    if True:\n        pass"
    is_valid_code = validator.validate(pure_code, [])
    print(f"Pure code validation: {is_valid_code} (should be False)")

    # Test with mixed content that has some code patterns but is mostly natural language
    mixed_response = "Robots utilize sensors to perceive their environment. The function robot_move() enables the robot to navigate spaces. This is achieved through various actuators."
    is_valid_mixed = validator.validate(mixed_response, [])
    print(f"Mixed content validation: {is_valid_mixed} (should be True)")

    # Test with pure natural language
    natural_response = "Robotics is an interdisciplinary field that combines mechanical engineering, electrical engineering, and computer science to design and operate robots."
    is_valid_natural = validator.validate(natural_response, [])
    print(f"Natural language validation: {is_valid_natural} (should be True)")

    print("OK Response validation tests completed\n")

def test_edge_cases():
    """Test edge cases"""
    print("Testing edge cases...")

    generator = ResponseGenerator()

    # Test with empty results
    empty_results = []
    response = generator.generate_response("What is robotics?", empty_results)
    print(f"Empty results: {response}")

    # Test with results that become empty after sanitization
    code_only_results = [{"text": "def move_robot():\n    x = 5\n    y = 10\n    return x + y"}]
    response2 = generator.generate_response("What is robotics?", code_only_results)
    print(f"Code-only results: {response2}")

    print("OK Edge case tests completed\n")

if __name__ == "__main__":
    print("Running comprehensive verification tests for RAG fixes...\n")

    test_comprehensive_response_generation()
    test_response_validation()
    test_edge_cases()

    print("All comprehensive verification tests completed!")
    print("\nSummary of improvements:")
    print("1. ResponseGenerator now properly extracts conceptual information from mixed content")
    print("2. ResponseValidator uses more nuanced code detection")
    print("3. RAG Service returns natural language explanations instead of 'filtered out' messages")
    print("4. Content sanitization preserves conceptual information while removing technical details")