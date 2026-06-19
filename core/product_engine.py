import pandas as pd
import pandasql
import logging

logger = logging.getLogger("ProductEngine")

def list_all_products(products_df):
    """
    Returns a markdown table of the first 20 products.
    """
    if products_df is None or products_df.empty:
        return "⚠️ The product catalog is empty or has not been loaded."
        
    try:
        # Run query using pandasql
        query = "SELECT name, brand, price, rating FROM products_df LIMIT 20"
        result_df = pandasql.sqldf(query, {"products_df": products_df})
        
        if result_df.empty:
            return "No products found in the catalog."
            
        # Format results as a markdown table
        markdown = "### 📦 Product List (Top 20)\n\n"
        markdown += "| Name | Brand | Price (₹) | Rating |\n"
        markdown += "| :--- | :--- | :--- | :--- |\n"
        for _, row in result_df.iterrows():
            markdown += f"| {row['name']} | {row['brand']} | ₹{row['price']} | {row['rating']} ★ |\n"
        return markdown
        
    except Exception as e:
        logger.error(f"Error querying product list: {e}")
        return f"⚠️ Error fetching products: {e}"

def search_product(products_df, search_term):
    """
    Searches for products matching the search_term in name or brand.
    Returns a formatted markdown text of matching products.
    """
    if products_df is None or products_df.empty:
        return "⚠️ The product catalog is empty or has not been loaded."
        
    if not search_term or not search_term.strip():
        return "Please enter a valid search keyword. (e.g. `/search Sneaker`)"
        
    try:
        search_pattern = f"%{search_term.strip()}%"
        # Run query using pandasql
        query = """
            SELECT name, brand, price, rating, description 
            FROM products_df 
            WHERE name LIKE :search_pattern 
               OR brand LIKE :search_pattern 
               OR category LIKE :search_pattern
        """
        result_df = pandasql.sqldf(query, {"products_df": products_df, "search_pattern": search_pattern})
        
        if result_df.empty:
            return f"No products found matching **'{search_term}'**."
            
        markdown = f"### 🔍 Search Results for: '{search_term}'\n\n"
        for idx, row in result_df.iterrows():
            markdown += f"**{idx+1}. {row['name']}**\n"
            markdown += f"- **Brand**: {row['brand']}\n"
            markdown += f"- **Price**: ₹{row['price']}\n"
            markdown += f"- **Rating**: {row['rating']} ★\n"
            markdown += f"- **Description**: {row['description']}\n\n"
            markdown += "---\n\n"
        return markdown
        
    except Exception as e:
        logger.error(f"Error searching product: {e}")
        return f"⚠️ Error searching products: {e}"
