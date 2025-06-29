from textblob import TextBlob

def analyze_comment_sentiment(comment_text):
    analysis = TextBlob(comment_text)
    sentiment = analysis.sentiment.polarity  # Range from -1 to 1
    
    # Convert to rating out of 10
    rating = round((sentiment + 1) * 5, 1)
    
    return {
        'sentiment': sentiment,
        'rating': rating,
        'label': 'positive' if sentiment > 0 else 'negative' if sentiment < 0 else 'neutral'
    }