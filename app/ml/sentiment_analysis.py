import torch
import json
import pandas as pd
from transformers import AutoTokenizer, AutoModelForSequenceClassification
from app.core.config import MODEL_PATH, JSON_FILE, PRETRAINED_MODEL, DATA_DIR
import os

def preprocess_text(text, tokenizer, max_length=128):
    """Tokenize the input text"""
    encoded_text = tokenizer.encode_plus(
        text,
        max_length=max_length,
        padding='max_length',
        truncation=True,
        return_tensors='pt'
    )
    
    return encoded_text

def load_sentiment_model(model_path, device, model_name="indolem/indobert-base-uncased", num_labels=3):
    """Load the sentiment analysis model"""
    # Initialize the model
    model = AutoModelForSequenceClassification.from_pretrained(model_name, num_labels=num_labels)
    
    # Load the saved model state
    model.load_state_dict(torch.load(model_path, map_location=device))
    model.to(device)
    
    # Handle DataParallel if needed
    if torch.cuda.device_count() > 1:
        print(f"Using {torch.cuda.device_count()} GPUs!")
        model = torch.nn.DataParallel(model)
        
    model.eval()
    
    return model

def classify_review(review_text, model, tokenizer, device):
    """Classify a single review"""
    # Make sure review_text is a string
    review_text = str(review_text)
    
    # Skip empty strings
    if not review_text.strip():
        return None
        
    try:
        # Preprocess the text
        encoded_review = preprocess_text(review_text, tokenizer)
        
        # Move to device
        input_ids = encoded_review['input_ids'].to(device)
        attention_mask = encoded_review['attention_mask'].to(device)
        
        # Get prediction
        with torch.no_grad():
            outputs = model(input_ids=input_ids, attention_mask=attention_mask)
            logits = outputs.logits
            _, preds = torch.max(logits, dim=1)
        
        # Convert prediction to label - Assuming 3 classes: negative (0), neutral (1), positive (2)
        sentiment_map = {0: "negative", 1: "neutral", 2: "positive"}
        sentiment = sentiment_map[preds.item()]
        
        return sentiment
    except Exception as e:
        print(f"Error processing review: {e}")
        return None

def process_reviews_json():
    """Process JSON file with reviews and classify sentiment"""
    # Set device
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    print(f"Using device: {device}")
    
    # Load the tokenizer
    tokenizer = AutoTokenizer.from_pretrained(PRETRAINED_MODEL)
    
    # Load the model
    model = load_sentiment_model(MODEL_PATH, device, model_name=PRETRAINED_MODEL, num_labels=3)
    
    # Load the JSON file
    print(f"Loading reviews from {JSON_FILE}")
    with open(JSON_FILE, 'r', encoding='utf-8') as f:
        reviews_data = json.load(f)
    
    # Process each review in the JSON file
    results = []
    
    # Determine the structure of the JSON
    if isinstance(reviews_data, list):
        # If it's a list of reviews
        for i, review_item in enumerate(reviews_data):
            # Extract review text based on the structure
            review_text = None
            if isinstance(review_item, dict) and 'review_text' in review_item:
                review_text = review_item['review_text']
            elif isinstance(review_item, dict) and 'review' in review_item:
                review_text = review_item['review']
            elif isinstance(review_item, str):
                review_text = review_item
            
            # Skip null, None, empty strings, or whitespace-only strings
            if review_text is None or not str(review_text).strip():
                print(f"Review {i+1}: Skipping due to null/empty content")
                continue
            
            # Classify the review
            sentiment = classify_review(review_text, model, tokenizer, device)
            print(f"Review {i+1}: {sentiment}")
            
            # Add the result
            if isinstance(review_item, dict):
                review_item['sentiment'] = sentiment
                results.append(review_item)
            else:
                results.append({'text': review_text, 'sentiment': sentiment})
    
    elif isinstance(reviews_data, dict):
        # If it's a dictionary with reviews
        if 'reviews' in reviews_data and isinstance(reviews_data['reviews'], list):
            # Process the list of reviews
            for i, review_item in enumerate(reviews_data['reviews']):
                review_text = None
                if isinstance(review_item, dict) and 'review_text' in review_item:
                    review_text = review_item['review_text']
                elif isinstance(review_item, dict) and 'review' in review_item:
                    review_text = review_item['review']
                elif isinstance(review_item, str):
                    review_text = review_item
                
                # Skip null, None, empty strings, or whitespace-only strings
                if review_text is None or not str(review_text).strip():
                    print(f"Review {i+1}: Skipping due to null/empty content")
                    continue
                
                # Classify the review
                sentiment = classify_review(review_text, model, tokenizer, device)
                print(f"Review {i+1}: {sentiment}")
                
                # Add the result
                if isinstance(review_item, dict):
                    review_item['sentiment'] = sentiment
                    results.append(review_item)
                else:
                    results.append({'text': review_text, 'sentiment': sentiment})
        else:
            # Process each key as a separate review
            for i, (key, value) in enumerate(reviews_data.items()):
                # Skip null values
                if value is None:
                    print(f"Review with key '{key}': Skipping due to null content")
                    continue
                
                review_text = value if isinstance(value, str) else str(value)
                # Skip empty strings or whitespace-only strings
                if not review_text.strip():
                    print(f"Review with key '{key}': Skipping due to empty content")
                    continue
                
                sentiment = classify_review(review_text, model, tokenizer, device)
                print(f"Review {i+1} (key: {key}): {sentiment}")
                results.append({'id': key, 'text': review_text, 'sentiment': sentiment})
    
    # Save the results to a new JSON file
    output_file = os.path.join(DATA_DIR, os.path.basename(JSON_FILE).replace('.json', '_with_sentiment.json'))
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=4)
    
    print(f"Results saved to {output_file}")
    
    return results