"""
Configurazione per il sistema di summarizzazione
"""
import os
from typing import Dict, Any

# === CONFIGURAZIONE OPENAI ===
OPENAI_MODEL = "gpt-4o-mini"  # Ottimo per riassunti in italiano
OPENAI_MAX_TOKENS_INPUT = 4000  # Lunghezza massima dell'input
OPENAI_MAX_TOKENS_OUTPUT = 800  # Per summary unificato
OPENAI_TEMPERATURE = 0.3  # Bassa per coerenza
OPENAI_TOP_P = 0.9

# === CONFIGURAZIONE RIASSUNTO UNIFICATO ===
SUMMARY_LENGTH = "circa 200-300 parole"

# === CONFIGURAZIONE FILE ===
DEFAULT_INPUT_FILE = "summarizer/data/acquapazza_crawl_clean_manual.json"
DEFAULT_OUTPUT_FILE = "summarizer/data/unified_summary.txt"

# === CONFIGURAZIONE AWS ===
AWS_REGION = os.getenv('AWS_REGION', 'eu-west-1')
S3_BUCKET = os.getenv('S3_BUCKET')

# === CONFIGURAZIONE LOGGING ===
LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')

def get_openai_config() -> Dict[str, Any]:
    """Restituisce la configurazione OpenAI"""
    return {
        'model': OPENAI_MODEL,
        'max_tokens_input': OPENAI_MAX_TOKENS_INPUT,
        'max_tokens_output': OPENAI_MAX_TOKENS_OUTPUT,
        'temperature': OPENAI_TEMPERATURE,
        'top_p': OPENAI_TOP_P
    }

def get_summary_config() -> Dict[str, Any]:
    """Restituisce la configurazione per il riassunto unificato"""
    return {
        'length': SUMMARY_LENGTH
    }

def get_file_config() -> Dict[str, Any]:
    """Restituisce la configurazione per i file"""
    return {
        'input_file': DEFAULT_INPUT_FILE,
        'output_file': DEFAULT_OUTPUT_FILE
    }