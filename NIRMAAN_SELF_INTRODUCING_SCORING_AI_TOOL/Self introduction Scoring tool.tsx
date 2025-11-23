import React, { useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { AlertCircle, CheckCircle, Upload, FileText } from 'lucide-react';

const SpeechScoringApp = () => {
  const [transcript, setTranscript] = useState('');
  const [results, setResults] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const analyzeTranscript = async () => {
    if (!transcript.trim()) {
      setError('Please enter a transcript to analyze');
      return;
    }

    setLoading(true);
    setError('');

    try {
      const response = await fetch('https://api.anthropic.com/v1/messages', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          model: 'claude-sonnet-4-20250514',
          max_tokens: 4000,
          messages: [{
            role: 'user',
            content: `You are an expert speech analysis system. Analyze this self-introduction transcript and provide detailed scoring based on the following rubric:

**RUBRIC STRUCTURE:**

1. **Content & Structure (40 points total)**
   - Salutation Level (5 points):
     * No salutation: 0
     * Normal (Hi, Hello): 2
     * Good (Good Morning/Afternoon/Evening, Hello everyone): 4
     * Excellent (includes "excited to introduce" or similar): 5
   
   - Keyword Presence (20 points):
     * Must Have (4 points each): Name, Age, School/Class, Family, Hobbies/Interests
     * Good to Have (2 points each): About Family details, Origin Location, Ambition/Goal, Interesting fact/unique thing, Strengths/Achievements
   
   - Flow/Order (15 points):
     * Order followed (Salutation → Basic details → Additional details → Closing): 15
     * Order not followed: 10

2. **Speech Rate (10 points)** - Based on WPM (words per minute)
   * Too Fast (>161 WPM): 2
   * Fast (141-160 WPM): 6
   * Ideal (111-140 WPM): 10
   * Slow (81-110 WPM): 6
   * Too Slow (<80 WPM): 2

3. **Language & Grammar (15 points)** - Grammar Score = 1 - min(errors per 100 words / 10, 1)
   * Score 0.9-1.0: 15 points
   * Score 0.7-0.89: 12 points
   * Score 0.5-0.69: 9 points
   * Score 0.3-0.49: 6 points
   * Score 0-0.29: 3 points

4. **Vocabulary Richness (10 points)** - TTR = Distinct words ÷ Total words
   * TTR >0.9: 10 points
   * TTR 0.7-0.89: 8 points
   * TTR 0.5-0.69: 6 points
   * TTR 0.3-0.49: 4 points
   * TTR <0.3: 2 points

5. **Clarity - Filler Word Rate (10 points)** - (Filler words ÷ Total words) × 100
   * Rate 0-0.29%: 10 points
   * Rate 0.3-0.49%: 8 points
   * Rate 0.5-0.69%: 6 points
   * Rate 0.7-0.89%: 4 points
   * Rate ≥0.9%: 2 points
   * Filler words: um, uh, like, you know, so, actually, basically, right, i mean, well, kinda, sort of, okay, hmm, ah

6. **Engagement - Sentiment (15 points)** - Positive probability (0-1)
   * Probability ≥0.9: 15 points
   * Probability 0.7-0.89: 12 points
   * Probability 0.5-0.69: 9 points
   * Probability 0.3-0.49: 6 points
   * Probability <0.3: 3 points

**TRANSCRIPT TO ANALYZE:**
${transcript}

**DURATION:** Assume 52 seconds (if not provided, estimate based on word count)

Analyze this transcript thoroughly and return a JSON response with this exact structure:
{
  "overall_score": <number 0-100>,
  "word_count": <number>,
  "sentence_count": <number>,
  "duration_seconds": <number>,
  "wpm": <number>,
  "criteria": [
    {
      "name": "Content & Structure",
      "score": <number>,
      "max_score": 40,
      "details": {
        "salutation_score": <number>,
        "salutation_type": "<string>",
        "keywords_found": {
          "must_have": ["<found keywords>"],
          "good_to_have": ["<found keywords>"]
        },
        "keywords_score": <number>,
        "flow_score": <number>,
        "flow_feedback": "<string>"
      },
      "feedback": "<detailed feedback>"
    },
    {
      "name": "Speech Rate",
      "score": <number>,
      "max_score": 10,
      "details": {
        "wpm": <number>,
        "category": "<string>"
      },
      "feedback": "<feedback>"
    },
    {
      "name": "Language & Grammar",
      "score": <number>,
      "max_score": 15,
      "details": {
        "error_count": <number>,
        "errors_per_100": <number>,
        "grammar_ratio": <number>
      },
      "feedback": "<feedback>"
    },
    {
      "name": "Vocabulary Richness",
      "score": <number>,
      "max_score": 10,
      "details": {
        "distinct_words": <number>,
        "total_words": <number>,
        "ttr": <number>
      },
      "feedback": "<feedback>"
    },
    {
      "name": "Clarity",
      "score": <number>,
      "max_score": 10,
      "details": {
        "filler_count": <number>,
        "filler_rate": <number>,
        "filler_words_found": ["<list>"]
      },
      "feedback": "<feedback>"
    },
    {
      "name": "Engagement",
      "score": <number>,
      "max_score": 15,
      "details": {
        "sentiment": "<positive/neutral/negative>",
        "positive_probability": <number>
      },
      "feedback": "<feedback>"
    }
  ],
  "summary": "<overall summary feedback>"
}

Be precise with calculations and provide constructive feedback. Return ONLY the JSON, no additional text.`
          }]
        })
      });

      const data = await response.json();
      const text = data.content.map(item => item.type === 'text' ? item.text : '').join('\n');
      const cleanJson = text.replace(/```json\n?|\n?```/g, '').trim();
      const parsed = JSON.parse(cleanJson);
      
      setResults(parsed);
    } catch (err) {
      setError(`Analysis failed: ${err.message}`);
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const loadSampleText = () => {
    const sample = `Hello everyone, myself Muskan, studying in class 8th B section from Christ Public School. 
I am 13 years old. I live with my family. There are 3 people in my family, me, my mother and my father.
One special thing about my family is that they are very kind hearted to everyone and soft spoken. One thing I really enjoy is play, playing cricket and taking wickets.
A fun fact about me is that I see in mirror and talk by myself. One thing people don't know about me is that I once stole a toy from one of my cousin.
My favorite subject is science because it is very interesting. Through science I can explore the whole world and make the discoveries and improve the lives of others. 
Thank you for listening.`;
    setTranscript(sample);
  };

  const getScoreColor = (score, maxScore) => {
    const percentage = (score / maxScore) * 100;
    if (percentage >= 80) return 'text-green-600';
    if (percentage >= 60) return 'text-yellow-600';
    return 'text-red-600';
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 p-6">
      <div className="max-w-6xl mx-auto">
        <div className="text-center mb-8">
          <h1 className="text-4xl font-bold text-gray-800 mb-2">
            Self-Introduction Scoring Tool
          </h1>
          <p className="text-gray-600">
            AI-powered analysis of communication skills based on comprehensive rubrics
          </p>
        </div>

        <Card className="mb-6 shadow-lg">
          <CardHeader className="bg-gradient-to-r from-blue-600 to-indigo-600 text-white">
            <CardTitle className="flex items-center gap-2">
              <FileText className="w-6 h-6" />
              Input Transcript
            </CardTitle>
          </CardHeader>
          <CardContent className="p-6">
            <textarea
              value={transcript}
              onChange={(e) => setTranscript(e.target.value)}
              placeholder="Paste the self-introduction transcript here..."
              className="w-full h-48 p-4 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent resize-none"
            />
            <div className="flex gap-3 mt-4">
              <button
                onClick={analyzeTranscript}
                disabled={loading}
                className="flex-1 bg-gradient-to-r from-blue-600 to-indigo-600 text-white px-6 py-3 rounded-lg font-semibold hover:from-blue-700 hover:to-indigo-700 disabled:opacity-50 disabled:cursor-not-allowed transition-all shadow-md"
              >
                {loading ? 'Analyzing...' : 'Analyze Transcript'}
              </button>
              <button
                onClick={loadSampleText}
                className="px-6 py-3 border-2 border-indigo-600 text-indigo-600 rounded-lg font-semibold hover:bg-indigo-50 transition-all"
              >
                Load Sample
              </button>
            </div>
            {error && (
              <div className="mt-4 p-4 bg-red-50 border border-red-200 rounded-lg flex items-start gap-2">
                <AlertCircle className="w-5 h-5 text-red-600 mt-0.5" />
                <span className="text-red-700">{error}</span>
              </div>
            )}
          </CardContent>
        </Card>

        {results && (
          <div className="space-y-6">
            <Card className="shadow-lg">
              <CardHeader className="bg-gradient-to-r from-green-600 to-teal-600 text-white">
                <CardTitle className="text-2xl">Overall Score</CardTitle>
              </CardHeader>
              <CardContent className="p-6">
                <div className="text-center">
                  <div className="text-6xl font-bold text-green-600 mb-2">
                    {results.overall_score}
                    <span className="text-3xl text-gray-500">/100</span>
                  </div>
                  <div className="grid grid-cols-3 gap-4 mt-6 text-sm">
                    <div className="bg-gray-50 p-3 rounded-lg">
                      <div className="text-gray-600">Words</div>
                      <div className="text-xl font-semibold">{results.word_count}</div>
                    </div>
                    <div className="bg-gray-50 p-3 rounded-lg">
                      <div className="text-gray-600">Sentences</div>
                      <div className="text-xl font-semibold">{results.sentence_count}</div>
                    </div>
                    <div className="bg-gray-50 p-3 rounded-lg">
                      <div className="text-gray-600">WPM</div>
                      <div className="text-xl font-semibold">{results.wpm}</div>
                    </div>
                  </div>
                </div>
              </CardContent>
            </Card>

            {results.criteria.map((criterion, idx) => (
              <Card key={idx} className="shadow-md hover:shadow-lg transition-shadow">
                <CardHeader className="bg-gray-50">
                  <div className="flex justify-between items-center">
                    <CardTitle className="text-lg">{criterion.name}</CardTitle>
                    <div className={`text-2xl font-bold ${getScoreColor(criterion.score, criterion.max_score)}`}>
                      {criterion.score}/{criterion.max_score}
                    </div>
                  </div>
                </CardHeader>
                <CardContent className="p-6">
                  <div className="mb-4">
                    <div className="w-full bg-gray-200 rounded-full h-3">
                      <div
                        className="bg-gradient-to-r from-blue-500 to-indigo-500 h-3 rounded-full transition-all"
                        style={{ width: `${(criterion.score / criterion.max_score) * 100}%` }}
                      />
                    </div>
                  </div>
                  
                  <p className="text-gray-700 mb-4">{criterion.feedback}</p>
                  
                  {criterion.details && (
                    <div className="bg-blue-50 p-4 rounded-lg space-y-2 text-sm">
                      {Object.entries(criterion.details).map(([key, value]) => (
                        <div key={key} className="flex justify-between">
                          <span className="text-gray-600 capitalize">
                            {key.replace(/_/g, ' ')}:
                          </span>
                          <span className="font-semibold text-gray-800">
                            {Array.isArray(value) 
                              ? value.join(', ') || 'None'
                              : typeof value === 'object'
                              ? JSON.stringify(value)
                              : value}
                          </span>
                        </div>
                      ))}
                    </div>
                  )}
                </CardContent>
              </Card>
            ))}

            {results.summary && (
              <Card className="shadow-lg border-2 border-indigo-200">
                <CardHeader className="bg-gradient-to-r from-indigo-50 to-blue-50">
                  <CardTitle className="flex items-center gap-2 text-indigo-800">
                    <CheckCircle className="w-6 h-6" />
                    Summary & Recommendations
                  </CardTitle>
                </CardHeader>
                <CardContent className="p-6">
                  <p className="text-gray-700 leading-relaxed">{results.summary}</p>
                </CardContent>
              </Card>
            )}
          </div>
        )}
      </div>
    </div>
  );
};

export default SpeechScoringApp;