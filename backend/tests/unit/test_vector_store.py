import unittest
from unittest.mock import Mock, patch, MagicMock
from backend.src.services.vector_store import VectorStore


class TestVectorStore(unittest.TestCase):
    def setUp(self):
        with patch('backend.src.services.vector_store.QdrantClient'):
            self.vector_store = VectorStore()

    @patch('backend.src.services.vector_store.QdrantClient')
    def test_initialization(self, mock_qdrant_client):
        # Arrange
        mock_client_instance = Mock()
        mock_qdrant_client.return_value = mock_client_instance

        # Act
        vector_store = VectorStore()

        # Assert
        mock_qdrant_client.assert_called_once()
        self.assertIsNotNone(vector_store.client)

    @patch('backend.src.services.vector_store.QdrantClient')
    def test_similarity_search(self, mock_qdrant_client):
        # Arrange
        mock_client_instance = Mock()
        mock_qdrant_client.return_value = mock_client_instance

        # Mock the search response
        mock_search_result = [
            Mock(id="1", payload={"text": "test content", "metadata": {}}, score=0.9)
        ]
        mock_client_instance.search.return_value = mock_search_result

        vector_store = VectorStore()

        # Act
        results = vector_store.similarity_search("test query", k=1)

        # Assert
        mock_client_instance.search.assert_called_once()
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]["text"], "test content")

    @patch('backend.src.services.vector_store.QdrantClient')
    def test_add_texts(self, mock_qdrant_client):
        # Arrange
        mock_client_instance = Mock()
        mock_qdrant_client.return_value = mock_client_instance

        vector_store = VectorStore()

        # Act
        texts = ["text1", "text2"]
        result = vector_store.add_texts(texts)

        # Assert
        mock_client_instance.upsert.assert_called_once()
        self.assertIsInstance(result, list)
        self.assertEqual(len(result), 2)

    @patch('backend.src.services.vector_store.QdrantClient')
    def test_create_collection(self, mock_qdrant_client):
        # Arrange
        mock_client_instance = Mock()
        mock_qdrant_client.return_value = mock_client_instance

        vector_store = VectorStore()

        # Act
        vector_store.create_collection("test_collection", 1536)

        # Assert
        mock_client_instance.recreate_collection.assert_called_once()

    @patch('backend.src.services.vector_store.QdrantClient')
    def test_delete_collection(self, mock_qdrant_client):
        # Arrange
        mock_client_instance = Mock()
        mock_qdrant_client.return_value = mock_client_instance

        vector_store = VectorStore()

        # Act
        vector_store.delete_collection("test_collection")

        # Assert
        mock_client_instance.delete_collection.assert_called_once_with("test_collection")

    @patch('backend.src.services.vector_store.QdrantClient')
    def test_get_collection_info(self, mock_qdrant_client):
        # Arrange
        mock_client_instance = Mock()
        mock_qdrant_client.return_value = mock_client_instance

        # Mock the collection info response
        mock_collection_info = Mock()
        mock_client_instance.get_collection.return_value = mock_collection_info

        vector_store = VectorStore()

        # Act
        info = vector_store.get_collection_info("test_collection")

        # Assert
        mock_client_instance.get_collection.assert_called_once_with("test_collection")
        self.assertEqual(info, mock_collection_info)

    @patch('backend.src.services.vector_store.QdrantClient')
    def test_count_vectors(self, mock_qdrant_client):
        # Arrange
        mock_client_instance = Mock()
        mock_qdrant_client.return_value = mock_client_instance

        # Mock the collection info response with count
        mock_collection_info = Mock()
        mock_collection_info.vectors_count = 100
        mock_client_instance.get_collection.return_value = mock_collection_info

        vector_store = VectorStore()

        # Act
        count = vector_store.count_vectors("test_collection")

        # Assert
        self.assertEqual(count, 100)

    @patch('backend.src.services.vector_store.QdrantClient')
    def test_search_with_filters(self, mock_qdrant_client):
        # Arrange
        mock_client_instance = Mock()
        mock_qdrant_client.return_value = mock_client_instance

        # Mock the search response
        mock_search_result = [
            Mock(id="1", payload={"text": "filtered content", "metadata": {"category": "AI"}}, score=0.8)
        ]
        mock_client_instance.search.return_value = mock_search_result

        vector_store = VectorStore()

        # Act
        results = vector_store.search_with_filters("query", filters={"category": "AI"}, k=1)

        # Assert
        mock_client_instance.search.assert_called_once()
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]["text"], "filtered content")

    @patch('backend.src.services.vector_store.QdrantClient')
    def test_get_all_documents(self, mock_qdrant_client):
        # Arrange
        mock_client_instance = Mock()
        mock_qdrant_client.return_value = mock_client_instance

        # Mock the scroll response
        mock_scroll_result = [
            [Mock(id="1", payload={"text": "doc1", "metadata": {}})],
            []  # Empty list to indicate end of scroll
        ]
        mock_client_instance.scroll.return_value = iter(mock_scroll_result)

        vector_store = VectorStore()

        # Act
        docs = vector_store.get_all_documents()

        # Assert
        mock_client_instance.scroll.assert_called_once()
        self.assertEqual(len(docs), 1)
        self.assertEqual(docs[0]["text"], "doc1")

    @patch('backend.src.services.vector_store.QdrantClient')
    def test_delete_by_payload_filter(self, mock_qdrant_client):
        # Arrange
        mock_client_instance = Mock()
        mock_qdrant_client.return_value = mock_client_instance

        vector_store = VectorStore()

        # Act
        vector_store.delete_by_payload_filter("test_collection", {"category": "old"})

        # Assert
        mock_client_instance.delete.assert_called_once()

    @patch('backend.src.services.vector_store.QdrantClient')
    def test_update_payload(self, mock_qdrant_client):
        # Arrange
        mock_client_instance = Mock()
        mock_qdrant_client.return_value = mock_client_instance

        vector_store = VectorStore()

        # Act
        vector_store.update_payload("test_collection", {"new_field": "new_value"}, ["1", "2"])

        # Assert
        mock_client_instance.set_payload.assert_called_once()


if __name__ == '__main__':
    unittest.main()