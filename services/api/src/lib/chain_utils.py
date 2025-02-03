from typing import TypeVar, Callable, Any
from langchain_core.runnables import RunnableSerializable

T = TypeVar('T')

def retry_chain_invoke(
    chain: RunnableSerializable,
    inputs: dict[str, Any] = {},
    max_retries: int = 3
) -> Any:
    """
    Invokes a LangChain chain with retry logic.
    
    Args:
        chain: The LangChain chain to invoke
        inputs: The inputs to pass to the chain
        max_retries: Maximum number of retry attempts (default: 3)
        
    Returns:
        The chain's response
        
    Raises:
        Exception: Re-raises the last exception if all retries fail
    """
    for attempt in range(max_retries):
        try:
            response = chain.invoke(inputs)
            return response
        except Exception as e:
            if attempt == max_retries - 1:  # Last attempt
                raise e  # Re-raise the exception if all retries failed
            continue 