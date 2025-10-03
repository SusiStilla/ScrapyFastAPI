"""
AWS Lambda Handler per il sistema di summarizzazione
Compatibile con Step Functions e integrabile in pipeline AWS
"""
import json
import logging
from typing import Dict, Any

from .core import SummarizerAWS

# Configurazione logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)


def lambda_handler(event: Dict[str, Any], context: Any = None) -> Dict[str, Any]:
    """
    Handler principale per AWS Lambda
    
    Evento di input atteso:
    {
        "file_path": "/path/to/file.jsonl",  # Per file locali
        "s3_bucket": "my-bucket",            # Per file S3 (alternativo)
        "s3_key": "data/file.jsonl",         # Per file S3 (alternativo)
        "output_s3_bucket": "output-bucket", # Opzionale: dove salvare i risultati
        "output_s3_prefix": "summaries/"     # Opzionale: prefisso per i file di output
    }
    
    Output:
    {
        "statusCode": 200,
        "body": {
            "success": true,
            "summary": "...",                 # Summary unificato
            "contact_info": [...],            # Informazioni di contatto rilevate
            "metadata": {
                "records_processed": 2,
                "summary_length": 1200,
                "contacts_found": 3
            }
        }
    }
    """
    
    logger.info(f"Evento ricevuto: {json.dumps(event, default=str)}")
    
    try:
        # Inizializza il summarizer AWS
        summarizer = SummarizerAWS()
        
        # Processa l'evento
        result = summarizer.handle_lambda_event(event)
        
        logger.info(f"Processamento completato con successo. Status: {result['statusCode']}")
        
        return result
        
    except Exception as e:
        error_msg = f"Errore nel processamento: {str(e)}"
        logger.error(error_msg)
        
        return {
            "statusCode": 500,
            "body": {
                "success": False,
                "error": error_msg,
                "summary": None,
                "unified_summary": None
            }
        }


def step_function_handler(event: Dict[str, Any], context: Any = None) -> Dict[str, Any]:
    """
    Handler specifico per AWS Step Functions
    Formatta l'output in modo più strutturato per il workflow
    """
    
    logger.info(f"Step Function evento ricevuto: {json.dumps(event, default=str)}")
    
    try:
        # Usa lo stesso handler lambda ma formatta l'output per Step Functions
        result = lambda_handler(event, context)
        
        if result["statusCode"] == 200:
            # Successo - estrai i dati dal body per Step Functions
            body = result["body"]
            
            return {
                "success": True,
                "data": {
                    "summary": body.get("summary"),
                    "contact_info": body.get("contact_info", []),
                    "metadata": body.get("metadata", {})
                },
                "next_step": determine_next_step(body),  # Logica per il prossimo step
                "timestamp": context.aws_request_id if context else None
            }
        else:
            # Errore
            return {
                "success": False,
                "error": result["body"]["error"],
                "retry_recommended": is_retryable_error(result["body"]["error"]),
                "timestamp": context.aws_request_id if context else None
            }
            
    except Exception as e:
        error_msg = f"Errore nel Step Function handler: {str(e)}"
        logger.error(error_msg)
        
        return {
            "success": False,
            "error": error_msg,
            "retry_recommended": False,
            "timestamp": context.aws_request_id if context else None
        }


def determine_next_step(body: Dict[str, Any]) -> str:
    """Determina il prossimo step nel workflow basato sui risultati"""
    
    if body.get("summary"):
        if body.get("contact_info"):
            return "SAVE_RESULTS_WITH_CONTACTS"
        else:
            return "SAVE_RESULTS"
    else:
        return "REVIEW_REQUIRED"


def is_retryable_error(error_message: str) -> bool:
    """Determina se l'errore è recuperabile con un retry"""
    
    retryable_keywords = [
        "timeout", "connection", "rate limit", 
        "temporary", "service unavailable", "502", "503"
    ]
    
    error_lower = error_message.lower()
    return any(keyword in error_lower for keyword in retryable_keywords)


def health_check_handler(event: Dict[str, Any], context: Any = None) -> Dict[str, Any]:
    """Handler per health check del servizio"""
    
    try:
        # Test veloce del sistema
        summarizer = SummarizerAWS()
        
        # Verifica che OpenAI sia raggiungibile
        test_response = summarizer.core.client.models.list()
        
        return {
            "statusCode": 200,
            "body": {
                "status": "healthy",
                "openai_connection": "ok",
                "timestamp": context.aws_request_id if context else "local"
            }
        }
        
    except Exception as e:
        return {
            "statusCode": 503,
            "body": {
                "status": "unhealthy",
                "error": str(e),
                "timestamp": context.aws_request_id if context else "local"
            }
        }


# Export per facilità di import
__all__ = [
    'lambda_handler',
    'step_function_handler', 
    'health_check_handler'
]