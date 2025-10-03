"""
Sistema di Summarizzazione con OpenAI
Modulo per la creazione di riassunti da contenuti web scraped
"""

from .core import SummarizerCore, SummarizerAWS
from .lambda_handler import lambda_handler, step_function_handler, health_check_handler
from .utils import ContactExtractor, JSONLDataLoader
from .prompts import PromptTemplates
from .config import get_openai_config, get_summary_config, get_file_config

__version__ = "1.0.0"
__author__ = "SAIO Team"

__all__ = [
    # Core classes
    'SummarizerCore',
    'SummarizerAWS',
    
    # AWS handlers
    'lambda_handler',
    'step_function_handler', 
    'health_check_handler',
    
    # Utilities
    'ContactExtractor',
    'JSONLDataLoader',
    'PromptTemplates',
    
    # Configuration
    'get_openai_config',
    'get_summary_config',
    'get_file_config'
]