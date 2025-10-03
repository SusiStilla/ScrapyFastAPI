"""
Main entry point per il sistema di summarizzazione
Mantiene compatibilità con l'interfaccia precedente
"""
import argparse
import sys
from pathlib import Path

from .core import SummarizerCore
from .config import get_file_config


def main():
    """Funzione principale per l'uso da riga di comando"""
    
    # Parsing degli argomenti da riga di comando
    parser = argparse.ArgumentParser(description='Genera riassunti da file JSONL')
    
    file_config = get_file_config()
    
    parser.add_argument('--input', '-i', 
                       default=file_config['input_file'], 
                       help='File di input JSONL')
    parser.add_argument('--output', '-o',
                       default=file_config['output_file'],
                       help='File di output per il summary unificato')
    
    args = parser.parse_args()
    
    try:
        # Verifica che il file di input esista
        if not Path(args.input).exists():
            print(f"❌ ERRORE: File di input non trovato: {args.input}")
            sys.exit(1)
        
        print(f"🚀 Inizializzazione sistema di summarizzazione...")
        
        # Inizializza il core summarizer
        summarizer = SummarizerCore()
        
        print(f"✅ Sistema inizializzato correttamente")
        print(f"📄 Elaborazione file: {args.input}")
        
        # Processa il file
        result = summarizer.process_jsonl_file(args.input)
        
        print(f"\n📊 Risultati:")
        print(f"  📋 Record processati: {result['records_processed']}")
        print(f"  📞 Contatti trovati: {len(result['contact_info'])}")
        
        if result['contact_info']:
            print(f"  📱 Contatti rilevati:")
            for contact in result['contact_info']:
                print(f"    • {contact}")
        
        # === SALVATAGGIO SUMMARY UNIFICATO ===
        print(f"\n� Salvataggio summary unificato...")
        
        # Crea header descrittivo
        header = f"SUMMARY UNIFICATO - {result['records_processed']} pagine processate\n"
        header += "=" * 60 + "\n\n"
        
        summary_content = header + result['summary']
        
        with open(args.output, 'w', encoding='utf-8') as f:
            f.write(summary_content)
        
        print(f"  ✅ Salvato in: {args.output}")
        print(f"  📏 Lunghezza summary: {len(result['summary'])} caratteri")
        
        print(f"\n🎉 Processo completato con successo!")
        print(f"📋 Summary unificato: {args.output}")
        
    except KeyboardInterrupt:
        print(f"\n⚠️  Processo interrotto dall'utente")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ ERRORE: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()