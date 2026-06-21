from flask import Flask, render_template, request, jsonify
import joblib
import numpy as np
import pandas as pd
from scrapers import scrape_amazon_data, scrape_croma_data, scrape_reliance_data
import logging
import traceback

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# Load the trained model
try:
    model = joblib.load('price_predictor_model.joblib')
    logger.info("Model loaded successfully from price_predictor_model.joblib")
except Exception as e:
    logger.error(f"Error loading model: {e}")
    model = None

def categorize_product(product_name):
    """Categorize product based on keywords"""
    product_lower = product_name.lower()
    
    # Mobile phones
    mobile_keywords = ['iphone', 'samsung', 'oneplus', 'pixel', 'redmi', 'vivo', 'oppo', 'realme', 
                      'mobile', 'phone', 'smartphone', 'android', 'ios']
    
    # Laptops
    laptop_keywords = ['laptop', 'macbook', 'notebook', 'ultrabook', 'inspiron', 'thinkpad', 'vivobook',
                      'zenbook', 'pavilion', 'omen', 'nitro', 'predator', 'rog', 'legion']
    
    # Earphones/Headphones
    earphone_keywords = ['earphone', 'headphone', 'airpods', 'earbuds', 'headset', 'audio', 'sound', 
                        'jbl', 'boat', 'sony', 'sennheiser']
    
    if any(keyword in product_lower for keyword in mobile_keywords):
        return 'Mobile'
    elif any(keyword in product_lower for keyword in laptop_keywords):
        return 'Laptop'
    elif any(keyword in product_lower for keyword in earphone_keywords):
        return 'Earphones'
    else:
        return 'Other'

def get_available_scrapers(category):
    """Return available scrapers based on category"""
    if category in ['Mobile', 'Laptop', 'Earphones']:
        return {
            'amazon': 'Amazon',
            'croma': 'Croma', 
            'reliance': 'Reliance Digital'
        }
    else:
        return {
            'amazon': 'Amazon'
        }

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/search', methods=['POST'])
def search():
    try:
        product_name = request.form.get('product_name', '').strip()
        category = request.form.get('category', 'Mobile')
        selected_scrapers = request.form.getlist('scrapers')
        
        if not product_name:
            return render_template('results.html', 
                                no_results=True, 
                                product_name=product_name,
                                category=category)
        
        if not model:
            return render_template('results.html',
                                no_results=True,
                                product_name=product_name,
                                category=category,
                                error="Prediction model not available")
        
        logger.info(f"User is searching for: {product_name} in category: {category}")
        
        # Get available scrapers for this category
        available_scrapers = get_available_scrapers(category)
        
        # If no scrapers selected, use default based on category
        if not selected_scrapers:
            if category in ['Mobile', 'Laptop', 'Earphones']:
                selected_scrapers = ['amazon', 'croma', 'reliance']
            else:
                selected_scrapers = ['amazon']
        
        # Run scrapers based on selection
        scraped_data = []
        
        if 'amazon' in selected_scrapers:
            amazon_data = scrape_amazon_data(product_name)
            if amazon_data:
                scraped_data.append(amazon_data)
                logger.info(f"Amazon data: {amazon_data}")
        
        if 'croma' in selected_scrapers and category in ['Mobile', 'Laptop', 'Earphones']:
            croma_data = scrape_croma_data(product_name)
            if croma_data:
                scraped_data.append(croma_data)
                logger.info(f"Croma data: {croma_data}")
        
        if 'reliance' in selected_scrapers and category in ['Mobile', 'Laptop', 'Earphones']:
            reliance_data = scrape_reliance_data(product_name)
            if reliance_data:
                scraped_data.append(reliance_data)
                logger.info(f"Reliance data: {reliance_data}")
        
        if not scraped_data:
            return render_template('results.html',
                                no_results=True,
                                product_name=product_name,
                                category=category)
        
        # Find the best deal (lowest price)
        best_deal = min(scraped_data, key=lambda x: x['price'])
        logger.info(f"Best deal found: {best_deal}")
        
        # Prepare data for AI prediction - EXACTLY like your sample
        try:
            # Create DataFrame with the same structure as your sample
            prediction_data = pd.DataFrame({
                'category': [category],
                'brand': [best_deal['brand']],
                'price': [best_deal['price']],
                'discount_percentage': [best_deal['discount_percentage']],
                'rating': [best_deal['rating']],
                'review_count': [best_deal['review_count']]
            })
            
            logger.info(f"Prediction data: {prediction_data.to_dict()}")
            
            # Make prediction using the model
            predicted_price = model.predict(prediction_data)[0]
            logger.info(f"AI Predicted Price: {predicted_price}")
            
            return render_template('results.html',
                                product_name=product_name,
                                category=category,
                                best_deal=best_deal,
                                predicted_price=predicted_price,
                                all_results=scraped_data,
                                no_results=False)
            
        except Exception as e:
            logger.error(f"Prediction error: {e}")
            logger.error(traceback.format_exc())
            # Fallback: use a simple calculation if model fails
            predicted_price = best_deal['price'] * 0.9  # 10% lower as fallback
            logger.info(f"Using fallback prediction: {predicted_price}")
            
            return render_template('results.html',
                                product_name=product_name,
                                category=category,
                                best_deal=best_deal,
                                predicted_price=predicted_price,
                                all_results=scraped_data,
                                no_results=False)
        
    except Exception as e:
        logger.error(f"Search error: {e}")
        logger.error(traceback.format_exc())
        return render_template('results.html',
                            no_results=True,
                            product_name=product_name,
                            category=category,
                            error="Search failed")

if __name__ == '__main__':
    app.run(debug=True, port=5000)