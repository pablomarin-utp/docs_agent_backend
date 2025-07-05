import pytest
from unittest.mock import Mock, patch, MagicMock
from app.chat.chatbot import initialize_agent_workflow, process_user_message
from app.schemas.chat_schema import AgentState, ChatMessage
from uuid import uuid4

class TestChatbot:
    
    def test_initialize_agent_workflow(self):
        """Test that agent workflow initializes correctly."""
        graph, config = initialize_agent_workflow()
        
        assert graph is not None
        assert config is not None
        assert "configurable" in config
        assert "thread_id" in config["configurable"]
    
    @patch('app.chat.chatbot.llm_model')
    @patch('app.chat.chatbot.rag_tool')
    def test_process_user_message_success(self, mock_rag_tool, mock_llm_model):
        """Test successful message processing."""
        # Setup mocks
        mock_response = Mock()
        mock_response.content = "Test response"
        mock_llm_model.invoke.return_value = mock_response
        
        # Create test data
        user_id = str(uuid4())
        user_input = [("user", "What is the weather?")]
        
        # Initialize workflow
        graph, config = initialize_agent_workflow()
        
        # Process message
        result = process_user_message(user_id, user_input, graph, config)
        
        # Assertions
        assert isinstance(result, str)
        assert len(result) > 0
    
    def test_agent_state_creation(self):
        """Test AgentState schema validation."""
        user_id = str(uuid4())
        messages = [
            ChatMessage(role="user", content="Hello"),
            ChatMessage(role="assistant", content="Hi there!")
        ]
        
        state = AgentState(
            user_id=user_id,
            messages=messages,
            summary="Test conversation"
        )
        
        assert state.user_id == user_id
        assert len(state.messages) == 2
        assert state.summary == "Test conversation"
    
    def test_chat_message_creation(self):
        """Test ChatMessage schema validation."""
        message = ChatMessage(role="user", content="Test message")
        
        assert message.role == "user"
        assert message.content == "Test message"
    
    def test_chat_message_langgraph_format(self):
        """Test ChatMessage conversion to LangGraph format."""
        message = ChatMessage(role="assistant", content="Test response")
        langgraph_format = message.to_langgraph_format()
        
        assert langgraph_format == {"role": "assistant", "content": "Test response"}
    
    def test_chat_message_from_langgraph_format(self):
        """Test ChatMessage creation from LangGraph format."""
        langgraph_msg = {"role": "user", "content": "Test input"}
        message = ChatMessage.from_langgraph_format(langgraph_msg)
        
        assert message.role == "user"
        assert message.content == "Test input"
    
    @patch('app.chat.chatbot.logger')
    def test_process_user_message_error_handling(self, mock_logger):
        """Test error handling in message processing."""
        user_id = str(uuid4())
        user_input = [("user", "Test message")]
        
        # Create a mock graph that raises an exception
        mock_graph = Mock()
        mock_graph.invoke.side_effect = Exception("Test error")
        
        config = {"configurable": {"thread_id": 1}}
        
        # Should raise the exception
        with pytest.raises(Exception):
            process_user_message(user_id, user_input, mock_graph, config)
        
        # Verify error was logged
        mock_logger.error.assert_called()
    
    def test_invalid_chat_message_role(self):
        """Test ChatMessage with invalid role."""
        with pytest.raises(ValueError):
            ChatMessage(role="invalid_role", content="Test")
    
    def test_empty_message_content(self):
        """Test ChatMessage with empty content."""
        message = ChatMessage(role="user", content="")
        assert message.content == ""
        assert message.role == "user"
