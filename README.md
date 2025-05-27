# Made with Nestlé AI Chatbot — Technical Assessment

## Table of Contents
- [Project Overview](#project-overview)
- [Features](#features)
- [System Architecture](#system-architecture)
- [Technologies Used](#technologies-used)
- [Setup and Deployment](#setup-and-deployment)
- [Usage](#usage)
- [Codebase Structure](#codebase-structure)
- [Known Limitations / Out-of-Scope Features](#known-limitations--out-of-scope-features)
- [Future Enhancements](#future-enhancements)
- [Contact](#contact)

---

## Project Overview

This project implements an AI-powered chatbot for the [Made with Nestlé Canada website](https://www.madewithnestle.ca/). The chatbot answers user queries using site content, employing web scraping, semantic search with a vector database, and large language model (LLM) generation. Both backend and frontend are deployed on Microsoft Azure.

---

## Features

- Web scraping of products, recipes, and articles.
- Content ingestion and semantic search using Pinecone vector database.
- Retrieval-augmented answer generation using OpenAI GPT models.
- User-facing React chatbot interface with pop-out feature and branding.
- Azure-based deployment (App Service for backend, Static Web App for frontend).
- CORS and environment variable support for secure operations.

---

## System Architecture

1. **Scraping**:  
   Python scripts extract products, recipes, and articles from the website.

2. **Vector Database**:  
   Extracted content is embedded and stored in Pinecone with relevant metadata.

3. **Backend**:  
   FastAPI server accepts user queries, searches Pinecone for relevant context, and calls the OpenAI API for final answer generation.

4. **Frontend**:  
   React app displays the chatbot in the lower-right corner, layered over a screenshot background, and communicates with the backend API.

---

## Technologies Used

- **Python 3.11** — backend and scraping
- **Selenium, BeautifulSoup** — scraping
- **Pinecone** — vector database for semantic search
- **OpenAI API** — language model for answer generation
- **FastAPI** — backend web framework
- **React** — frontend chatbot UI
- **Azure App Service** — backend hosting
- **Azure Static Web Apps** — frontend hosting

---

## Setup and Deployment

### Local Setup

**Prerequisites:**  
- Python 3.11  
- Node.js and npm  
- Azure account (for cloud deployment)

#### Backend

1. Clone the repository:
    ```bash
    git clone <repo-url>
    ```

2. Set environment variables in a `.env` file:
    ```
    PINECONE_API_KEY=your_pinecone_api_key
    PINECONE_HOST=your_pinecone_host
    OPENAI_API_KEY=your_openai_api_key
    ```

3. Install dependencies:
    ```bash
    pip install -r requirements.txt
    pip install -r requirements-dev.txt (for web scraping)
    ```

4. Run the backend server:
    ```bash
    python -m uvicorn app.main:app --reload
    ```

#### Frontend

1. Navigate to the frontend folder:
    ```bash
    cd ../nestle-chatbot-frontend
    ```

2. Set environment variables in a `.env` file in ../nestle-chatbot-frontend:
    ```
    REACT_APP_API_URL=http://localhost:8000
    ```

3. Install dependencies:
    ```bash
    npm install
    ```

4. Build the frontend:
    ```bash
    npm run build
    ```

5. Serve locally (for development):
    ```bash
    npm start
    ```

### Azure Deployment

#### Backend

- Deploy using Azure App Service (Python Linux).
- Configure environment variables via Azure portal.
- Add the Azure remote to your local git repo.
  Azure provides a unique git URL for your App Service (find it under “Deployment Center” > “Settings”).
  ```bash
    git remote add azure https://<azure-git-url>
  ```
- Push code updates:
    ```bash
    git push azure main:master
    ```

#### Frontend

- Deploy using Azure Static Web Apps.
- Connect to your GitHub repo for automatic deployment.
- Static assets (e.g., icons, background) are in `/public` and `/build`.

---

## Usage

- Visit the deployed frontend: [Frontend URL](https://salmon-pond-0ce065a0f.6.azurestaticapps.net)
- The chatbot icon appears in the lower-right corner.
- Click to open and enter questions about Made with Nestlé content.
- Answers reference actual site content and provide URLs when relevant.

---

## Known Limitations / Out-of-Scope Features

- Only main site content (products, recipes, articles) is scraped; other types are excluded.
- Does not parse or store all images or tables; focuses on text content for search and answers.
- No automation for real-time or periodic scraping (scraping scripts are run manually).
- Error logging, scaling, and production monitoring are minimal (assessment scope).
- GraphRAG/GraphDB integration is not yet implemented (see Future Enhancements).

---

## Future Enhancements

- Add integration with a graph database (Azure Cosmos DB with Gremlin API) to enable advanced, structured queries
(e.g., "Which products contain hazelnuts?" or "List all recipes using SMARTIES"). The design for this graph module and potential LLM integration is provided in [GRAPHDB.md](GRAPHDB.md).
- Expand scraping coverage to all potential content types.
- Improve the chatbot UI with additional features and mobile responsiveness.
- Improve system prompt for security and higher accuracy
- Automate content updates for real-time accuracy.
- Add comprehensive error handling and monitoring for production.

---
