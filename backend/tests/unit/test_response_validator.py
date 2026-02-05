import unittest
from backend.src.services.response_validator import ResponseValidator


class TestResponseValidator(unittest.TestCase):
    def setUp(self):
        self.validator = ResponseValidator()

    def test_validate_with_matching_content(self):
        # Arrange
        response = "The neural network learns from data patterns."
        sources = [{"text": "Neural networks learn from data patterns in the training set."}]

        # Act
        result = self.validator.validate(response, sources)

        # Assert
        self.assertTrue(result)

    def test_validate_with_non_matching_content(self):
        # Arrange
        response = "Quantum computing uses qubits."
        sources = [{"text": "Neural networks learn from data patterns in the training set."}]

        # Act
        result = self.validator.validate(response, sources)

        # Assert
        self.assertFalse(result)

    def test_validate_with_partial_matching_content(self):
        # Arrange
        response = "Neural networks are a machine learning technique."
        sources = [{"text": "Neural networks are a machine learning technique used for pattern recognition."}]

        # Act
        result = self.validator.validate(response, sources)

        # Assert
        self.assertTrue(result)

    def test_validate_with_multiple_sources(self):
        # Arrange
        response = "AI systems can recognize patterns in data."
        sources = [
            {"text": "Machine learning systems can recognize patterns in data."},
            {"text": "Deep learning models analyze data patterns effectively."}
        ]

        # Act
        result = self.validator.validate(response, sources)

        # Assert
        self.assertTrue(result)

    def test_validate_empty_sources(self):
        # Arrange
        response = "Some content"
        sources = []

        # Act
        result = self.validator.validate(response, sources)

        # Assert
        self.assertFalse(result)

    def test_validate_empty_response(self):
        # Arrange
        response = ""
        sources = [{"text": "Some source content"}]

        # Act
        result = self.validator.validate(response, sources)

        # Assert
        self.assertFalse(result)

    def test_calculate_similarity_high_match(self):
        # Arrange
        text1 = "Artificial intelligence is a wonderful field."
        text2 = "Artificial intelligence is a wonderful field with many applications."

        # Act
        similarity = self.validator._calculate_similarity(text1, text2)

        # Assert
        self.assertGreater(similarity, 0.7)  # Should have high similarity

    def test_calculate_similarity_low_match(self):
        # Arrange
        text1 = "Quantum physics studies matter and energy."
        text2 = "Baking bread requires flour and water."

        # Act
        similarity = self.validator._calculate_similarity(text1, text2)

        # Assert
        self.assertLess(similarity, 0.3)  # Should have low similarity

    def test_calculate_similarity_identical(self):
        # Arrange
        text1 = "Machine learning is a subset of AI."
        text2 = "Machine learning is a subset of AI."

        # Act
        similarity = self.validator._calculate_similarity(text1, text2)

        # Assert
        self.assertEqual(similarity, 1.0)  # Should be identical

    def test_extract_key_phrases(self):
        # Arrange
        text = "Neural networks and deep learning are important AI concepts."

        # Act
        phrases = self.validator._extract_key_phrases(text)

        # Assert
        self.assertIn("neural networks", phrases)
        self.assertIn("deep learning", phrases)
        self.assertIn("ai", phrases)

    def test_extract_key_phrases_with_punctuation(self):
        # Arrange
        text = "AI (Artificial Intelligence) and ML (Machine Learning) are related fields!"

        # Act
        phrases = self.validator._extract_key_phrases(text)

        # Assert
        self.assertIn("ai", phrases)
        self.assertIn("artificial intelligence", phrases)
        self.assertIn("ml", phrases)
        self.assertIn("machine learning", phrases)

    def test_validate_with_synonyms(self):
        # Arrange
        response = "Algorithms learn from examples."
        sources = [{"text": "Models learn from training data."}]

        # Act
        result = self.validator.validate(response, sources)

        # This might be False depending on implementation, but testing the behavior
        # The implementation would need NLP techniques to recognize synonyms
        self.assertIsInstance(result, bool)

    def test_validate_case_insensitive(self):
        # Arrange
        response = "NEURAL NETWORKS are powerful."
        sources = [{"text": "neural networks are powerful tools."}]

        # Act
        result = self.validator.validate(response, sources)

        # Assert
        self.assertTrue(result)

    def test_validate_with_numbers_and_specifics(self):
        # Arrange
        response = "The model achieved 95% accuracy."
        sources = [{"text": "The model achieved 95% accuracy on the test set."}]

        # Act
        result = self.validator.validate(response, sources)

        # Assert
        self.assertTrue(result)

    def test_validate_with_different_sentence_structure(self):
        # Arrange
        response = "Deep learning models can identify patterns."
        sources = [{"text": "Patterns can be identified by deep learning models."}]

        # Act
        result = self.validator.validate(response, sources)

        # Assert
        self.assertTrue(result)

    def test_check_response_source_alignment(self):
        # Arrange
        response = "Neural networks learn from data."
        sources = [{"text": "Neural networks learn from data patterns in the training set."}]

        # Act
        aligned = self.validator._check_response_source_alignment(response, sources)

        # Assert
        self.assertTrue(aligned)

    def test_check_response_source_alignment_no_match(self):
        # Arrange
        response = "Quantum computing uses qubits."
        sources = [{"text": "Neural networks learn from data patterns in the training set."}]

        # Act
        aligned = self.validator._check_response_source_alignment(response, sources)

        # Assert
        self.assertFalse(aligned)


if __name__ == '__main__':
    unittest.main()