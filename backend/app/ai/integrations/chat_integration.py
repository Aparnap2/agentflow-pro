"""
Chat Integration Module

Provides chat platform integration for real-time customer support.
"""

import logging
import asyncio
from typing import Dict, List, Optional, Any, Union
from enum import Enum
from pydantic import BaseModel, Field, validator
import json
from datetime import datetime

logger = logging.getLogger(__name__)

class ChatPlatform(str, Enum):
    """Supported chat platforms."""
    SLACK = "slack"
    DISCORD = "discord"
    TEAMS = "teams"
    WHATSAPP = "whatsapp"
    CUSTOM = "custom"

class MessageType(str, Enum):
    """Types of chat messages."""
    TEXT = "text"
    IMAGE = "image"
    FILE = "file"
    CARD = "card"
    BUTTON = "button"
    MENU = "menu"
    TYPING = "typing"
    READ_RECEIPT = "read_receipt"

class MessageStatus(str, Enum):
    """Status of a chat message."""
    SENT = "sent"
    DELIVERED = "delivered"
    READ = "read"
    FAILED = "failed"

class ChatUser(BaseModel):
    """Represents a user in the chat system."""
    id: str
    name: str
    email: Optional[str] = None
    avatar_url: Optional[str] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)
    is_bot: bool = False
    is_online: bool = False
    last_seen: Optional[datetime] = None

class ChatMessage(BaseModel):
    """Represents a chat message."""
    message_id: str
    conversation_id: str
    sender: ChatUser
    recipient: ChatUser
    message_type: MessageType = MessageType.TEXT
    content: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    status: MessageStatus = MessageStatus.SENT
    metadata: Dict[str, Any] = Field(default_factory=dict)
    buttons: Optional[List[Dict[str, Any]]] = None
    quick_replies: Optional[List[Dict[str, Any]]] = None

class ChatConversation(BaseModel):
    """Represents a chat conversation."""
    conversation_id: str
    participants: List[ChatUser]
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    metadata: Dict[str, Any] = Field(default_factory=dict)
    is_active: bool = True
    tags: List[str] = Field(default_factory=list)

class ChatIntegrationConfig(BaseModel):
    """Configuration for chat integration."""
    platform: ChatPlatform
    api_key: str
    api_secret: Optional[str] = None
    base_url: Optional[str] = None
    webhook_url: Optional[str] = None
    default_channel: Optional[str] = None
    timeout: int = 30
    max_retries: int = 3
    rate_limit: int = 100  # messages per minute

class ChatIntegration:
    """
    Handles integration with various chat platforms.
    
    This class provides a unified interface for sending and receiving
    messages across different chat platforms.
    """
    
    def __init__(self, config: Union[Dict[str, Any], ChatIntegrationConfig]):
        """
        Initialize the chat integration.
        
        Args:
            config: Configuration as a dict or ChatIntegrationConfig
        """
        if isinstance(config, dict):
            self.config = ChatIntegrationConfig(**config)
        else:
            self.config = config
            
        self._client = None
        self._message_queue = asyncio.Queue()
        self._is_processing = False
        self._message_handlers = []
        
        self._initialize_client()
    
    def _initialize_client(self) -> None:
        """Initialize the chat platform client."""
        try:
            if self.config.platform == ChatPlatform.SLACK:
                from slack_sdk import WebClient
                from slack_sdk.errors import SlackApiError
                
                self._client = WebClient(
                    token=self.config.api_key,
                    timeout=self.config.timeout
                )
                
            elif self.config.platform == ChatPlatform.DISCORD:
                import discord
                
                intents = discord.Intents.default()
                intents.messages = True
                intents.message_content = True
                
                self._client = discord.Client(intents=intents)
                
                # Register message handler
                @self._client.event
                async def on_message(message):
                    if message.author == self._client.user:
                        return
                        
                    chat_message = self._convert_discord_message(message)
                    await self._handle_incoming_message(chat_message)
            
            logger.info(f"Initialized {self.config.platform.value} chat client")
            
        except ImportError as e:
            logger.error(f"Failed to import required package for {self.config.platform.value}: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"Failed to initialize chat client: {str(e)}")
            raise
    
    async def start(self) -> None:
        """Start the chat client."""
        if not self._client:
            raise RuntimeError("Chat client not initialized")
            
        if self.config.platform == ChatPlatform.DISCORD and not self._client.is_ready():
            await self._client.start(self.config.api_key)
        
        self._is_processing = True
        asyncio.create_task(self._process_message_queue())
        logger.info("Chat client started")
    
    async def stop(self) -> None:
        """Stop the chat client."""
        self._is_processing = False
        
        if self._client:
            if self.config.platform == ChatPlatform.DISCORD:
                await self._client.close()
            
            logger.info("Chat client stopped")
    
    def register_message_handler(self, handler):
        """
        Register a message handler.
        
        Args:
            handler: Async function that takes a ChatMessage
        """
        self._message_handlers.append(handler)
        return handler
    
    async def _handle_incoming_message(self, message: ChatMessage) -> None:
        """
        Handle an incoming chat message.
        
        Args:
            message: Incoming chat message
        """
        try:
            # Call all registered handlers
            for handler in self._message_handlers:
                try:
                    await handler(message)
                except Exception as e:
                    logger.error(f"Error in message handler: {str(e)}", exc_info=True)
                    
        except Exception as e:
            logger.error(f"Failed to handle incoming message: {str(e)}", exc_info=True)
    
    async def _process_message_queue(self) -> None:
        """Process messages from the queue."""
        while self._is_processing:
            try:
                message = await self._message_queue.get()
                await self._send_message_internal(message)
                self._message_queue.task_done()
            except Exception as e:
                logger.error(f"Error processing message: {str(e)}", exc_info=True)
    
    async def send_message(self, message: Union[Dict[str, Any], ChatMessage]) -> bool:
        """
        Send a chat message.
        
        Args:
            message: Message to send (dict or ChatMessage)
            
        Returns:
            bool: True if message was queued successfully
        """
        try:
            if not isinstance(message, ChatMessage):
                message = ChatMessage(**message)
                
            await self._message_queue.put(message)
            return True
            
        except Exception as e:
            logger.error(f"Failed to queue message: {str(e)}")
            return False
    
    async def _send_message_internal(self, message: ChatMessage) -> bool:
        """
        Internal method to send a message to the chat platform.
        
        Args:
            message: Message to send
            
        Returns:
            bool: True if message was sent successfully
        """
        try:
            if self.config.platform == ChatPlatform.SLACK:
                return await self._send_slack_message(message)
            elif self.config.platform == ChatPlatform.DISCORD:
                return await self._send_discord_message(message)
            else:
                logger.warning(f"Unsupported platform: {self.config.platform}")
                return False
                
        except Exception as e:
            logger.error(f"Failed to send message: {str(e)}", exc_info=True)
            return False
    
    async def _send_slack_message(self, message: ChatMessage) -> bool:
        """Send a message via Slack."""
        try:
            blocks = []
            
            # Add main text
            if message.content:
                blocks.append({
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": message.content
                    }
                })
            
            # Add buttons if present
            if message.buttons:
                actions = []
                for btn in message.buttons:
                    actions.append({
                        "type": "button",
                        "text": {
                            "type": "plain_text",
                            "text": btn.get("text", "Button")
                        },
                        "value": btn.get("value", ""),
                        "action_id": btn.get("action_id", "button_click")
                    })
                
                blocks.append({
                    "type": "actions",
                    "elements": actions
                })
            
            # Send the message
            response = self._client.chat_postMessage(
                channel=message.recipient.id,
                text=message.content,
                blocks=blocks if blocks else None,
                metadata=message.metadata
            )
            
            return response["ok"]
            
        except Exception as e:
            logger.error(f"Failed to send Slack message: {str(e)}")
            return False
    
    async def _send_discord_message(self, message: ChatMessage) -> bool:
        """Send a message via Discord."""
        try:
            channel = self._client.get_channel(int(message.recipient.id))
            if not channel:
                logger.error(f"Channel not found: {message.recipient.id}")
                return False
            
            # Send the message
            await channel.send(message.content)
            
            # TODO: Handle buttons and other rich content
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to send Discord message: {str(e)}")
            return False
    
    def _convert_discord_message(self, message) -> ChatMessage:
        """Convert a Discord message to ChatMessage."""
        return ChatMessage(
            message_id=str(message.id),
            conversation_id=str(message.channel.id),
            sender=ChatUser(
                id=str(message.author.id),
                name=message.author.name,
                is_bot=message.author.bot
            ),
            recipient=ChatUser(
                id=str(self._client.user.id),
                name=self._client.user.name,
                is_bot=True
            ),
            content=message.content,
            timestamp=message.created_at,
            metadata={
                "guild_id": str(getattr(message.guild, "id", None)),
                "channel_id": str(message.channel.id),
                "author_id": str(message.author.id)
            }
        )
    
    async def get_conversation_history(self, conversation_id: str, limit: int = 50) -> List[ChatMessage]:
        """
        Get conversation history.
        
        Args:
            conversation_id: ID of the conversation
            limit: Maximum number of messages to return
            
        Returns:
            List of chat messages
        """
        try:
            if self.config.platform == ChatPlatform.SLACK:
                response = self._client.conversations_history(
                    channel=conversation_id,
                    limit=limit
                )
                
                messages = []
                for msg in response.get("messages", []):
                    messages.append(ChatMessage(
                        message_id=msg["ts"],
                        conversation_id=conversation_id,
                        sender=ChatUser(
                            id=msg.get("user", ""),
                            name=msg.get("username", "Unknown User")
                        ),
                        recipient=ChatUser(
                            id=self._client.auth_test()["user_id"],
                            name=self._client.auth_test()["user"]
                        ),
                        content=msg.get("text", ""),
                        timestamp=datetime.fromtimestamp(float(msg["ts"])),
                        metadata=msg
                    ))
                
                return messages
                
            elif self.config.platform == ChatPlatform.DISCORD:
                # Discord implementation would go here
                pass
                
            return []
            
        except Exception as e:
            logger.error(f"Failed to get conversation history: {str(e)}")
            return []
    
    async def update_message(self, message_id: str, content: str) -> bool:
        """
        Update an existing message.
        
        Args:
            message_id: ID of the message to update
            content: New content
            
        Returns:
            bool: True if update was successful
        """
        try:
            if self.config.platform == ChatPlatform.SLACK:
                response = self._client.chat_update(
                    ts=message_id,
                    channel=self.config.default_channel,
                    text=content
                )
                return response["ok"]
                
            elif self.config.platform == ChatPlatform.DISCORD:
                # Discord implementation would go here
                pass
                
            return False
            
        except Exception as e:
            logger.error(f"Failed to update message: {str(e)}")
            return False

# Example usage
if __name__ == "__main__":
    import asyncio
    from dotenv import load_dotenv
    import os
    
    load_dotenv()
    
    async def test_chat():
        # Example configuration
        config = {
            "platform": "slack",  # or "discord"
            "api_key": os.getenv("SLACK_BOT_TOKEN"),
            "default_channel": "#general"
        }
        
        chat = ChatIntegration(config)
        
        # Register a message handler
        @chat.register_message_handler
        async def handle_message(message: ChatMessage):
            print(f"Received message from {message.sender.name}: {message.content}")
            
            # Echo the message back
            response = ChatMessage(
                message_id=f"resp_{message.message_id}",
                conversation_id=message.conversation_id,
                sender=message.recipient,  # Bot is the sender now
                recipient=message.sender,  # Original sender is now recipient
                content=f"You said: {message.content}",
                buttons=[
                    {"text": "Option 1", "value": "option1"},
                    {"text": "Option 2", "value": "option2"}
                ]
            )
            
            await chat.send_message(response)
        
        try:
            # Start the chat client
            await chat.start()
            
            # Keep the client running
            while True:
                await asyncio.sleep(1)
                
        except KeyboardInterrupt:
            print("Shutting down...")
            await chat.stop()
    
    asyncio.run(test_chat())
