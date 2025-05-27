# Graph Database Integration Design

## Overview

This document outlines the design, rationale, and use cases for integrating a graph database (Azure Cosmos DB with Gremlin API) into the Made with Nestlé Canada Chatbot project. The goal is to enable advanced, structured queries over the knowledge graph built from scraped website content, allowing the chatbot to answer questions that require explicit reasoning over entities and their relationships.

---

## Purpose of Graph Database in the Chatbot System

- **Explicit Knowledge Representation:**  
  The graph database models products, recipes, articles, brands, and ingredients as nodes. Relationships such as `BELONGS_TO`, `MENTIONS`, and `CONTAINS` represent the connections between them.

- **Advanced Querying and Reasoning:**  
  The graph enables efficient and precise queries, such as:
    - Finding all products for a specific brand.
    - Listing all recipes containing a particular ingredient.
    - Identifying which brands are mentioned in a given article.
    - Retrieving all ingredients shared by multiple recipes.

- **Enhancing Chatbot Responses:**  
  When a user question involves relationships, filtering, or explicit entity attributes, the system can use the graph database to retrieve and present accurate, structured results—either standalone or combined with vector-based semantic search results.

---

## Example Use Cases

| User Question                                     | Retrieval Type | Graph Query Example (Gremlin)                                                |
|---------------------------------------------------|---------------|------------------------------------------------------------------------------|
| Which products contain hazelnuts?                 | Graph         | Find all Product nodes connected to Ingredient "hazelnuts" via CONTAINS edge |
| List all recipes using SMARTIES.                  | Graph         | Find all Recipe nodes mentioning Brand "SMARTIES" or containing "SMARTIES"   |
| What brands are related to Easter recipes?        | Graph         | Traverse from Recipe nodes mentioning "Easter" to related Brand nodes        |
| What ingredients are shared by two or more recipes?| Graph         | Aggregate Ingredient nodes connected to multiple Recipe nodes                 |

---

## Proposed Integration Flow

1. **Intent Detection:**  
   The backend (optionally aided by an LLM) detects when a user's question is best answered by a graph query (e.g., questions about lists, filters, or entity relationships).

2. **Entity Extraction:**  
   The system identifies relevant entities (brands, ingredients, etc.) in the user question.

3. **Parameterized Graph Query:**  
   Using the extracted entities and query intent, the backend constructs a safe, parameterized Gremlin query (no user-controlled code is executed).

4. **Combining with Semantic Retrieval:**  
   For some questions, results from the graph database can be combined with context from vector search, improving both coverage and precision in the chatbot's answers.

---

## Future LLM Integration

- In a full production system, the chatbot could use LLMs (e.g., OpenAI function calling) to:
    - Identify intent and entities from natural language questions.
    - Trigger graph database queries as needed, using safe parameters.
    - Present results from the graph alongside or merged with vector search results.

- This hybrid retrieval-augmented generation (RAG) approach ensures:
    - Conversational, context-rich responses from the LLM.
    - Factual, relationship-based answers from the knowledge graph.

---

## Implementation Note

- Robust, production-level LLM-to-graph query integration requires additional work in prompt engineering, entity/intent extraction, and query validation, which are out of scope for this assessment but described here as a future direction.

---

## References

- [Azure Cosmos DB Gremlin documentation](https://learn.microsoft.com/en-us/azure/cosmos-db/gremlin/)
- [OpenAI Function Calling](https://platform.openai.com/docs/guides/function-calling)
- [Gremlin Language Reference](https://tinkerpop.apache.org/gremlin.html)

---
