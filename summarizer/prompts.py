"""
Template dei prompt per il sistema di summarizzazione
"""
from typing import List

class PromptTemplates:
    """Gestisce i template dei prompt per OpenAI"""
    
    @staticmethod
    def get_system_prompt() -> str:
        """Prompt di sistema per stabilire il comportamento dell'AI"""
        return """Sei un assistente esperto nella creazione di riassunti in italiano. 
Scrivi sempre in italiano perfetto, chiaro e naturale. 
La tua specialità è preservare informazioni di contatto importanti (telefoni, email, indirizzi, orari) 
e creare riassunti che mantengano le informazioni più rilevanti del contenuto originale."""
    
    @staticmethod
    def get_summary_prompt(text: str, length_target: str, contact_info: List[str] = None) -> str:
        """Prompt per il summary unificato"""
        contact_reminder = ""
        if contact_info:
            contact_reminder = f"\n\nINFORMAZIONI DI CONTATTO RILEVATE (DA INCLUDERE OBBLIGATORIAMENTE):\n" + "\n".join(contact_info)
        
        return f"""Crea un riassunto dettagliato e coerente in italiano del seguente contenuto web.

Il riassunto deve:
- Essere di {length_target}
- Essere scritto in italiano perfetto
- Includere OBBLIGATORIAMENTE tutte le informazioni di contatto presenti (telefono, email, indirizzo, orari, sito web)
- Includere le informazioni più importanti su storia, servizi, prodotti e caratteristiche dell'attività
- Essere scorrevole e ben strutturato
- Terminare sempre con una sezione "CONTATTI:" se sono presenti informazioni di contatto

IMPORTANTE: Non omettere mai numeri di telefono, email, indirizzi o altri dati di contatto se presenti nel testo.{contact_reminder}

Contenuto da riassumere:
{text}

Riassunto in italiano:"""
    
    @staticmethod
    def get_aws_error_response(error_message: str) -> dict:
        """Template per risposte di errore AWS"""
        return {
            "statusCode": 500,
            "body": {
                "success": False,
                "error": error_message,
                "summary": None,
                "unified_summary": None
            }
        }
    
    @staticmethod
    def get_aws_success_response(summary: str = None, contact_info: List[str] = None) -> dict:
        """Template per risposte di successo AWS"""
        return {
            "statusCode": 200,
            "body": {
                "success": True,
                "error": None,
                "summary": summary,
                "contact_info_found": contact_info or [],
                "metadata": {
                    "summary_length": len(summary) if summary else 0,
                    "contacts_found": len(contact_info) if contact_info else 0
                }
            }
        }