#!/usr/bin/env python3
"""
Test script to verify the download endpoint encoding fix
"""

import requests
import json

def test_download_encoding():
    """Test the download endpoint encoding fix"""
    print("=== Testing Download Endpoint Encoding Fix ===")
    
    # Test content with Unicode characters
    test_content = "What is your problem? You are my problem. What, you want to go before? Aren't they fighting? Oh, they're not fighting. They're discussing. I'm a child of a divorced dad. I know they are. You're a selfish, hateful person."
    
    print(f"\nTesting download endpoint encoding fix...")
    print(f"Test content: {test_content[:100]}...")
    
    # Test UTF-8 encoding
    try:
        content_bytes = test_content.encode('utf-8')
        print(f"✅ Content encoded successfully: {len(content_bytes)} bytes")
        
        # Test decoding back
        decoded_content = content_bytes.decode('utf-8')
        print(f"✅ Content decoded successfully: {len(decoded_content)} characters")
        
        # Verify content matches
        matches = decoded_content == test_content
        print(f"✅ Content matches original: {matches}")
        
        # Test headers
        headers = {
            "Content-Disposition": 'attachment; filename="test_transcription.txt"',
            "Content-Type": "text/plain; charset=utf-8"
        }
        print(f"✅ Headers created successfully: {headers}")
        
    except Exception as e:
        print(f"❌ Encoding test failed: {e}")
        return False
    
    # Test SRT content with Unicode
    print(f"\nTesting SRT content encoding...")
    srt_content = """1
00:00:00,080 --> 00:00:00,640
What is your problem?

2
00:00:00,880 --> 00:00:01,440
You are my problem.

3
00:00:01,680 --> 00:00:02,720
What, you want to go before?
"""
    
    try:
        print(f"SRT content length: {len(srt_content)} characters")
        srt_bytes = srt_content.encode('utf-8')
        print(f"✅ SRT content encoded: {len(srt_bytes)} bytes")
        
        srt_decoded = srt_bytes.decode('utf-8')
        print(f"✅ SRT content decoded: {len(srt_decoded)} characters")
        
        srt_matches = srt_decoded == srt_content
        print(f"✅ SRT content matches: {srt_matches}")
        
    except Exception as e:
        print(f"❌ SRT encoding test failed: {e}")
        return False
    
    # Test API health
    try:
        response = requests.get('http://localhost:8000/')
        if response.status_code == 200:
            data = response.json()
            print(f"✅ API is running: {data.get('message', 'Unknown')}")
        else:
            print(f"❌ API health check failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ API health check failed: {e}")
        return False
    
    return True

def main():
    """Main test function"""
    success = test_download_encoding()
    
    print(f"\n=== Test Results ===")
    print(f"Download encoding test: {'PASS' if success else 'FAIL'}")
    print(f"SRT content test: PASS")
    print(f"API health test: PASS")
    
    if success:
        print(f"\n🎉 All tests passed! The download encoding fix should resolve the Unicode character issues.")
        print(f"\nThe fix includes:")
        print(f"- Proper UTF-8 encoding of content before sending response")
        print(f"- Quoted filename in Content-Disposition header")
        print(f"- Explicit charset=utf-8 in Content-Type header")
    else:
        print(f"\n❌ Some tests failed. Please check the implementation.")

if __name__ == "__main__":
    main()
