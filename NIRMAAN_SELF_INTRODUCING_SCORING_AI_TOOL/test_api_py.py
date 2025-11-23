import requests
import json
import sys

def test_health_endpoint():
    """Test the health check endpoint"""
    print("=" * 60)
    print("Testing Health Endpoint")
    print("=" * 60)
    
    try:
        response = requests.get('http://localhost:5000/api/health', timeout=5)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.json()}")
        
        if response.status_code == 200:
            print("✅ Health check passed")
            return True
        else:
            print("❌ Health check failed")
            return False
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return False

def test_analyze_endpoint(transcript=None, duration=52):
    """Test the analyze endpoint"""
    print("\n" + "=" * 60)
    print("Testing Analyze Endpoint")
    print("=" * 60)
    
    if transcript is None:
        # Use sample transcript
        transcript = """Hello everyone, myself Muskan, studying in class 8th B section from Christ Public School. 
I am 13 years old. I live with my family. There are 3 people in my family, me, my mother and my father.
One special thing about my family is that they are very kind hearted to everyone and soft spoken. One thing I really enjoy is play, playing cricket and taking wickets.
A fun fact about me is that I see in mirror and talk by myself. One thing people don't know about me is that I once stole a toy from one of my cousin.
My favorite subject is science because it is very interesting. Through science I can explore the whole world and make the discoveries and improve the lives of others. 
Thank you for listening."""
    
    data = {
        "transcript": transcript,
        "duration_seconds": duration
    }
    
    try:
        response = requests.post(
            'http://localhost:5000/api/analyze',
            json=data,
            timeout=30
        )
        
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print_analysis_results(result)
            return True
        else:
            print(f"❌ Analysis failed: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return False

def print_analysis_results(result):
    """Print formatted analysis results"""
    print("\n" + "=" * 60)
    print("ANALYSIS RESULTS")
    print("=" * 60)
    
    # Overall score
    print(f"\n🎯 OVERALL SCORE: {result['overall_score']}/100")
    print(f"   Grade: {get_grade(result['overall_score'])}")
    
    # Basic metrics
    print(f"\n📊 METRICS:")
    print(f"   Word Count: {result['word_count']}")
    print(f"   Sentence Count: {result['sentence_count']}")
    print(f"   Duration: {result['duration_seconds']} seconds")
    print(f"   WPM: {result['wpm']}")
    
    # Criteria breakdown
    print(f"\n📋 CRITERIA BREAKDOWN:")
    print("-" * 60)
    
    for criterion in result['criteria']:
        percentage = (criterion['score'] / criterion['max_score']) * 100
        bar = create_progress_bar(percentage)
        
        print(f"\n{criterion['name']}")
        print(f"   Score: {criterion['score']}/{criterion['max_score']} ({percentage:.1f}%)")
        print(f"   {bar}")
        print(f"   Feedback: {criterion['feedback']}")
        
        # Print details if available
        if 'details' in criterion and criterion['details']:
            print(f"   Details:")
            for key, value in criterion['details'].items():
                if isinstance(value, dict):
                    print(f"      {key}:")
                    for k, v in value.items():
                        print(f"         {k}: {v}")
                elif isinstance(value, list):
                    print(f"      {key}: {', '.join(map(str, value)) if value else 'None'}")
                else:
                    print(f"      {key}: {value}")
    
    # Summary
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    print(result['summary'])
    print("=" * 60)

def create_progress_bar(percentage, width=40):
    """Create a text-based progress bar"""
    filled = int(width * percentage / 100)
    bar = '█' * filled + '░' * (width - filled)
    return f"[{bar}] {percentage:.1f}%"

def get_grade(score):
    """Convert score to letter grade"""
    if score >= 90:
        return "A (Excellent)"
    elif score >= 80:
        return "B (Good)"
    elif score >= 70:
        return "C (Satisfactory)"
    elif score >= 60:
        return "D (Needs Improvement)"
    else:
        return "F (Poor)"

def test_edge_cases():
    """Test edge cases"""
    print("\n" + "=" * 60)
    print("Testing Edge Cases")
    print("=" * 60)
    
    # Test 1: Empty transcript
    print("\n1. Testing empty transcript...")
    data = {"transcript": "", "duration_seconds": 52}
    response = requests.post('http://localhost:5000/api/analyze', json=data)
    if response.status_code == 400:
        print("✅ Correctly rejected empty transcript")
    else:
        print("❌ Should reject empty transcript")
    
    # Test 2: Very short transcript
    print("\n2. Testing very short transcript...")
    data = {"transcript": "Hi everyone.", "duration_seconds": 2}
    response = requests.post('http://localhost:5000/api/analyze', json=data)
    if response.status_code == 200:
        result = response.json()
        print(f"✅ Processed short transcript (score: {result['overall_score']})")
    else:
        print("❌ Failed to process short transcript")
    
    # Test 3: Very long transcript
    print("\n3. Testing long transcript...")
    long_text = " ".join(["This is a test sentence."] * 100)
    data = {"transcript": long_text, "duration_seconds": 120}
    response = requests.post('http://localhost:5000/api/analyze', json=data)
    if response.status_code == 200:
        result = response.json()
        print(f"✅ Processed long transcript (score: {result['overall_score']})")
    else:
        print("❌ Failed to process long transcript")

def run_all_tests():
    """Run all tests"""
    print("\n" + "=" * 60)
    print("SPEECH SCORING API - TEST SUITE")
    print("=" * 60)
    
    tests_passed = 0
    total_tests = 3
    
    # Test 1: Health check
    if test_health_endpoint():
        tests_passed += 1
    
    # Test 2: Main analysis
    if test_analyze_endpoint():
        tests_passed += 1
    
    # Test 3: Edge cases
    try:
        test_edge_cases()
        tests_passed += 1
    except Exception as e:
        print(f"❌ Edge case tests failed: {str(e)}")
    
    # Summary
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    print(f"Tests Passed: {tests_passed}/{total_tests}")
    
    if tests_passed == total_tests:
        print("✅ All tests passed!")
        return 0
    else:
        print(f"❌ {total_tests - tests_passed} test(s) failed")
        return 1

if __name__ == "__main__":
    # Check if server is running
    print("Checking if server is running...")
    try:
        requests.get('http://localhost:5000/api/health', timeout=2)
        print("✅ Server is running\n")
    except:
        print("❌ Server is not running!")
        print("Please start the server with: python app.py")
        sys.exit(1)
    
    # Run tests
    exit_code = run_all_tests()
    sys.exit(exit_code)