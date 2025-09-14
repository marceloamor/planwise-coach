from openai import OpenAI
from .config import OPENAI_API_KEY, OPENAI_MODEL
from .prompts import SYSTEM_PROMPT
import logging

logger = logging.getLogger(__name__)

# Initialize client lazily to avoid issues when API key is not set
client = None

def get_openai_client():
    global client
    if client is None:
        if not OPENAI_API_KEY:
            raise ValueError("OPENAI_API_KEY environment variable is required")
        try:
            # Initialize client with longer timeout for plan generation
            client = OpenAI(
                api_key=OPENAI_API_KEY,
                timeout=60.0,  # Increased timeout for complex plan generation
                max_retries=1  # Reduced retries to fail faster if needed
            )
        except Exception as e:
            logger.error(f"Failed to initialize OpenAI client: {e}")
            raise ValueError(f"Failed to initialize OpenAI client: {e}")
    return client

def chat_to_plan(messages: list[dict[str, str]]) -> str:
    """
    Call the model and return raw content (explanation + JSON).
    messages: [{"role":"system"/"user"/"assistant","content": "..."}]
    
    TODO: In future versions, we might want different temperatures:
    - Initial plan creation: 0.4 for creativity
    - Plan modifications: 0.2 for consistency
    """
    try:
        client = get_openai_client()
        logger.info(f"Sending request to OpenAI with model {OPENAI_MODEL}")
        
        # Log the conversation length for debugging
        total_tokens = sum(len(msg.get("content", "")) for msg in messages)
        logger.info(f"Sending {len(messages)} messages (~{total_tokens} chars) to OpenAI")
        
        resp = client.chat.completions.create(
            model=OPENAI_MODEL,
            temperature=0.3,  # Balanced for MVP
            messages=messages,
            timeout=90,  # Increased timeout for complex generation
            max_tokens=4000,  # Ensure we get complete responses
            stream=False,  # Keep non-streaming for now, will add streaming separately
            stop=None,  # Don't stop early
            presence_penalty=0,  # No penalty for repetition
            frequency_penalty=0   # No penalty for repetition
        )
        
        # Safely extract content with error checking
        if not resp.choices:
            logger.error("OpenAI returned empty choices array")
            raise Exception("AI coach returned empty response. Please try again.")
        
        if not resp.choices[0].message:
            logger.error("OpenAI returned choice without message")
            raise Exception("AI coach returned malformed response. Please try again.")
            
        content = resp.choices[0].message.content
        if not content:
            logger.error("OpenAI returned empty content")
            raise Exception("AI coach returned empty content. Please try again.")
            
        logger.info(f"Successfully received response from OpenAI ({len(content)} characters)")
        
        # Check if response seems complete (should contain both explanation and JSON)
        if len(content) < 1000:
            logger.warning(f"Response seems short ({len(content)} chars) - might be incomplete")
        
        if "PLAN" not in content.upper():
            logger.warning("Response doesn't contain 'PLAN' marker - might be incomplete")
            
        return content
        
    except Exception as e:
        error_msg = str(e)
        logger.error(f"OpenAI API error: {error_msg}")
        
        # Provide more specific error messages
        if "timeout" in error_msg.lower():
            raise Exception("The AI coach is taking longer than usual to respond. Please try a simpler request or try again in a moment.")
        elif "rate_limit" in error_msg.lower():
            raise Exception("Too many requests. Please wait a moment before trying again.")
        elif "insufficient_quota" in error_msg.lower() or "quota" in error_msg.lower():
            raise Exception("OpenAI API quota exceeded. Please check your API usage and billing.")
        else:
            raise Exception(f"AI coach temporarily unavailable: {error_msg}") 