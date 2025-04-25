from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from newspaper import Article
from textblob import TextBlob
import logging
import os

app = Flask(__name__, static_folder='.', static_url_path='')
CORS(app)
logging.basicConfig(level=logging.DEBUG)

@app.route('/', methods=['GET'])
def serve_index():
    return send_from_directory('.', 'index.html')

@app.route('/analyze', methods=['POST'])
def analyze():
    try:
        data = request.get_json()
        app.logger.debug(f"Received request: {data}")
        url = data.get('url')
        if not url:
            return jsonify({'error': 'No URL provided'}), 400

        article = Article(url)
        article.download()
        article.parse()
        article.nlp()

        if not article.text:
            return jsonify({'error': 'Unable to fetch article content'}), 400

        analysis = TextBlob(article.text)
        polarity = round(analysis.polarity, 2)
        sentiment = 'Positive' if polarity > 0 else 'Negative' if polarity < 0 else 'Neutral'
        subjectivity = analysis.subjectivity
        bias = 'Low' if subjectivity < 0.3 else 'Moderate' if subjectivity < 0.7 else 'High'
        credibility = 'True' if subjectivity < 0.5 else 'False'

        word_count = len(article.text.split())
        reading_time = f"{round(word_count / 200)} min read"

        response = {
            'title': article.title or 'N/A',
            'author': ', '.join(article.authors) if article.authors else 'N/A',
            'summary': article.summary or 'N/A',
            'sentiment': sentiment,
            'polarity': polarity,
            'bias': bias,
            'credibility': credibility,
            'word_count': word_count,
            'reading_time': reading_time
        }
        return jsonify(response), 200

    except Exception as e:
        app.logger.error(f"Error analyzing article: {str(e)}")
        return jsonify({'error': f'Failed to analyze article: {str(e)}'}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=3000, debug=True)