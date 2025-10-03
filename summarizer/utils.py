"""
Utilità per l'estrazione di contatti e gestione dati JSONL
"""
import json
import re
from typing import List, Dict, Any

class ContactExtractor:
    """Classe per estrarre informazioni di contatto da testi"""
    
    @staticmethod
    def extract_contact_info(text: str) -> List[str]:
        """Estrae automaticamente informazioni di contatto dal testo."""
        contact_info = []
        
        # Pattern per telefoni italiani (più specifici)
        phone_patterns = [
            r'\b0\d{2,3}[\.\s]?\d{6,7}\b',  # Numeri fissi: 0161.217420, 02.12345678
            r'\b3\d{2}[\.\s]?\d{3}[\.\s]?\d{4}\b',  # Cellulari: 339.123.4567
            r'\b\+39[\s]?0\d{2,3}[\s]?\d{6,7}\b',  # +39 0161 217420
            r'\b\+39[\s]?3\d{2}[\s]?\d{3}[\s]?\d{4}\b'  # +39 339 123 4567
        ]
        
        for pattern in phone_patterns:
            phones = re.findall(pattern, text)
            for phone in phones:
                # Pulisci e formatta il numero
                clean_phone = re.sub(r'[\s\.]', '', phone)
                if clean_phone not in [c.split(' ', 1)[1] for c in contact_info if c.startswith('📞')]:
                    contact_info.append(f"📞 {phone}")
        
        # Pattern per email
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        emails = re.findall(email_pattern, text)
        for email in emails:
            if email not in [c.split(' ', 1)[1] for c in contact_info if c.startswith('📧')]:
                contact_info.append(f"📧 {email}")
        
        # Pattern per indirizzi (più specifici e limitati)
        address_patterns = [
            r'Via\s+[A-Za-z\s]+\d{1,4}(?:\s*,\s*\d{5})?',  # Via Roma 123, 13100
            r'Piazza\s+[A-Za-z\s]+(?:\d{1,4})?',  # Piazza Cavour 1
            r'Corso\s+[A-Za-z\s]+\d{1,4}'  # Corso Italia 45
        ]
        
        for pattern in address_patterns:
            addresses = re.findall(pattern, text, re.IGNORECASE)
            for address in addresses:
                # Verifica che sia un indirizzo valido (non una frase)
                if (len(address.split()) <= 4 and 
                    not any(word in address.lower() for word in ['successi', 'brillante', 'percorso', 'ambito'])):
                    contact_info.append(f"📍 {address}")
        
        # Rimuovi duplicati mantenendo l'ordine
        seen = set()
        unique_contacts = []
        for contact in contact_info:
            if contact not in seen:
                seen.add(contact)
                unique_contacts.append(contact)
        
        return unique_contacts
    
    @staticmethod
    def verify_contacts_in_summary(summary: str, contact_info: List[str]) -> str:
        """Verifica che i contatti siano inclusi nel summary e li aggiunge se mancanti"""
        if not contact_info:
            return summary
            
        missing_contacts = []
        for contact in contact_info:
            # Estrai il numero/email dal contatto formattato
            contact_value = contact.split(' ', 1)[1] if ' ' in contact else contact
            # Verifica se il contatto è presente nel summary (anche con formattazione diversa)
            contact_clean = re.sub(r'[\s\.\-\(\)]', '', contact_value)
            summary_clean = re.sub(r'[\s\.\-\(\)]', '', summary)
            if contact_clean not in summary_clean:
                missing_contacts.append(contact)
        
        # Se mancano contatti, aggiungili alla fine (solo se non già presente una sezione contatti)
        if missing_contacts and "CONTATTI:" not in summary:
            summary += "\n\nCONTATTI:\n" + "\n".join(missing_contacts)
            
        return summary


class JSONLDataLoader:
    """Classe per caricare e gestire dati JSONL"""
    
    @staticmethod
    def load_data(file_path: str) -> List[Dict[str, Any]]:
        """Carica i dati dal file JSON concatenato (formato personalizzato)."""
        data = []
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read().strip()
            
            # Gestisce sia formato JSONL tradizionale che JSON concatenati
            if '\n' in content:
                # Formato JSONL tradizionale (una riga per JSON)
                for line in content.split('\n'):
                    if line.strip():
                        data.append(json.loads(line.strip()))
            else:
                # JSON concatenati su una singola riga (formato del nostro file)
                json_objects = JSONLDataLoader._split_concatenated_json(content)
                
                # Parsa tutti gli oggetti JSON trovati
                for json_str in json_objects:
                    data.append(json.loads(json_str))
            
            return data
            
        except FileNotFoundError:
            raise FileNotFoundError(f"File non trovato: {file_path}")
        except json.JSONDecodeError as e:
            raise ValueError(f"Errore di decodifica JSON: {e}")
        except Exception as e:
            raise Exception(f"Errore generico nel caricamento dati: {e}")
    
    @staticmethod
    def _split_concatenated_json(content: str) -> List[str]:
        """Divide JSON concatenati in oggetti singoli"""
        json_objects = []
        
        # Trova tutte le posizioni dove termina un oggetto JSON e ne inizia un altro
        pattern = r'}\s*{'
        matches = list(re.finditer(pattern, content))
        
        if matches:
            # Aggiungi il primo oggetto
            first_end = matches[0].start() + 1  # +1 per includere la }
            json_objects.append(content[:first_end])
            
            # Aggiungi tutti gli oggetti intermedi e l'ultimo
            for i in range(len(matches)):
                start_pos = matches[i].start() + 1  # dopo la }
                if i < len(matches) - 1:
                    end_pos = matches[i+1].start() + 1
                    json_objects.append(content[start_pos:end_pos])
                else:
                    # L'ultimo oggetto
                    json_objects.append(content[start_pos:])
        else:
            # Se non ci sono separatori, è un singolo oggetto
            json_objects.append(content)
        
        return json_objects
    
    @staticmethod
    def combine_texts_for_unified_summary(data: List[Dict[str, Any]]) -> str:
        """Combina tutti i testi per il summary unificato"""
        all_texts = []
        
        for record in data:
            text = record.get("text", "")
            if text:
                # Aggiungi anche informazioni di contesto (titolo e URL)
                title = record.get("title", "")
                url = record.get("url", "")
                
                context_info = f"Pagina: {title}"
                if url:
                    context_info += f" (da {url})"
                
                formatted_text = f"{context_info}\n{text}"
                all_texts.append(formatted_text)
        
        if not all_texts:
            raise ValueError("Nessun testo trovato per il summary unificato.")
        
        # Unisce tutti i testi con un separatore
        return "\n\n".join(all_texts)