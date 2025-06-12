"""
Example script demonstrating how to use the OpenRouter integration in AgentFlow Pro.

This script shows how to:
1. Initialize the OpenRouter client
2. Generate text using different models
3. Handle streaming responses
4. Use the predefined model configurations
"""

import asyncio
import os
from dotenv import load_dotenv
from typing import List, Dict, Any, Optional, AsyncGenerator

# Load environment variables from .env file
load_dotenv()

# Import the OpenRouter client
from app.ai.llm import OpenRouterLLM, get_predefined_model_config

async def generate_text(
    prompt: str,
    model_name: str = "deepseek-ai/deepseek-chat",
    temperature: float = 0.7,
    max_tokens: int = 1024,
    stream: bool = False
) -> None:
    """Generate text using the specified OpenRouter model.
    
    Args:
        prompt: The input prompt
        model_name: Name of the model to use (default: deepseek-chat)
        temperature: Sampling temperature (0.0 to 2.0)
        max_tokens: Maximum number of tokens to generate
        stream: Whether to stream the response
    """
    print(f"\n{'='*80}")
    print(f"MODEL: {model_name}")
    print(f"PROMPT: {prompt[:100]}..." if len(prompt) > 100 else f"PROMPT: {prompt}")
    print("-" * 40)
    
    try:
        # Initialize the LLM
        llm = OpenRouterLLM(
            model_name=model_name,
            temperature=temperature,
            max_tokens=max_tokens,
            request_timeout=60  # 60 seconds timeout
        )
        
        # Generate the response
        if stream:
            print("RESPONSE (streaming):")
            response = await llm.client.generate(
                model=model_name,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=max_tokens,
                temperature=temperature,
                stream=True
            )
            
            # Process the streaming response
            full_response = ""
            async for chunk in response:
                content = chunk.choices[0].delta.get('content', '')
                if content:
                    print(content, end='', flush=True)
                    full_response += content
            print("\n" + "-" * 40)
            print(f"Generated {len(full_response.split())} words")
            
        else:
            response = await llm.generate(
                [prompt],
                max_tokens=max_tokens,
                temperature=temperature
            )
            
            # Print the response
            content = response["choices"][0]["message"]["content"]
            print("RESPONSE:")
            print(content)
            print("-" * 40)
            print(f"Generated {len(content.split())} words")
    
    except Exception as e:
        print(f"Error generating text: {str(e)}")

async def main():
    """Run the example script."""
    # Check if API key is set
    if not os.getenv("OPENROUTER_API_KEY"):
        print("ERROR: OPENROUTER_API_KEY environment variable not set.")
        print("Please set it in your .env file or as an environment variable.")
        return
    
    # Example prompts
    prompts = [
        "Explain quantum computing in simple terms.",
        "Write a Python function to calculate Fibonacci numbers.",
        "What are the main differences between Python and JavaScript?"
    ]
    
    # Models to test
    models = [
        "deepseek-ai/deepseek-chat",  # General purpose
        "deepseek-ai/deepseek-coder-33b-instruct",  # Programming
        "qwen/qwen-14b-chat",  # Balanced performance
        "google/gemini-pro",  # Google's model
        "openai/gpt-4-turbo"  # OpenAI's latest
    ]
    
    # Test each model with each prompt
    for model in models:
        for prompt in prompts[:1]:  # Just test with first prompt for brevity
            await generate_text(
                prompt=prompt,
                model_name=model,
                temperature=0.7,
                max_tokens=500,
                stream=True  # Try with streaming
            )
            await asyncio.sleep(1)  # Rate limiting

if __name__ == "__main__":
    asyncio.run(main())
