# SAIO — Search AI Optimization

## 🎯 Obiettivo del progetto
Costruire una piattaforma che aiuti aziende e locali ad aumentare la loro **visibilità sugli LLM** (Large Language Models) come ChatGPT, Gemini, Copilot.  
Quando un utente chiede ad esempio *“Qual è la migliore pizzeria in Zona Solari a Milano?”* oppure *“Quali sono le aziende italiane di wearable calcistici?”*, SAIO deve fornire strumenti per migliorare la probabilità che l’azienda/locali siano **menzionati e favoriti** dagli LLM.

---

## 🧪 Ipotesi da verificare
- **H1 – Structuredness**: siti con **Schema.org JSON-LD** + **FAQ** chiare hanno più chance di essere “capiti” dagli LLM.  
- **H2 – Locality & Clarity**: contenuti che ripetono **luogo + categoria** migliorano il match semantico.  
- **H3 – Presence Breadth**: presenza su **directory/portali** (TripAdvisor, TheFork, blog locali, associazioni) aumenta la probabilità di citazione.  
- **H4 – Multi-source consistency**: lo **stesso messaggio** ripetuto su più fonti (sito, directory, social) migliora la confidenza del modello.

---

## 📏 Metriche (KPI)
- **Visibility Score (VS)**: indice 0-100 che misura la “leggibilità” dell’entità dagli LLM, basato su:
  - Structuredness (schema.org, FAQ)
  - Topicality (keyword chiare nei titoli/meta)
  - Locality (presenza del luogo)
  - Presence (numero di fonti)
  - Reputation proxy (recensioni, menzioni)
- **Overlap@K**: sovrapposizione tra entità restituite dagli LLM e dal ranking SAIO.  
- **Actionability**: % dei consigli che un cliente può applicare subito.

---

## 🔧 Metodo di test (pipeline)
1. **Baseline LLM**: porre query reali a ChatGPT, Gemini, Copilot; salvare entità/fonti menzionate.  
2. **Scraping**: raccolta contenuti da siti ufficiali, directory e blog.  
3. **Indicizzazione**: salvataggio in Postgres + pgvector/Supabase.  
4. **Feature extraction**: estrazione di segnali (schema.org, FAQ, locality, topicality).  
5. **Ranking**: calcolo Visibility Score.  
6. **Confronto**: comparazione con baseline LLM (Overlap@K).  
7. **Report**: generazione consigli pratici (on-page e off-page).

---

## 🏗️ Architettura MVP

```
/saio
  /apps
    /api        <- FastAPI (ingest, analyze, report)
    /ui         <- Streamlit (dashboard)
  /saio_core
    /graph      <- LangGraph (pipeline orchestrator)
    /scraping   <- spiders/utilities
    /features   <- estrazione segnali
    /ranking    <- scoring + weights
    /storage    <- DB/vector
    /models     <- dataclasses
```

### Stack
- **Backend**: FastAPI  
- **Orchestrazione AI**: LangGraph  
- **UI**: Streamlit  
- **DB**: Supabase Postgres + pgvector  
- **Auth**: Auth0 (non essenziale per MVP)  
- **Embeddings**: OpenAI / Hugging Face

---

## 📚 Case study iniziali

### Case A — “Migliore pizzeria in Zona Solari (Milano)”
- Entità seme: 6-10 pizzerie locali.  
- Fonti: siti ufficiali, TripAdvisor, TheFork, blog.  
- Output: Visibility Score + raccomandazioni (JSON-LD, FAQ, copy).

### Case B — “Aziende italiane di wearable calcistici”
- Entità seme: 6-10 aziende (Soccerment, GPEXE, ecc.).  
- Fonti: siti ufficiali, blog, associazioni di categoria.  
- Output: report con suggerimenti su schema, contenuti tecnici, consistenza terminologica.

---

## ✨ Roadmap
- [ ] MVP: scraping + embeddings + Visibility Score.  
- [ ] Dashboard Streamlit con report e checklist.  
- [ ] Supporto a più domini (food, retail, tech).  
- [ ] Integrazione con API LLM per baseline automatica.  
- [ ] Funzionalità avanzate (contenuti autogenerati, MCP, CRM leggero).

---

## 📌 Risultato atteso
Un prototipo che dimostra come:  
1. Gli LLM si basano su fonti **chiare, strutturate e distribuite**.  
2. È possibile quantificare e migliorare la **visibilità digitale** di un’azienda.  
3. SAIO può fornire un **indice di visibilità** e una **lista di azioni pratiche** a pagamento.
