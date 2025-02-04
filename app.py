import streamlit as st

# ✅ Set Streamlit page config as the first command
st.set_page_config(page_title="AI Fashion Assistant-Lily!", page_icon="🛍️", layout="wide")
import pandas as pd
import groq
import os
from fuzzywuzzy import process


# Load dataset
df = pd.read_csv("cleaned_output.csv")

# Ensure column names are lowercase
df["category"] = df["category"].astype(str).str.lower()
df["sub_category"] = df["sub_category"].astype(str).str.lower()
df["title"] = df["title"].astype(str).str.lower()

# Set up Groq API Key
groq_api_key = "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"
client = groq.Client(api_key=groq_api_key)

# ✅ Predefined FAQs for the e-commerce website
faq_responses = {
    "return policy": "📦 You can return items within 30 days for a full refund. Visit our 'Returns & Refunds' page for more details.",
    "shipping": "🚚 We offer free shipping for orders above $50. Standard delivery takes 3-5 business days.",
    "international shipping": "🌍 Yes! We ship worldwide, but shipping fees may vary based on your location.",
    "payment methods": "💳 We accept Visa, Mastercard, PayPal, Klana, and Apple Pay.",
    "order tracking": "📦 You can track your order by logging into your account and visiting the 'Track Order' section.",
    "customer support": "📞 You can contact our customer support at support@fashionstore.com or call +1 800 123 4567.",
}

# Function to query Groq's LLM
def query_groq(prompt, model="mixtral-8x7b"):
    response = client.chat.completions.create(
        model=model,
        messages=[{"role": "system", "content": "You are an AI shopping assistant."},
                  {"role": "user", "content": prompt}]
    )
    return response.choices[0].message.content.strip()

# Function to find the closest category/subcategory match
def find_best_match(query, choices, threshold=70):
    best_match, score = process.extractOne(query, choices)
    return best_match if score >= threshold else None

# Function to retrieve products with filtering
def find_products(category=None, subcategory=None, min_price=0, max_price=999999, limit=5):
    product_id_column = None
    for col in ["product_id", "id", "pid", "product_code"]:
        if col in df.columns:
            product_id_column = col
            break

    if product_id_column is None:
        return "❌ No valid product ID column found in dataset."

    if subcategory:
        results = df[df["sub_category"].str.contains(subcategory, case=False, na=False)]
    elif category:
        results = df[df["category"].str.contains(category, case=False, na=False)]
    else:
        return " Kindly specify a category or subcategory."

    # Apply price range filter
    results = results[(results["selling_price"] >= min_price) & (results["selling_price"] <= max_price)]

    if results.empty:
        return f"❌ No products found for '{subcategory if subcategory else category}' in this price range."

    return results[[product_id_column, "title", "selling_price"]].head(limit).to_dict(orient="records"), product_id_column

# Function to handle user queries (Products + FAQs + LLM)
def handle_query(user_query, min_price=0, max_price=999999):
    query_lower = user_query.lower()

    # ✅ Check if the query matches any FAQ key
    for keyword in faq_responses.keys():
        if keyword in query_lower:
            return faq_responses[keyword]

    # ✅ Handle category & subcategory searches
    if "categories" in query_lower:
        return {"Categories": list(df["category"].unique())}

    elif "subcategories" in query_lower:
        return {"Subcategories": list(df["sub_category"].unique())}

    elif "find" in query_lower or "show me" in query_lower:
        category_match = find_best_match(query_lower, df["category"].unique())
        subcategory_match = find_best_match(query_lower, df["sub_category"].unique())

        if subcategory_match:
            return find_products(subcategory=subcategory_match, min_price=min_price, max_price=max_price)
        elif category_match:
            return find_products(category=category_match, min_price=min_price, max_price=max_price)
        else:
            return "❌ No matching products found. Try searching by category or subcategory."

    # ✅ If no match, fallback to Groq AI model
    return query_groq(user_query)

# ---------------- UI Enhancements ---------------- #

# Sidebar Navigation
st.sidebar.title("🛍️ AI Fashion Assistant- Lily!")
st.sidebar.write("Ask Lily anything about fashion!")

# Sidebar - Price Range Filter
st.sidebar.subheader("💰 Filter by Price")
min_price = st.sidebar.slider("Min Price ($)", 0, 500, 0)
max_price = st.sidebar.slider("Max Price ($)", 10, 1000, 1000)

# Sidebar - Category selection
if st.sidebar.button("Show Categories"):
    st.sidebar.write("📌 Available Categories:")
    st.sidebar.write(list(df["category"].unique()))

# Sidebar - Subcategory selection
if st.sidebar.button("Show Subcategories"):
    st.sidebar.write("📌 Available Subcategories:")
    st.sidebar.write(list(df["sub_category"].unique()))

# Main Chat Area
st.markdown("<h1 style='text-align: center; color: #ff4b4b;'>AI Fashion Assistant-Lily! 🛍️</h1>", unsafe_allow_html=True)
st.write("**Ask me about fashion products, brands, categories, and return policies!**")

# ✅ User Chat Input
user_query = st.text_input("👤 Type your query:", placeholder="E.g., 'Find sneakers under $50'")

if st.button("Ask"):
    response = handle_query(user_query, min_price, max_price)

    with st.chat_message("user"):
        st.write(f"👤 {user_query}")

    with st.chat_message("assistant"):
        if isinstance(response, dict):  # Categories or subcategories
            st.write(response)
        elif isinstance(response, tuple):  # ✅ Product recommendations
            product_list, product_id_column = response
            st.write("✨ **Here are some matching products:**")
            for product in product_list:
                st.write(f"🔹 **{product['title']}** - 💰 **${product['selling_price']}** (ID: {product[product_id_column]})")
        else:
            st.write(response)  # ✅ FAQ or LLM response

# Footer
st.markdown("<h6 style='text-align: center;'>Powered by <b>Groq AI</b> | Developed by <b>Your Name</b> 🚀</h6>", unsafe_allow_html=True)


# # Function to query Groq's LLM
# def query_groq(prompt, model="mixtral-8x7b"):
#     response = client.chat.completions.create(
#         model=model,
#         messages=[{"role": "system", "content": "You are an AI shopping assistant."},
#                   {"role": "user", "content": prompt}]
#     )
#     return response.choices[0].message.content.strip()

# # Function to find the closest category/subcategory match
# def find_best_match(query, choices, threshold=70):
#     best_match, score = process.extractOne(query, choices)
#     return best_match if score >= threshold else None

# # Function to retrieve products with filtering
# def find_products(category=None, subcategory=None, min_price=0, max_price=999999, limit=5):
#     product_id_column = "product_id" if "product_id" in df.columns else "id" if "id" in df.columns else "pid"

#     if subcategory:
#         results = df[df["sub_category"].str.contains(subcategory, case=False, na=False)]
#     elif category:
#         results = df[df["category"].str.contains(category, case=False, na=False)]
#     else:
#         return "❌ Please specify a category or subcategory."

#     # Apply price range filter
#     results = results[(results["selling_price"] >= min_price) & (results["selling_price"] <= max_price)]

#     if results.empty:
#         return f"❌ No products found for '{subcategory if subcategory else category}' in this price range."

#     return results[[product_id_column, "title", "selling_price"]].head(limit).to_dict(orient="records")

# # Function to handle user queries
# def handle_query(user_query, min_price=0, max_price=999999):
#     query_lower = user_query.lower()

#     if "categories" in query_lower:
#         return {"Categories": list(df["category"].unique())}

#     elif "subcategories" in query_lower:
#         return {"Subcategories": list(df["sub_category"].unique())}

#     elif "find" in query_lower or "show me" in query_lower:
#         category_match = find_best_match(query_lower, df["category"].unique())
#         subcategory_match = find_best_match(query_lower, df["sub_category"].unique())

#         if subcategory_match:
#             return find_products(subcategory=subcategory_match, min_price=min_price, max_price=max_price)
#         elif category_match:
#             return find_products(category=category_match, min_price=min_price, max_price=max_price)
#         else:
#             return "❌ No matching products found. Try searching by category or subcategory."

#     else:
#         return query_groq(user_query)

# # ---------------- UI Enhancements ---------------- #

# # Sidebar Navigation
# st.sidebar.title("🛍️ AI Fashion Assistant")
# st.sidebar.write("Ask Lily anything about fashion!")

# # Sidebar - Price Range Filter
# st.sidebar.subheader("💰 Filter by Price")
# min_price = st.sidebar.slider("Min Price ($)", 0, 500, 0)
# max_price = st.sidebar.slider("Max Price ($)", 10, 1000, 1000)

# # Sidebar - Category selection
# if st.sidebar.button("Show Categories"):
#     st.sidebar.write("📌 Available Categories:")
#     st.sidebar.write(list(df["category"].unique()))

# # Sidebar - Subcategory selection
# if st.sidebar.button("Show Subcategories"):
#     st.sidebar.write("📌 Available Subcategories:")
#     st.sidebar.write(list(df["sub_category"].unique()))

# # Main Chat Area
# st.markdown("<h1 style='text-align: center; color: #ff4b4b;'>AI Fashion Assistant 🛍️</h1>", unsafe_allow_html=True)
# st.write("**Ask me about fashion products, brands, categories, and return policies!**")

# # User Chat Input
# user_query = st.text_input("👤 Type your query:", placeholder="E.g., 'Find sneakers under $50'")

# if st.button("Ask"):
#     response = handle_query(user_query, min_price, max_price)

#     with st.chat_message("user"):
#         st.write(f"👤 {user_query}")

#     with st.chat_message("assistant"):
#         if isinstance(response, dict):  # Categories or subcategories
#             st.write(response)
#         elif isinstance(response, list):  # Product recommendations (without images)
#             st.write("✨ **Here are some matching products:**")
#             for product in response:
#                 st.write(f"🔹 **{product['title']}** - 💰 **${product['selling_price']}** (ID: {product['pid']})")
#         else:
#             st.write(response)  # General LLM response
# st.markdown("<h6 style='text-align: center;'>Powered by <b>Groq AI</b> | Developed by <b>Your Name</b> 🚀</h6>", unsafe_allow_html=True)
























# # Load dataset
# df = pd.read_csv("cleaned_output.csv")

# # Convert text columns to lowercase for consistency
# df["category"] = df["category"].astype(str).str.lower()
# df["sub_category"] = df["sub_category"].astype(str).str.lower()
# df["title"] = df["title"].astype(str).str.lower()

# # Set up Groq API Key (Replace with your actual key)
# groq_api_key = "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"

# # Initialize Groq client
# client = groq.Client(api_key=groq_api_key)

# # Function to query Groq's LLM for intent recognition
# def query_groq(prompt, model="mixtral-8x7b"):
#     response = client.chat.completions.create(
#         model=model,
#         messages=[{"role": "system", "content": "You are an AI shopping assistant."},
#                   {"role": "user", "content": prompt}]
#     )
#     return response.choices[0].message.content.strip()

# # Function to find the closest category or subcategory match using fuzzy matching
# def find_best_match(query, choices, threshold=70):
#     best_match, score = process.extractOne(query, choices)
#     return best_match if score >= threshold else None

# # Function to retrieve products based on category or subcategory
# def find_products(category=None, subcategory=None, limit=5):
#     product_id_column = "product_id" if "product_id" in df.columns else "id" if "id" in df.columns else "pid"

#     if subcategory:
#         results = df[df["sub_category"].str.contains(subcategory, case=False, na=False)]
#     elif category:
#         results = df[df["category"].str.contains(category, case=False, na=False)]
#     else:
#         return "❌ Please specify a category or subcategory."

#     if results.empty:
#         return f"❌ No products found for '{subcategory if subcategory else category}'. Try another search."

#     return results[[product_id_column, "title", "selling_price", ]].head(limit).to_dict(orient="records")

# # Function to handle user queries
# def handle_query(user_query):
#     query_lower = user_query.lower()

#     if "categories" in query_lower:
#         return {"Categories": list(df["category"].unique())}

#     elif "subcategories" in query_lower or "sub_categories" in query_lower:
#         return {"Subcategories": list(df["sub_category"].unique())}

#     elif "find" in query_lower or "show me" in query_lower:
#         category_match = find_best_match(query_lower, df["category"].unique())
#         subcategory_match = find_best_match(query_lower, df["sub_category"].unique())

#         if subcategory_match:
#             return find_products(subcategory=subcategory_match)
#         elif category_match:
#             return find_products(category=category_match)
#         else:
#             return "No matching products found. Try searching by category or subcategory."

#     else:
#         return query_groq(user_query)

# # ---------------- UI Enhancements ---------------- #

# # Sidebar Navigation
# st.sidebar.title("🛍️ AI Fashion Assistant-Lily")
# st.sidebar.subheader("Navigate")
# st.sidebar.write("Ask Lily anything about fashion!")

# # Sidebar - Category selection
# if st.sidebar.button("Show Categories", key="categories_button"):
#     st.sidebar.write("📌 Available Categories:")
#     st.sidebar.write(list(df["category"].unique()))

# # Sidebar - Subcategory selection
# if st.sidebar.button("Show Subcategories", key="subcategories_button"):
#     st.sidebar.write("📌 Available Subcategories:")
#     st.sidebar.write(list(df["sub_category"].unique()))

# # Main Chat Area
# st.markdown("<h1 style='text-align: center; color: #ff4b4b;'>AI Fashion Assistant-Lily 🛍️</h1>", unsafe_allow_html=True)
# st.write("**Ask me about fashion products, brands, categories, and return policies!**")

# # User Chat Input
# user_query = st.text_input("👤 Type your query:", placeholder="E.g., 'Find sneakers under $50'")

# if st.button("Ask", key="ask_button"):
#     response = handle_query(user_query)

#     # Chat Message Format
#     with st.chat_message("user"):
#         st.write(f"👤 {user_query}")

#     with st.chat_message("assistant"):
#         if isinstance(response, dict):  # If response is a dictionary (categories/subcategories)
#             st.write(response)
#         elif isinstance(response, list):  # If response is product recommendations
#             st.write("✨ **Here are some matching products:**")
#             for product in response:
#                 st.write(f"🔹 **{product['title']}** - 💰 **${product['selling_price']}** (ID: {product['product_id']})")
#         else:
#             st.write(response)  # Display general text responses

# # Footer
# st.markdown("<h6 style='text-align: center;'>Powered by <b>Groq AI</b> | Developed by <b>Your Name</b> 🚀</h6>", unsafe_allow_html=True)














# Load dataset
# df = pd.read_csv("cleaned_output.csv")

# # Convert text columns to lowercase for consistency
# df["category"] = df["category"].astype(str).str.lower()
# df["sub_category"] = df["sub_category"].astype(str).str.lower()
# df["title"] = df["title"].astype(str).str.lower()

# Set up Groq API Key (Replace with your actual key)
# groq_api_key = "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"

# # Initialize Groq client
# client = groq.Client(api_key=groq_api_key)

# # Function to query Groq's LLM for intent recognition
# def query_groq(prompt, model="mixtral-8x7b"):
#     """
#     Queries Groq's LLM and returns the response.
#     """
#     response = client.chat.completions.create(
#         model=model,
#         messages=[{"role": "system", "content": "You are an AI shopping assistant."},
#                   {"role": "user", "content": prompt}]
#     )
#     return response.choices[0].message.content.strip().lower()

# # Function to find the closest category or subcategory match using fuzzy matching
# def find_best_match(query, choices, threshold=70):
#     """
#     Uses fuzzy matching to find the best match in a list of choices.
#     """
#     best_match, score = process.extractOne(query, choices)
#     return best_match if score >= threshold else None

# # Function to retrieve products based on category or subcategory
# def find_products(category=None, subcategory=None, limit=5):
#     """
#     Finds up to 5 products based on category or subcategory.
#     """
#     product_id_column = "product_id" if "product_id" in df.columns else "id" if "id" in df.columns else "pid"

#     if subcategory:  # Searching by subcategory
#         results = df[df["sub_category"].str.contains(subcategory, case=False, na=False)]
#     elif category:  # Searching by category
#         results = df[df["category"].str.contains(category, case=False, na=False)]
#     else:
#         return "Please specify a category or subcategory."

#     if results.empty:
#         return f"No products found for '{subcategory if subcategory else category}'. Try another search."

#     return results[[product_id_column, "title", "selling_price"]].head(limit).to_dict(orient="records")

# # Function to handle user queries
# def handle_query(user_query):
#     """
#     Determines if the query should be handled by the dataset or sent to Groq's LLM.
#     """
#     query_lower = user_query.lower()

#     # Fix: Return correct list of subcategories
#     if "categories" in query_lower:
#         return {"Categories": list(df["category"].unique())}

#     elif "subcategories" in query_lower or "sub_categories" in query_lower:
#         return {"Subcategories": list(df["sub_category"].unique())}  # Fix: Correctly return subcategories

#     # Check if query is about finding a product (fuzzy matching for better accuracy)
#     elif "find" in query_lower or "show me" in query_lower:
#         words = query_lower.split()

#         # Use fuzzy matching to find the closest category or subcategory
#         category_match = find_best_match(query_lower, df["category"].unique())
#         subcategory_match = find_best_match(query_lower, df["sub_category"].unique())

#         if subcategory_match:
#             return find_products(subcategory=subcategory_match)
#         elif category_match:
#             return find_products(category=category_match)
#         else:
#             return "No matching products found. Try searching by category or subcategory."

#     # Otherwise, send query to Groq's LLM for general responses
#     else:
#         return query_groq(user_query)

# # Streamlit UI
# st.title("🛍️ AI Fashion Assistant (Powered by Groq)")
# st.write("Ask me about fashion products, brands, categories, subcategories, and return policies!")

# # User Input
# user_query = st.text_input("👤 Type your query:")

# if st.button("Ask"):
#     response = handle_query(user_query)

#     if isinstance(response, dict):  # If response is a dictionary (e.g., categories or subcategories)
#         st.write(response)
#     elif isinstance(response, list):  # If response is product recommendations
#         st.write("✨ Here are some matching products:")
#         for product in response:
#             st.write(f"🔹 **{product['title']}** - 💰 ${product['selling_price']} (ID: {product['product_id']})")
#     else:
#         st.write(response)  # Display text responses

# #Improve the streamlit UI
# # Set page config
# #st.set_page_config(page_title="AI Fashion Assistant -Lily!", page_icon="🛍️", layout="wide")

# # Sidebar Navigation
# st.sidebar.title("🛍️ AI Fashion Assistant")
# st.sidebar.subheader("Navigate")
# st.sidebar.write("Ask the Lily anything about fashion!")

# # Sidebar - Category selection
# if st.sidebar.button("Show Categories"):
#     st.sidebar.write("📌 Available Categories:")
#     st.sidebar.write(list(df["category"].unique()))

# # Sidebar - Subcategory selection
# if st.sidebar.button("Show Subcategories"):
#     st.sidebar.write("📌 Available Subcategories:")
#     st.sidebar.write(list(df["sub_category"].unique()))

# # Main Chat Area
# st.markdown("<h1 style='text-align: center; color: #ff4b4b;'>AI Fashion Assistant 🛍️</h1>", unsafe_allow_html=True)
# st.write("**Ask me about fashion products, brands, categories, and return policies!**")

# # User Chat Input
# user_query = st.text_input("👤 Type your query:", placeholder="E.g., 'Find sneakers under $50'")

# if st.button("Ask"):
#     response = handle_query(user_query)

#     # Chat Message Format
#     with st.chat_message("user"):
#         st.write(f"👤 {user_query}")

#     with st.chat_message("assistant"):
#         if isinstance(response, dict):  # If response is a dictionary (categories/subcategories)
#             st.write(response)
#         elif isinstance(response, list):  # If response is product recommendations
#             st.write("✨ **Here are some matching products:**")
#             for product in response:
#                 st.write(f"🔹 **{product['title']}** - 💰 **${product['selling_price']}** (ID: {product['product_id']})")
#         else:
#             st.write(response)  # Display general text responses

# # Footer
# st.markdown("<h6 style='text-align: center;'>Powered by <b>Groq AI</b> | Developed by <b>Your Name</b> 🚀</h6>", unsafe_allow_html=True)