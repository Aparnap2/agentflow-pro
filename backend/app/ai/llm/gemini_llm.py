import os
from typing import Dict, Any, Optional, List
import google.generativeai as genai
from .base_llm import BaseLLM, LLMResponse, GenerationConfig
import logging

logger = logging.getLogger(__name__)

class GeminiLLM(BaseLLM):
    """Google Gemini LLM implementation."""
    
    SUPPORTED_MODELS = {
        'gemini-pro': {
            'model': 'gemini-pro',
            'max_output_tokens': 30720,
            'temperature': 0.7,
            'top_p': 1.0,
            'top_k': 40
        },
        'gemini-1.5-pro': {
            'model': 'gemini-1.5-pro',
            'max_output_tokens': 1048576,
            'temperature': 0.7,
            'top_p': 1.0,
            'top_k': 40
        }
    }
    
    def __init__(self, model_name: str, api_key: Optional[str] = None, **kwargs):
        """Initialize the Gemini LLM.
        
        Args:
            model_name: Name of the Gemini model to use
            api_key: Google AI API key. If not provided, will use GOOGLE_API_KEY env var
            **kwargs: Additional model parameters
        """
        if model_name not in self.SUPPORTED_MODELS:
            raise ValueError(f"Unsupported model: {model_name}. Supported models: {list(self.SUPPORTED_MODELS.keys())}")
            
        self.model_config = self.SUPPORTED_MODELS[model_name].copy()
        self.model_config.update(kwargs)
        
        # Initialize the client with the API key
        self.api_key = api_key or os.getenv('GOOGLE_API_KEY')
        if not self.api_key:
            raise ValueError("Google API key is required. Set GOOGLE_API_KEY environment variable or pass api_key parameter.")
            
        super().__init__(model_name, self.model_config)
    
    def initialize_client(self) -> Any:
        """Initialize the Gemini client."""
        try:
            genai.configure(api_key=self.api_key)
            return genai
        except Exception as e:
            logger.error(f"Failed to initialize Gemini client: {str(e)}")
            raise
    
    async def generate(
        self,
        prompt: str,
        config: Optional[GenerationConfig] = None
    ) -> LLMResponse:
        """Generate text from the given prompt."""
        try:
            # Get generation config with defaults
            gen_config = self._get_generation_config(config)
            
            # Create the model instance
            model = genai.GenerativeModel(self.model_name)
            
            # Generate content
            response = await model.generate_content_async(
                prompt,
                generation_config={
                    'temperature': gen_config['temperature'],
                    'top_p': gen_config['top_p'],
                    'top_k': gen_config['top_k'],
                    'max_output_tokens': gen_config['max_tokens'],
                    'stop_sequences': gen_config.get('stop_sequences')
                }
            )
            
            # Extract the generated text
            generated_text = response.text if hasattr(response, 'text') else ""
            
            # Calculate token usage (approximate)
            prompt_tokens = len(prompt.split())  # Rough estimate
            completion_tokens = len(generated_text.split())  # Rough estimate
            
            return LLMResponse(
                text=generated_text,
                model=self.model_name,
                usage={
                    'prompt_tokens': prompt_tokens,
                    'completion_tokens': completion_tokens,
                    'total_tokens': prompt_tokens + completion_tokens
                },
                metadata={
                    'model': self.model_name,
                    'finish_reason': getattr(response, 'finish_reason', None)
                }
            )
            
        except Exception as e:
            logger.error(f"Error in Gemini generation: {str(e)}", exc_info=True)
            raise
    
    async def chat(
        self,
        messages: List[Dict[str, str]],
        config: Optional[GenerationConfig] = None
    ) -> LLMResponse:
        """Generate a chat completion."""
        try:
            # Get generation config with defaults
            gen_config = self._get_generation_config(config)
            
            # Create the chat model
            model = genai.GenerativeModel(self.model_name)
            chat = model.start_chat(history=[])
            
            # Convert messages to Gemini format
            history = []
            for msg in messages:
                role = 'user' if msg['role'] == 'user' else 'model'
                history.append({'role': role, 'parts': [msg['content']]})
            
            # Get the last user message
            if not history or history[-1]['role'] != 'user':
                raise ValueError("Last message must be from user")
                
            user_message = history.pop()
            
            # Generate response
            response = await chat.send_message_async(
                user_message['parts'][0],
                generation_config={
                    'temperature': gen_config['temperature'],
                    'top_p': gen_config['top_p'],
                    'top_k': gen_config['top_k'],
                    'max_output_tokens': gen_config['max_tokens'],
                    'stop_sequences': gen_config.get('stop_sequences')
                },
                stream=False
            )
            
            # Extract the generated text
            generated_text = response.text if hasattr(response, 'text') else ""
            
            # Calculate token usage (approximate)
            prompt_tokens = sum(len(msg['parts'][0].split()) for msg in history + [user_message])
            completion_tokens = len(generated_text.split())
            
            return LLMResponse(
                text=generated_text,
                model=self.model_name,
                usage={
                    'prompt_tokens': prompt_tokens,
                    'completion_tokens': completion_tokens,
                    'total_tokens': prompt_tokens + completion_tokens
                },
                metadata={
                    'model': self.model_name,
                    'finish_reason': getattr(response, 'finish_reason', None)
                }
            )
            
        except Exception as e:
            logger.error(f"Error in Gemini chat: {str(e)}", exc_info=True)
            raise
