# Datascience-Task

This repository provides an overview, setup instructions, features, and deployment details for an AI Fashion Assistant Chatbot.

This Chatbot was trained using the E-commerce Product Dataset on Kaggle - https://www.kaggle.com/datasets/aaditshukla/flipkart-fasion-products-dataset/code

## Chatbot Features
✅ Conversational AI Chatbot - Understands user queries and provides intelligent responses.
✅ Product Search by Category & Subcategory - Users can find specific fashion products easily.
✅ Price Range Filtering - Users can filter products based on their budget.
✅ Instant Answers to FAQs - Provides details about return policies, shipping, and payment options.
✅ Fallback to Groq LLM - Uses an AI model to answer open-ended questions.
✅ Streamlit UI with Sidebar Filters - Clean and interactive interface for seamless browsing.

## Technologies Used
- Python - Backend logic
- Streamlit - Web UI framework
- Groq AI (Mixtral-8x7B) - AI-powered responses
- Pandas - Data handling and filtering
- FuzzyWuzzy - Smart product matching for better search
- GitHub - Version control & collaboration

## Installation and Setup
1. Clone this repository
2. Install dependencies found in requirements.txt file
3. Run the chatbot in the terminal using *streamlit run app.py*

## User guide
1. To find Products, ask queries like “Find sneakers under $50” or “Show me jackets”.
2. To explore Categories, type “List all categories” or “List all subcategories”.
3. 	To ask FAQs, see example queries:
	•	“What is the return policy?”
	•	“Do you offer international shipping?”
	•	“What payment methods do you accept?”
4. Fallback to AI: If the query is not found, the bot will use Groq AI to generate an intelligent response.
