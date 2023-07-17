from pydantic import BaseModel, validator, EmailStr
from typing import Optional, Literal, List
import os
import re
import uuid
from fastapi import HTTPException

from .utils import get_settings
def validate_uuid(uuid_string):
    """
    Regex pattern to validate uuid
    """
    pattern = re.compile(
        r'^[0-9a-fA-F]{8}-'
        r'[0-9a-fA-F]{4}-'
        r'[0-9a-fA-F]{4}-'
        r'[0-9a-fA-F]{4}-'
        r'[0-9a-fA-F]{12}$'
    )
    return re.match(pattern, uuid_string)


class DocModel(BaseModel):
    """
    Model for document processing.
    """
    urls: List[str]
    client_id: EmailStr = EmailStr()
    embeddings_name: Optional[Literal['openai', 'sentence']] = 'openai'
    #collection_name: Optional[str] = 'LangChainCollection'
    drop_existing_embeddings: Optional[bool] = False

    @validator('urls')
    def validate_urls(cls, urls):
        if not isinstance(urls, list):
            raise ValueError('Urls must be a list')
        for url in urls:
            if not isinstance(url, str):
                raise ValueError('Urls must be a list of strings')
        return urls

    @validator('embeddings_name')
    def validate_embeddings(cls, embeddings_name):
        """
        Validates the embeddings name.
        """
        if embeddings_name == 'openai':
            key = get_settings().openai_api_key
            if len(key) != 51 or not key.startswith('sk'):
                raise ValueError('The API is not valid or not provided')
        return embeddings_name


class QueryModel(BaseModel):
    """
    Represents a query model with text, session_id, and optional parameters.
    """

    text: str
    session_id: str = str(uuid.uuid4())
    client_id: EmailStr = EmailStr()
    llm_name: Optional[Literal['openai', 'llamacpp', 'gpt4all']] = 'openai'
    #collection_name: Optional[str] = 'LangChainCollection'

    @validator('text')
    def validate_text(cls, text):
        """
        Validates the 'text' field to ensure it is not empty.
        """
        if not text:
            raise ValueError('Text must be provided')
        return text

    @validator('session_id')
    def validate_session_id(cls, session_id):
        """
        Validates the 'session_id' field to ensure it is a valid uuid4 format.
        """
        if not validate_uuid(session_id):
            raise ValueError('Session ID must be in uuid4 format')
        return session_id

    @validator('llm_name')
    def validate_llm_name(cls, llm_name):
        """
        Validates the 'llm_name' field based on specific conditions for different values.
        """
        if llm_name == 'openai':
            key = get_settings().openai_api_key
            if len(key) != 51 or not key.startswith('sk'):
                raise ValueError('The API is not valid or not provided')

        if llm_name == 'gpt4all':
            if not os.path.isfile('llms/ggml-gpt4all-j.bin'):
                raise HTTPException(status_code=404, detail="Model weights are not found")

        if llm_name == 'llamacpp':
            if not os.path.isfile('llms/ggml-gpt4all-l13b-snoozy.bin'):
                raise HTTPException(status_code=404, detail="Model weights are not found")    
  
        return llm_name


class DeleteSession(BaseModel):
    """
    Represents a request to delete a session.
    """
    session_id: str

    @validator('session_id')
    def validate_session_id(cls, session_id):
        """
        Validates the 'session_id' field to ensure it is a valid uuid4 format.
        """
        if not validate_uuid(session_id):
            raise ValueError('Session ID must be in uuid4 format')
        return session_id
