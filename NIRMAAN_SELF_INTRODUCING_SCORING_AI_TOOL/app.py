from flask import Flask, request, jsonify
from flask_cors import CORS
import re
from collections import Counter
import language_tool_python
from textblob import TextBlob
import math

app = Flask(__name__)
CORS(app)

# Initialize grammar checker (singleton pattern)
grammar_tool = None

def get_grammar_tool():
    global grammar_tool
    if grammar_tool is None:
        grammar_tool = language_tool_python.LanguageTool('en-US')
    return grammar_tool

class SpeechAnalyzer:
    def __init__(self, transcript, duration_seconds=52):
        self.transcript = transcript.strip()
        self.duration_seconds = duration_seconds
        self.words = self.transcript.lower().split()
        self.word_count = len(self.words)
        self.sentences = [s.strip() for s in re.split(r'[.!?]+', self.transcript) if s.strip()]
        self.sentence_count = len(self.sentences)
        
        # Filler words list
        self.filler_words = [
            'um', 'uh', 'like', 'you know', 'so', 'actually', 'basically', 
            'right', 'i mean', 'well', 'kinda', 'sort of', 'okay', 'hmm', 'ah'
        ]
    
    def calculate_wpm(self):
        """Calculate words per minute"""
        if self.duration_seconds > 0:
            return round((self.word_count / self.duration_seconds) * 60, 2)
        return 0
    
    def analyze_salutation(self):
        """Analyze salutation and return score"""
        first_sentence = self.sentences[0].lower() if self.sentences else ""
        
        excellent_phrases = ['excited to introduce', 'feeling great', 'pleasure to introduce']
        good_phrases = ['good morning', 'good afternoon', 'good evening', 'good day', 'hello everyone']
        normal_phrases = ['hi', 'hello']
        
        for phrase in excellent_phrases:
            if phrase in first_sentence:
                return 5, 'Excellent', first_sentence
        
        for phrase in good_phrases:
            if phrase in first_sentence:
                return 4, 'Good', first_sentence
        
        for phrase in normal_phrases:
            if phrase in first_sentence:
                return 2, 'Normal', first_sentence
        
        return 0, 'No Salutation', first_sentence
    
    def analyze_keywords(self):
        """Analyze presence of must-have and good-to-have keywords"""
        text_lower = self.transcript.lower()
        
        must_have = {
            'name': ['name', 'myself', 'i am', "i'm"],
            'age': ['year', 'age', 'old'],
            'school': ['school', 'class', 'grade', 'studying'],
            'family': ['family', 'mother', 'father', 'parents', 'siblings', 'brother', 'sister'],
            'hobbies': ['hobby', 'hobbies', 'enjoy', 'like', 'love', 'play', 'interest']
        }
        
        good_to_have = {
            'family_details': ['kind', 'caring', 'supportive', 'members', 'people in my family'],
            'location': ['from', 'live in', 'native', 'hometown'],
            'ambition': ['want to', 'goal', 'dream', 'ambition', 'aspire', 'future'],
            'unique_fact': ['fun fact', 'interesting', 'unique', 'special thing'],
            'strengths': ['strength', 'achievement', 'good at', 'excel']
        }
        
        must_have_found = []
        must_have_score = 0
        
        for category, keywords in must_have.items():
            if any(keyword in text_lower for keyword in keywords):
                must_have_found.append(category)
                must_have_score += 4
        
        good_to_have_found = []
        good_to_have_score = 0
        
        for category, keywords in good_to_have.items():
            if any(keyword in text_lower for keyword in keywords):
                good_to_have_found.append(category)
                good_to_have_score += 2
        
        total_score = min(must_have_score + good_to_have_score, 20)
        
        return {
            'must_have': must_have_found,
            'good_to_have': good_to_have_found,
            'score': total_score
        }
    
    def analyze_flow(self):
        """Analyze if introduction follows proper order"""
        text_lower = self.transcript.lower()
        sentences_lower = [s.lower() for s in self.sentences]
        
        # Check order: Salutation -> Name -> Basic Details -> Additional -> Closing
        has_salutation = any(word in sentences_lower[0] if sentences_lower else "" 
                            for word in ['hi', 'hello', 'good morning', 'good afternoon', 'good evening'])
        
        # Find positions
        name_pos = next((i for i, s in enumerate(sentences_lower) 
                        if any(word in s for word in ['myself', 'i am', 'my name'])), -1)
        
        closing_words = ['thank', 'thanks', 'grateful']
        has_closing = any(word in sentences_lower[-1] if sentences_lower else "" 
                         for word in closing_words)
        
        # Simple order check
        if has_salutation and name_pos >= 0 and (name_pos <= 2):
            if has_closing:
                return 15, "Good flow with proper opening and closing"
            return 13, "Good flow but could improve closing"
        
        return 10, "Flow could be improved - consider: Salutation → Name → Details → Closing"
    
    def analyze_grammar(self):
        """Analyze grammar errors using LanguageTool"""
        try:
            tool = get_grammar_tool()
            matches = tool.check(self.transcript)
            error_count = len(matches)
            errors_per_100 = (error_count / self.word_count) * 100 if self.word_count > 0 else 0
            
            grammar_ratio = max(0, 1 - min(errors_per_100 / 10, 1))
            
            if grammar_ratio >= 0.9:
                score = 15
            elif grammar_ratio >= 0.7:
                score = 12
            elif grammar_ratio >= 0.5:
                score = 9
            elif grammar_ratio >= 0.3:
                score = 6
            else:
                score = 3
            
            return {
                'error_count': error_count,
                'errors_per_100': round(errors_per_100, 2),
                'grammar_ratio': round(grammar_ratio, 2),
                'score': score
            }
        except Exception as e:
            # Fallback if LanguageTool fails
            return {
                'error_count': 0,
                'errors_per_100': 0,
                'grammar_ratio': 1.0,
                'score': 15
            }
    
    def analyze_vocabulary_richness(self):
        """Calculate Type-Token Ratio (TTR)"""
        if self.word_count == 0:
            return {'distinct_words': 0, 'total_words': 0, 'ttr': 0, 'score': 0}
        
        # Clean words
        cleaned_words = [re.sub(r'[^\w\s]', '', word) for word in self.words]
        distinct_words = len(set(cleaned_words))
        
        ttr = distinct_words / self.word_count
        
        if ttr > 0.9:
            score = 10
        elif ttr >= 0.7:
            score = 8
        elif ttr >= 0.5:
            score = 6
        elif ttr >= 0.3:
            score = 4
        else:
            score = 2
        
        return {
            'distinct_words': distinct_words,
            'total_words': self.word_count,
            'ttr': round(ttr, 3),
            'score': score
        }
    
    def analyze_filler_words(self):
        """Calculate filler word rate"""
        text_lower = self.transcript.lower()
        filler_count = 0
        filler_words_found = []
        
        for filler in self.filler_words:
            if ' ' in filler:  # Multi-word fillers
                count = text_lower.count(filler)
                if count > 0:
                    filler_count += count
                    filler_words_found.append(f"{filler} ({count})")
            else:  # Single word fillers
                pattern = r'\b' + re.escape(filler) + r'\b'
                matches = re.findall(pattern, text_lower)
                if matches:
                    filler_count += len(matches)
                    filler_words_found.append(f"{filler} ({len(matches)})")
        
        filler_rate = (filler_count / self.word_count * 100) if self.word_count > 0 else 0
        
        if filler_rate < 0.3:
            score = 10
        elif filler_rate < 0.5:
            score = 8
        elif filler_rate < 0.7:
            score = 6
        elif filler_rate < 0.9:
            score = 4
        else:
            score = 2
        
        return {
            'filler_count': filler_count,
            'filler_rate': round(filler_rate, 2),
            'filler_words_found': filler_words_found,
            'score': score
        }
    
    def analyze_sentiment(self):
        """Analyze sentiment/positivity using TextBlob"""
        blob = TextBlob(self.transcript)
        polarity = blob.sentiment.polarity  # -1 to 1
        
        # Convert to 0-1 scale for positive probability
        positive_probability = (polarity + 1) / 2
        
        if positive_probability >= 0.9:
            score = 15
            sentiment = 'Positive'
        elif positive_probability >= 0.7:
            score = 12
            sentiment = 'Positive'
        elif positive_probability >= 0.5:
            score = 9
            sentiment = 'Neutral'
        elif positive_probability >= 0.3:
            score = 6
            sentiment = 'Neutral'
        else:
            score = 3
            sentiment = 'Negative'
        
        return {
            'sentiment': sentiment,
            'positive_probability': round(positive_probability, 3),
            'score': score
        }
    
    def analyze(self):
        """Perform complete analysis"""
        wpm = self.calculate_wpm()
        
        # Content & Structure (40 points)
        salutation_score, salutation_type, salutation_text = self.analyze_salutation()
        keywords_result = self.analyze_keywords()
        flow_score, flow_feedback = self.analyze_flow()
        
        content_score = salutation_score + keywords_result['score'] + flow_score
        
        # Speech Rate (10 points)
        if wpm > 161:
            speech_score = 2
            speech_category = 'Too Fast'
        elif wpm >= 141:
            speech_score = 6
            speech_category = 'Fast'
        elif wpm >= 111:
            speech_score = 10
            speech_category = 'Ideal'
        elif wpm >= 81:
            speech_score = 6
            speech_category = 'Slow'
        else:
            speech_score = 2
            speech_category = 'Too Slow'
        
        # Grammar (15 points)
        grammar_result = self.analyze_grammar()
        
        # Vocabulary (10 points)
        vocab_result = self.analyze_vocabulary_richness()
        
        # Clarity (10 points)
        filler_result = self.analyze_filler_words()
        
        # Engagement (15 points)
        sentiment_result = self.analyze_sentiment()
        
        # Calculate overall score
        overall_score = (
            content_score +
            speech_score +
            grammar_result['score'] +
            vocab_result['score'] +
            filler_result['score'] +
            sentiment_result['score']
        )
        
        # Generate feedback
        criteria = [
            {
                'name': 'Content & Structure',
                'score': content_score,
                'max_score': 40,
                'details': {
                    'salutation_score': salutation_score,
                    'salutation_type': salutation_type,
                    'keywords_found': keywords_result,
                    'flow_score': flow_score,
                    'flow_feedback': flow_feedback
                },
                'feedback': self._generate_content_feedback(salutation_score, keywords_result, flow_score)
            },
            {
                'name': 'Speech Rate',
                'score': speech_score,
                'max_score': 10,
                'details': {
                    'wpm': wpm,
                    'category': speech_category
                },
                'feedback': f"Speech rate is {wpm} WPM ({speech_category}). " +
                           ("Great pace!" if speech_score >= 8 else "Consider adjusting your pace for better clarity.")
            },
            {
                'name': 'Language & Grammar',
                'score': grammar_result['score'],
                'max_score': 15,
                'details': grammar_result,
                'feedback': f"Found {grammar_result['error_count']} grammar issues. " +
                           ("Excellent grammar!" if grammar_result['score'] >= 12 else "Review grammar for improvement.")
            },
            {
                'name': 'Vocabulary Richness',
                'score': vocab_result['score'],
                'max_score': 10,
                'details': vocab_result,
                'feedback': f"Vocabulary diversity (TTR): {vocab_result['ttr']}. " +
                           ("Great variety!" if vocab_result['score'] >= 8 else "Try using more diverse vocabulary.")
            },
            {
                'name': 'Clarity',
                'score': filler_result['score'],
                'max_score': 10,
                'details': filler_result,
                'feedback': f"Filler word rate: {filler_result['filler_rate']}%. " +
                           ("Very clear delivery!" if filler_result['score'] >= 8 else "Reduce filler words for better clarity.")
            },
            {
                'name': 'Engagement',
                'score': sentiment_result['score'],
                'max_score': 15,
                'details': sentiment_result,
                'feedback': f"Overall tone is {sentiment_result['sentiment']} (positivity: {sentiment_result['positive_probability']}). " +
                           ("Great enthusiasm!" if sentiment_result['score'] >= 12 else "Consider adding more positive energy.")
            }
        ]
        
        summary = self._generate_summary(overall_score, criteria)
        
        return {
            'overall_score': overall_score,
            'word_count': self.word_count,
            'sentence_count': self.sentence_count,
            'duration_seconds': self.duration_seconds,
            'wpm': wpm,
            'criteria': criteria,
            'summary': summary
        }
    
    def _generate_content_feedback(self, sal_score, keywords, flow_score):
        feedback = []
        
        if sal_score >= 4:
            feedback.append("Strong opening.")
        else:
            feedback.append("Consider a more engaging greeting.")
        
        missing_must = 5 - len(keywords['must_have'])
        if missing_must > 0:
            feedback.append(f"Missing {missing_must} key details.")
        else:
            feedback.append("All essential information included.")
        
        if flow_score >= 13:
            feedback.append("Well-structured flow.")
        else:
            feedback.append("Structure could be improved.")
        
        return " ".join(feedback)
    
    def _generate_summary(self, score, criteria):
        if score >= 85:
            overall = "Excellent self-introduction with strong communication skills."
        elif score >= 70:
            overall = "Good self-introduction with room for minor improvements."
        elif score >= 55:
            overall = "Decent introduction but needs improvement in several areas."
        else:
            overall = "Significant improvement needed in communication skills."
        
        weakest = min(criteria, key=lambda x: x['score'] / x['max_score'])
        
        return f"{overall} Focus on improving: {weakest['name']} for better results."

@app.route('/api/analyze', methods=['POST'])
def analyze():
    try:
        data = request.get_json()
        transcript = data.get('transcript', '')
        duration = data.get('duration_seconds', 52)
        
        if not transcript:
            return jsonify({'error': 'Transcript is required'}), 400
        
        analyzer = SpeechAnalyzer(transcript, duration)
        results = analyzer.analyze()
        
        return jsonify(results)
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/health', methods=['GET'])
def health():
    return jsonify({'status': 'healthy'})

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)