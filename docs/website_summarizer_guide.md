# Website Summarizer - Sistema Generico di Analisi Siti Web

Un sistema completo e flessibile per analizzare e riassumere dati di crawling di qualsiasi tipo di sito web.

## 🚀 Caratteristiche Principali

- **Analisi Generica**: Funziona con qualsiasi tipo di sito web
- **Configurabile**: Sistema di configurazione per diversi tipi di siti
- **AI Integrato**: Supporto per riassunti automatici con BART
- **Multi-formato**: Output in testo, JSON o entrambi
- **Classificazione Automatica**: Identifica automaticamente le tipologie di pagine
- **Estrazione Informazioni**: Estrae contatti, navigazione e contenuti chiave

## 📁 Struttura del Sistema

```
SAIO/
├── app/
│   ├── website_summarizer.py      # Classe base per l'analisi
│   └── enhanced_summarizer.py     # Versione avanzata con configurazione
├── config/
│   └── summarizer_config.yaml     # Configurazioni per tipi di siti
├── analyze_website.py             # Script principale con opzioni
├── simple_summarizer.py           # Versione semplificata
└── requirements.txt               # Dipendenze necessarie
```

## 🛠️ Installazione

1. **Installa le dipendenze:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Per il supporto AI (opzionale):**
   ```bash
   pip install transformers torch
   ```

## 📖 Utilizzo

### 1. Analisi Semplice e Veloce

Per un'analisi rapida senza configurazioni:

```bash
python simple_summarizer.py data/your_crawl.json
```

**Output esempio:**
```
============================================================
ANALISI SEMPLICE SITO: example.com
============================================================

📊 STATISTICHE:
   • Pagine totali: 25
   • Parole totali: 3,450

📞 CONTATTI:
   • Email: info@example.com
   • Telefono: +39 123 456789

🏠 HOMEPAGE:
   Benvenuti nel nostro sito web...
```

### 2. Analisi Completa Configurabile

Per un'analisi dettagliata con classificazione automatica:

```bash
# Analisi base
python analyze_website.py data/your_crawl.json

# Specifica il tipo di sito
python analyze_website.py data/restaurant.json restaurant

# Con riassunti AI
python analyze_website.py data/company.json corporate

# Senza AI (più veloce)
python analyze_website.py data/shop.json ecommerce --no-ai

# Salva risultati in JSON
python analyze_website.py data/site.json --output analysis.json

# Output dettagliato
python analyze_website.py data/site.json --verbose
```

### 3. Tipi di Siti Supportati

| Tipo | Descrizione | Estrattori Specifici |
|------|-------------|---------------------|
| `restaurant` | Ristoranti, pizzerie, caffè | Menu, orari, specialità |
| `ecommerce` | Negozi online, retail | Prodotti, spedizioni, pagamenti |
| `corporate` | Aziende, servizi | Servizi, mission, team |
| `portfolio` | Portfolio personali | Competenze, progetti |
| `generic` | Qualsiasi altro sito | Analisi base |

## 🔧 Configurazione Personalizzata

### File di Configurazione

Il file `config/summarizer_config.yaml` permette di personalizzare:

- **Classificazione delle pagine**
- **Estrazione di informazioni specifiche**
- **Pattern di riconoscimento**
- **Priorità dei contenuti**

### Esempio di Configurazione per Ristoranti

```yaml
website_types:
  restaurant:
    priority_pages: ['homepage', 'about', 'menu/services', 'contact']
    key_fields:
      - name
      - cuisine_type
      - location
      - phone
      - opening_hours
      - specialties
    content_patterns:
      name: ['ristorante', 'pizzeria', 'trattoria']
      location: ['via', 'corso', 'piazza']
      phone: ['\d{3}[\.-]?\d{3}[\.-]?\d{4}']
```

## 📊 Output e Risultati

### Report Testuale

```
================================================================================
ANALISI SITO WEB: acquapazzavercelli.it
================================================================================

📊 STATISTICHE GENERALI:
   • Pagine totali: 79
   • Pagine analizzate con successo: 79
   • Parole totali: 4,730

📄 TIPOLOGIE DI PAGINE:
   • Homepage: 48 pagine
   • Gallery: 22 pagine
   • About: 4 pagine

📞 INFORMAZIONI DI CONTATTO:
   • Email: info@acquapazzavercelli.it
   • Address: Corso Gastaldi 25, 13100 Vercelli

🧭 STRUTTURA NAVIGAZIONE:
   homepage → gallery → about → contact

📝 RIASSUNTO CONTENUTO:
   Ristorante pizzeria nel cuore di Vercelli...

🎯 INFORMAZIONI SPECIFICHE:
   • Name: Ristorante Acquapazza
   • Location: Vercelli, Corso Gastaldi
   • Phone: 0161.217420
```

### Export JSON

```json
{
  "domain": "acquapazzavercelli.it",
  "total_pages": 79,
  "page_types": {
    "homepage": 48,
    "gallery": 22,
    "about": 4
  },
  "contact_info": {
    "email": "info@acquapazzavercelli.it",
    "phone": "0161.217420"
  },
  "content_summary": "Ristorante pizzeria nel cuore di Vercelli...",
  "analysis_date": "2025-09-26T10:30:00"
}
```

## 🤖 Integrazione AI

### BART Summarization

Il sistema supporta il modello BART di Facebook per riassunti automatici:

- **Modello**: `facebook/bart-large-cnn`
- **Attivazione**: Automatica se `transformers` è installato
- **Fallback**: Riassunto estrattivo se AI non disponibile

### MCP Hugging Face Integration

Integrazione con il server MCP Hugging Face per:
- Accesso ai modelli cloud
- Riassunti senza installazione locale
- Performance migliorate

## 📝 Esempi Pratici

### 1. Analizzare un Ristorante

```bash
python analyze_website.py data/restaurant_crawl.json restaurant --verbose
```

### 2. E-commerce con Output JSON

```bash
python analyze_website.py data/shop_crawl.json ecommerce \
  --output shop_analysis.json --format both
```

### 3. Portfolio senza AI

```bash
python analyze_website.py data/portfolio_crawl.json portfolio --no-ai
```

## 🔍 Uso Programmatico

```python
from app.enhanced_summarizer import create_summarizer, analyze_crawl_file

# Analisi semplice
report = analyze_crawl_file('data/site.json', 'restaurant')
print(report)

# Analisi personalizzata
summarizer = create_summarizer(website_type='ecommerce', use_ai=True)
pages = summarizer.load_crawl_data('data/shop.json')
analysis = summarizer.analyze_website(pages)
```

## 🚨 Risoluzione Problemi

### Errori Comuni

1. **"transformers not available"**
   ```bash
   pip install transformers torch
   ```

2. **"Config file not found"**
   - Il sistema usa configurazioni di default
   - Verifica il percorso del file di config

3. **"No pages found"**
   - Controlla il formato del file JSON
   - Ogni riga deve essere un oggetto JSON valido

### Performance

- **Senza AI**: ~1-2 secondi per 100 pagine
- **Con AI**: ~5-10 secondi per 100 pagine
- **Memory**: ~200MB senza AI, ~2GB con BART

## 🔄 Formati di Input Supportati

Il sistema accetta file JSON con questo formato:

```json
{"url": "https://example.com/", "title": "Home", "text": "Contenuto...", "status": 200}
{"url": "https://example.com/about", "title": "About", "text": "Chi siamo...", "status": 200}
```

Ogni riga deve essere un oggetto JSON separato (JSONL format).

## 🎯 Casi d'Uso

- **Web Scraping Analysis**: Analizza risultati di crawling
- **SEO Audit**: Identifica struttura e contenuti
- **Competitive Analysis**: Confronta siti concorrenti  
- **Content Strategy**: Pianifica contenuti basati su analisi
- **Site Migration**: Mappa contenuti durante migrazioni

---

**Sistema sviluppato per SAIO - Smart AI Operations**