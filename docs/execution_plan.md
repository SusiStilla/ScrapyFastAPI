# Execution Plan for FastAPI + Crawler Project

## 1. Project Overview  
This project is designed as a combination of a **FastAPI-based API layer** and a **crawler pipeline**.  
- **Goal**: Accept user-submitted URLs via an API endpoint and launch an intelligent crawler pipeline (`SitemapFirstSpider`) to discover and extract website content.  
- **Outcome**: Generate structured, high-quality text data stored in JSONL format with metadata for downstream processing.

---

## 2. API Layer (FastAPI)

- **Endpoint**:  
  - `POST /submit-url`  

- **Request Validation**:  
  - Use Pydantic models to validate required URL field.  
  - Normalize URLs (ensure scheme handling for `http`/`https`, remove trailing slashes, lowercase hostname).  

- **Execution Flow**:  
  - If validation is successful, enqueue the URL for crawling.  
  - Trigger the crawler job as an asynchronous task (can be executed as a background task, Celery job, or Lambda depending on deployment).

---

## 3. Crawler Execution Flow (SitemapFirstSpider)

### **URL Preprocessing**  
- Enforce `http://` or `https://` scheme.  
- Normalize the domain format (strip redundant `www`, lowercase, enforce canonical form).  

### **Sitemap Discovery**  
Attempt (in order of priority):  
1. `/robots.txt` (check for `Sitemap:` declaration).  
2. `/sitemap.xml`  
3. `/sitemap_index.xml`  
4. `/sitemap-index.xml`  

If no sitemap found → fallback to intelligent link discovery.

### **Domain & Path Constraints**  
- Configurable **subdomain inclusion/exclusion**.  
- Crawling restricted to given **path prefixes**.  
- Consistent URL normalization (remove query duplicates, tracking params, enforce canonical).

---

## 4. Crawler Capabilities

- **Intelligent Site Discovery**:  
  - Prioritize sitemap parsing.  
  - Enforce `robots.txt` compliance.  
  - Fallback: internal link discovery.  
  - Respect canonical tags for content deduplication.  

- **Content Extraction Strategies**:  
  - Use [trafilatura](https://github.com/adbar/trafilatura) if present for high-quality boilerplate removal.  
  - Fallback extraction via XPath and HTML parsing.  

- **Structured Data Handling**:  
  - Extract Schema.org structured data (JSON-LD, microdata, RDFa).  
  - Store alongside textual content for downstream semantic tasks.

---

## 5. Output Specification  
Each crawled page emits one JSON record into a **JSONL file**.  

Example output schema:  

```json
{
  "url": "https://example.com/page",
  "title": "Page Title",
  "text": "Extracted clean content...",
  "status": 200,
  "content_type": "text/html; charset=utf-8",
  "fetched_at": "2024-01-15T10:30:00Z",
  "sitemap_lastmod": "2024-01-10T08:00:00Z"
}
```

---

## 6. Execution Plan & Next Steps  

### **Implementation Milestones**:  
1. **API Development**  
   - Implement `/submit-url` in FastAPI with Pydantic validation.  
   - Normalize input URLs.  

2. **Crawler Integration**  
   - Develop `SitemapFirstSpider` with preprocessing and sitemap-first discovery.  
   - Add domain & path constraint mechanisms.  

3. **Content Extraction**  
   - Implement trafilatura-based extraction.  
   - Add XPath fallbacks and structured data handling.  

4. **Output Management**  
   - Define JSONL writing pipeline with standardized schema.  
   - Ensure timestamps and metadata are included.  

5. **Testing & Validation**  
   - Unit tests for API input validation.  
   - Integration tests for crawler workflows across multiple domains.  

6. **Deployment Strategy**  
   - Local Docker-based execution.  
   - Optionally extend with Celery queue or AWS Lambda for distributed execution.  

---