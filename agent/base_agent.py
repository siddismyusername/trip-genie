"""
Base Agent classes for TripGenie ADK-inspired architecture
"""
from abc import ABC, abstractmethod
from typing import List, Optional, Any, Dict
from models import AgentInput, AgentOutput
import logging
import asyncio

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class BaseAgent(ABC):
    """Base class for all agents in the system"""
    
    def __init__(self, name: str):
        self.name = name
        logger.info(f"Initialized agent: {self.name}")
    
    @abstractmethod
    async def process(self, input_data: AgentInput) -> AgentOutput:
        """
        Process the input data and return output
        
        Args:
            input_data: AgentInput containing data and metadata
            
        Returns:
            AgentOutput containing processed data
        """
        pass
    
    async def run(self, input_data: AgentInput) -> AgentOutput:
        """
        Run the agent with error handling
        
        Args:
            input_data: Input data for the agent
            
        Returns:
            Output from the agent
        """
        try:
            logger.info(f"Running agent: {self.name}")
            # Apply per-agent timeout from settings
            from config import settings
            output = await asyncio.wait_for(self.process(input_data), timeout=settings.agent_timeout_seconds)
            logger.info(f"Agent {self.name} completed successfully")
            return output
        except asyncio.TimeoutError:
            logger.error(f"Agent {self.name} timed out")
            return AgentOutput(
                data={},
                metadata={"error": "timeout"},
                success=False,
                error="Agent timed out"
            )
        except Exception as e:
            logger.error(f"Agent {self.name} failed: {str(e)}")
            return AgentOutput(
                data={},
                metadata={"error": str(e)},
                success=False,
                error=str(e)
            )


class SequentialAgent:
    """
    Orchestrator that runs agents sequentially
    Inspired by Google ADK's SequentialAgent
    """
    
    def __init__(self, agents: List[BaseAgent], name: str = "SequentialAgent"):
        self.agents = agents
        self.name = name
        logger.info(f"Initialized {self.name} with {len(agents)} agents")
    
    async def run(self, initial_input: Dict[str, Any]) -> AgentOutput:
        """
        Run all agents in sequence, passing output to the next agent
        
        Args:
            initial_input: Initial input dictionary
            
        Returns:
            Final output from the last agent
        """
        logger.info(f"Starting {self.name} workflow")
        
        current_data = AgentInput(data=initial_input)
        
        for i, agent in enumerate(self.agents):
            logger.info(f"Step {i+1}/{len(self.agents)}: {agent.name}")
            
            output = await agent.run(current_data)
            
            if not output.success:
                logger.error(f"Workflow failed at agent {agent.name}")
                return output
            
            # Pass output as input to next agent
            current_data = AgentInput(
                data=output.data,
                metadata=output.metadata
            )
        
        logger.info(f"{self.name} workflow completed successfully")
        return output


class LLMAgent(BaseAgent):
    """Base class for agents that use LLM (Llama 3)"""
    
    def __init__(self, name: str, model: str = "llama3"):
        super().__init__(name)
        self.model = model
    
    async def call_llm(self, prompt: str, system_prompt: Optional[str] = None) -> str:
        """
        Call Llama 3 via Ollama
        
        Args:
            prompt: User prompt
            system_prompt: Optional system prompt
            
        Returns:
            LLM response text
        """
        import ollama
        from config import settings
        
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})
        
        try:
            response = ollama.chat(
                model=settings.ollama_model,
                messages=messages
            )
            return response['message']['content']
        except Exception as e:
            logger.error(f"LLM call failed: {str(e)}")
            raise
