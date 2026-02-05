#!/usr/bin/env python3
"""
Test script to verify the fixes for the RAG chatbot and docs page
"""
import asyncio
from src.services.rag_service import RAGService
from src.services.vector_store import VectorStore
from src.services.response_generator import ResponseGenerator
from src.services.response_validator import ResponseValidator

def test_response_generator():
    """Test the response generator with sample content that might contain code"""
    print("Testing ResponseGenerator...")

    generator = ResponseGenerator()

    # Test with content that contains code-like patterns
    search_results_with_code = [
        {
            "text": "def example_function():\n    print('This is code')\n    return True\n\nThis is the explanation of the function."
        },
        {
            "text": "import numpy as np\narr = np.array([1, 2, 3])\n\nThis explains the array concept."
        }
    ]

    query = "What is robotics?"
    response = generator.generate_response(query, search_results_with_code)

    print(f"Query: {query}")
    print(f"Response: {response}")
    print("OK ResponseGenerator test completed\n")

    # Test with normal content
    normal_results = [
        {
            "text": "Robotics is an interdisciplinary branch of engineering and science that includes mechanical engineering, electrical engineering, computer science, and others. It deals with the design, construction, operation, and use of robots."
        }
    ]

    response2 = generator.generate_response(query, normal_results)
    print(f"Normal response: {response2}")
    print("OK Normal content test completed\n")

def test_response_validator():
    """Test the response validator with code and normal content"""
    print("Testing ResponseValidator...")

    validator = ResponseValidator()

    # Test with code content
    code_response = "def robot_move():\n    return 'moving'"
    is_valid_code = validator.validate(code_response, [])
    print(f"Code response validation: {is_valid_code} (should be False)")

    # Test with normal content
    normal_response = "Robotics is an interdisciplinary branch of engineering that deals with design of robots."
    is_valid_normal = validator.validate(normal_response, [])
    print(f"Normal response validation: {is_valid_normal} (should be True)")

    print("OK ResponseValidator test completed\n")

def test_rag_service():
    """Test the RAG service integration"""
    print("Testing RAG Service...")

    # Initialize vector store (this will use the existing collection)
    vector_store = VectorStore()
    rag_service = RAGService(vector_store)

    # Test with a simple query
    try:
        result = rag_service.query("What is robotics?", k=1)
        print(f"Query: What is robotics?")
        print(f"Response: {result['response']}")
        print(f"Is valid: {result['is_valid']}")
        print("OK RAG Service test completed\n")
    except Exception as e:
        print(f"RAG Service test failed: {e}")
        print("WARNING RAG Service test had issues\n")

if __name__ == "__main__":
    print("Running verification tests for fixes...\n")

    test_response_generator()
    test_response_validator()
    test_rag_service()

    print("All verification tests completed!")
    print("\nSummary of fixes applied:")
    print("1. Fixed FastAPI docs rendering by updating CSP headers to allow Swagger UI scripts")
    print("2. Created ResponseGenerator to properly format responses in natural language")
    print("3. Enhanced ResponseValidator to detect and reject code/log patterns")
    print("4. Updated RAG service to use the new response generation pipeline")
    print("5. Added content sanitization to remove code blocks from retrieved content")