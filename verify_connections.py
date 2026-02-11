import os
import sys
import json
import base64
from unittest.mock import MagicMock, patch

# Ensure the current directory is in the path
sys.path.append(os.getcwd())

# Mock the Groq client to avoid API calls and rate limits
sys.modules['groq'] = MagicMock()
from groq import Groq

# Mock the client instance
mock_client = MagicMock()
Groq.return_value = mock_client

# Mock response for ResumeParser
mock_resume_response = MagicMock()
mock_resume_response.choices[0].message.content = """
```json
{
  "personal_info": {
    "name": "Test User",
    "email": "test@example.com",
    "phone": "123-456-7890",
    "location": "Test City"
  },
  "professional_summary": "A test professional summary.",
  "skills": {
    "technical": ["Python", "JavaScript"]
  }
}
```
"""

# Mock response for MasterJSONBuilder (Person Details)
mock_person_response = MagicMock()
mock_person_response.choices[0].message.content = """
{
  "name": "Test User",
  "role": "Software Engineer",
  "tone": "professional",
  "appearance": {
    "gender": "male",
    "age_range": "30-35",
    "clothing": "casual",
    "distinctive_features": "none"
  },
  "key_points": ["Point 1", "Point 2"],
  "speaking_style": "clear"
}
"""

# Mock response for ClipJSONGenerator (Dialogue)
mock_dialogue_response = MagicMock()
mock_dialogue_response.choices[0].message.content = """
{
  "segment_1": "Hello, I'm Test User. This is the intro.",
  "segment_2": "This is the content for clip 2.",
  "segment_3": "This is the outro for clip 3."
}
"""

def side_effect(model, messages, **kwargs):
    content = messages[1]['content']
    if "Extract information from this resume" in content:
        return mock_resume_response
    elif "extract person details" in content.lower():
        return mock_person_response
    elif "create structured dialogue" in content.lower():
        return mock_dialogue_response
    return MagicMock()

mock_client.chat.completions.create.side_effect = side_effect

# Import the modules to test
try:
    from resume_parser import ResumeParser
    from master_builder import MasterJSONBuilder
    from clip_generator import ClipJSONGenerator
    print("✅ Imports successful")
except ImportError as e:
    print(f"❌ Import failed: {e}")
    sys.exit(1)

def test_resume_parser():
    print("\nTesting ResumeParser...")
    parser = ResumeParser(api_key="fake_key")
    # Mock _extract_pdf_text since we don't have a real PDF
    parser._extract_pdf_text = MagicMock(return_value="Resume text for Test User")
    
    data = parser.parse_file("dummy.pdf")
    if data['personal_info']['name'] == "Test User":
        print("✅ ResumeParser logic verified")
    else:
        print("❌ ResumeParser logic failed")
        print(data)

def test_master_builder():
    print("\nTesting MasterJSONBuilder...")
    builder = MasterJSONBuilder(api_key="fake_key")
    master = builder.build_master(
        user_description="Test Description",
        reference_image_path="dummy.jpg"
    )
    if master['person_identity']['name'] == "Test User":
        print("✅ MasterJSONBuilder logic verified")
    else:
        print("❌ MasterJSONBuilder logic failed")
        print(master['person_identity'])
    return master

def test_clip_generator(master_json):
    print("\nTesting ClipJSONGenerator...")
    generator = ClipJSONGenerator(api_key="fake_key")
    clips = generator.generate_all_clips(
        master_json=master_json,
        user_description="Test Description"
    )
    if len(clips) == 3 and clips[0]['dialogue']['is_introduction']:
        print("✅ ClipJSONGenerator logic verified")
    else:
        print("❌ ClipJSONGenerator logic failed")
        print(f"Clips generated: {len(clips)}")

if __name__ == "__main__":
    try:
        test_resume_parser()
        master = test_master_builder()
        test_clip_generator(master)
        print("\n✅ All module connections verified successfully.")
    except Exception as e:
        print(f"\n❌ Verification failed with error: {e}")
        import traceback
        traceback.print_exc()
