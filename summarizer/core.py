"""
Core del sistema di summarizzazione con OpenAI
"""
import os
import re
from typing import List, Dict, Any, Optional
from openai import OpenAI
from dotenv import load_dotenv

from .config import get_openai_config, get_summary_config
from .prompts import PromptTemplates
from .utils import ContactExtractor, JSONLDataLoader

# Carica le variabili d'ambiente
load_dotenv()


class SummarizerCore:
    """Classe principale per la summarizzazione con OpenAI"""
    
    def __init__(self):
        self.client = self._initialize_openai_client()
        self.openai_config = get_openai_config()
        self.summary_config = get_summary_config()
        self.prompts = PromptTemplates()
        self.contact_extractor = ContactExtractor()
        self.data_loader = JSONLDataLoader()
    
    def _initialize_openai_client(self) -> OpenAI:
        """Inizializza il client OpenAI"""
        api_key = os.getenv('OPENAI_API_KEY')
        if not api_key:
            raise ValueError("OPENAI_API_KEY non trovata nel file .env")
        
        client = OpenAI(api_key=api_key)
        # Test della connessione
        try:
            client.models.list()
        except Exception as e:
            raise ConnectionError(f"Impossibile connettersi a OpenAI: {e}")
        
        return client
    
    def summarize_text(self, text: str) -> str:
        """Genera il riassunto unificato di un testo usando OpenAI GPT-4o-mini"""
        
        # Estrai informazioni di contatto per assicurarsi che non vengano perse
        contact_info = self.contact_extractor.extract_contact_info(text)
        
        # Tronca il testo se troppo lungo (lasciando spazio per il prompt)
        max_chars = self.openai_config['max_tokens_input'] * 3  # Circa 3 caratteri per token
        if len(text) > max_chars:
            text = text[:max_chars] + "..."
        
        # Genera il prompt
        prompt = self.prompts.get_summary_prompt(text, self.summary_config['length'], contact_info)
        
        try:
            response = self.client.chat.completions.create(
                model=self.openai_config['model'],
                messages=[
                    {"role": "system", "content": self.prompts.get_system_prompt()},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=self.openai_config['max_tokens_output'],
                temperature=self.openai_config['temperature'],
                top_p=self.openai_config['top_p']
            )
            
            summary = response.choices[0].message.content.strip()
            
            # Verifica che i contatti rilevati siano stati inclusi nel summary
            summary = self.contact_extractor.verify_contacts_in_summary(summary, contact_info)
            
            return summary
            
        except Exception as e:
            raise Exception(f"Errore nella generazione del riassunto: {e}")
    
    def process_jsonl_file(self, file_path: str) -> Dict[str, Any]:
        """Processa un file JSONL e genera un summary unificato"""
        
        # Carica i dati
        try:
            data = self.data_loader.load_data(file_path)
        except Exception as e:
            raise ValueError(f"Errore nel caricamento del file: {e}")
        
        if not data:
            raise ValueError("Nessun dato trovato nel file")
        
        # Raccogli tutte le informazioni di contatto
        all_contact_info = []
        for record in data:
            original_text = record.get("text", "")
            if original_text:
                contacts = self.contact_extractor.extract_contact_info(original_text)
                all_contact_info.extend(contacts)
        
        # Genera summary unificato
        try:
            combined_text = self.data_loader.combine_texts_for_unified_summary(data)
            summary = self.summarize_text(combined_text)
        except Exception as e:
            raise ValueError(f"Errore nella generazione del summary: {e}")
        
        # Rimuovi duplicati dalle informazioni di contatto
        unique_contacts = list(dict.fromkeys(all_contact_info))
        
        return {
            "summary": summary,
            "contact_info": unique_contacts,
            "records_processed": len(data)
        }
    



class SummarizerAWS:
    """Wrapper AWS-specific per il Summarizer"""
    
    def __init__(self):
        self.core = SummarizerCore()
        self.prompts = PromptTemplates()
    
    def handle_lambda_event(self, event: Dict[str, Any]) -> Dict[str, Any]:
        """Handler principale per AWS Lambda"""
        
        try:
            # Estrai parametri dall'evento
            file_path = event.get('file_path')
            s3_bucket = event.get('s3_bucket')
            s3_key = event.get('s3_key')
            
            # Determina il percorso del file
            if not file_path and s3_bucket and s3_key:
                # TODO: Implementare download da S3
                raise NotImplementedError("Download da S3 non ancora implementato")
            elif not file_path:
                raise ValueError("Specificare 'file_path' o ('s3_bucket' e 's3_key')")
            
            # Processa il file
            result = self.core.process_jsonl_file(file_path)
            
            return self.prompts.get_aws_success_response(
                summary=result["summary"],
                contact_info=result["contact_info"]
            )
            
        except Exception as e:
            return self.prompts.get_aws_error_response(str(e))