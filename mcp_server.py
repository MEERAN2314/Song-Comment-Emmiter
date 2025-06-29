from flask import Flask, request, jsonify
from flask_cors import CORS
from pymongo import MongoClient
from dotenv import load_dotenv
import os

load_dotenv()

app = Flask(__name__)
CORS(app)

# MongoDB connection
client = MongoClient(
    os.getenv("MONGODB_URI"),
    serverSelectionTimeoutMS=5000,  # 5 second timeout
    socketTimeoutMS=30000,  # 30 second socket timeout
    connectTimeoutMS=30000  # 30 second connection timeout
)
db = client[os.getenv("DB_NAME")]
comments_collection = db['song_comments']

@app.route('/store_comments', methods=['POST'])
def store_comments():
    data = request.json
    try:
        result = comments_collection.insert_many(data['comments'])
        return jsonify({
            "status": "success",
            "inserted_ids": len(result.inserted_ids)
        }), 200
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500

@app.route('/get_comments', methods=['GET'])
def get_comments():
    try:
        song_id = request.args.get('song_id')
        limit = int(request.args.get('limit', 10))
        sort_by = request.args.get('sort_by', 'rating')
        
        query = {"song_id": song_id}
        comments = list(comments_collection.find(query, {'_id': 0}))
        
        # Sort comments
        if sort_by == 'rating':
            comments.sort(key=lambda x: x['rating'], reverse=True)
        elif sort_by == 'positive':
            comments.sort(key=lambda x: x['sentiment'], reverse=True)
        elif sort_by == 'negative':
            comments.sort(key=lambda x: x['sentiment'])
        
        return jsonify({
            "status": "success",
            "comments": comments[:limit]
        }), 200
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)