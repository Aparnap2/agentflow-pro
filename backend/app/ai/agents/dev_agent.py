from typing import Dict, Any, List, Optional
from .base_agent import BaseAgent, AgentConfig, AgentResponse

class DevelopmentAgent(BaseAgent):
    """Base class for development and QA agents."""
    
    def __init__(self, config: AgentConfig):
        super().__init__(config)
        self.supported_languages = ['python', 'javascript', 'typescript', 'java', 'go']
    
    async def review_code(self, code_data: Dict) -> AgentResponse:
        """Review and analyze code for quality and best practices."""
        try:
            language = code_data.get('language', 'python')
            review = await self.llm.generate(
                f"Review this {language} code for quality, bugs, and best practices:\n"
                f"{code_data.get('code', '')}\n\n"
                "Provide specific feedback and suggestions for improvement."
            )
            return AgentResponse(
                success=True,
                output={"code_review": review},
                metadata={
                    "language": language,
                    "file": code_data.get('file_path', 'unknown')
                }
            )
        except Exception as e:
            return AgentResponse(
                success=False,
                error=f"Code review failed: {str(e)}"
            )
    
    async def generate_tests(self, code_data: Dict) -> AgentResponse:
        """Generate test cases for the provided code."""
        try:
            language = code_data.get('language', 'python')
            test_framework = code_data.get('test_framework', 'pytest' if language == 'python' else 'jest')
            
            tests = await self.llm.generate(
                f"Generate {test_framework} test cases for this {language} code:\n"
                f"{code_data.get('code', '')}\n\n"
                f"Include test cases for edge cases and error conditions."
            )
            return AgentResponse(
                success=True,
                output={
                    "test_cases": tests,
                    "test_framework": test_framework
                },
                metadata={
                    "language": language,
                    "file": code_data.get('file_path', 'unknown')
                }
            )
        except Exception as e:
            return AgentResponse(
                success=False,
                error=f"Test generation failed: {str(e)}"
            )
