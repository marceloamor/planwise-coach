"""
Streaming support for AI responses (FUTURE FEATURE).

This module provides functionality for streaming chat responses from OpenAI.
Currently not integrated into the main application but ready for future use.

To enable streaming:
1. Update the /chat endpoint in main.py to accept a 'stream' parameter
2. Use create_streaming_response() instead of chat_to_plan()
3. Update frontend to handle Server-Sent Events (SSE)
"""

from fastapi import Request
from fastapi.responses import StreamingResponse
import json
import asyncio
from typing import AsyncGenerator
from .llm import get_openai_client
from .config import OPENAI_MODEL
import logging

logger = logging.getLogger(__name__)

async def stream_chat_response(messages: list[dict[str, str]]) -> AsyncGenerator[str, None]:
    """
    Stream AI response as it's generated.
    Yields Server-Sent Events format for frontend consumption.
    """
    try:
        client = get_openai_client()
        logger.info(f"Starting streaming request to OpenAI with model {OPENAI_MODEL}")
        
        stream = client.chat.completions.create(
            model=OPENAI_MODEL,
            temperature=0.3,
            messages=messages,
            timeout=60,
            max_tokens=4000,
            stream=True
        )
        
        accumulated_content = ""
        
        for chunk in stream:
            if chunk.choices[0].delta.content is not None:
                content = chunk.choices[0].delta.content
                accumulated_content += content
                
                # Send the chunk as Server-Sent Event
                yield f"data: {json.dumps({'type': 'content', 'data': content})}\n\n"
        
        # Send completion signal
        yield f"data: {json.dumps({'type': 'complete', 'data': accumulated_content})}\n\n"
        
    except Exception as e:
        logger.error(f"Streaming error: {e}")
        yield f"data: {json.dumps({'type': 'error', 'data': str(e)})}\n\n"

def create_streaming_response(messages: list[dict[str, str]]) -> StreamingResponse:
    """Create a StreamingResponse for chat."""
    return StreamingResponse(
        stream_chat_response(messages),
        media_type="text/plain",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "Access-Control-Allow-Origin": "*",
        }
    ) 