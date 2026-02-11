"""
VEO Dialogue Generator - Flask Backend
======================================
Main backend server integrating all components.
"""

from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import os
import sys
import base64
import tempfile
from datetime import datetime
from dotenv import load_dotenv

# Import custom modules
from resume_parser import ResumeParser
from master_builder import MasterJSONBuilder
from clip_generator import ClipJSONGenerator

# Load environment variables
load_dotenv()

# Initialize Flask app
app = Flask(__name__)
CORS(app)

# Configuration
GROQ_API_KEY = os.getenv('GROQ_API_KEY')
if not GROQ_API_KEY:
    print("⚠️  WARNING: GROQ_API_KEY not found in .env file!")
    print("Please create a .env file with your Groq API key:")
    print("GROQ_API_KEY=your_api_key_here")

# Create necessary directories
UPLOAD_FOLDER = 'uploads'
OUTPUT_FOLDER = 'outputs'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

# Initialize components
resume_parser = ResumeParser(api_key=GROQ_API_KEY) if GROQ_API_KEY else None
master_builder = MasterJSONBuilder(api_key=GROQ_API_KEY) if GROQ_API_KEY else None
clip_generator = ClipJSONGenerator(api_key=GROQ_API_KEY) if GROQ_API_KEY else None


# ============ HELPER FUNCTIONS ============

def save_base64_image(base64_string: str, filename: str) -> str:
    """
    Saves base64 image to file.
    """
    try:
        # Remove data URL prefix if present
        if ',' in base64_string:
            base64_string = base64_string.split(',')[1]
        
        # Decode and save
        image_data = base64.b64decode(base64_string)
        filepath = os.path.join(UPLOAD_FOLDER, filename)
        
        with open(filepath, 'wb') as f:
            f.write(image_data)
        
        return filepath
    except Exception as e:
        raise Exception(f"Error saving image: {str(e)}")


def cleanup_old_files():
    """
    Cleanup old uploaded files (optional, run periodically).
    """
    # Implementation: delete files older than 24 hours
    pass


# ============ API ENDPOINTS ============

@app.route('/')
def index():
    """
    Serve the main application UI.
    """
    return send_from_directory('.', 'index_premium_final.html')


@app.route('/api/parse-resume', methods=['POST'])
def parse_resume():
    """
    Endpoint 1: Parse resume file (PDF/DOCX)
    """
    try:
        if not GROQ_API_KEY:
            return jsonify({
                'success': False,
                'error': 'GROQ_API_KEY not configured. Please add it to .env file.'
            }), 500
        
        # Check if file is present
        if 'file' not in request.files:
            return jsonify({
                'success': False,
                'error': 'No file uploaded'
            }), 400
        
        file = request.files['file']
        
        if file.filename == '':
            return jsonify({
                'success': False,
                'error': 'No file selected'
            }), 400
        
        # Save file temporarily
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"resume_{timestamp}_{file.filename}"
        filepath = os.path.join(UPLOAD_FOLDER, filename)
        file.save(filepath)
        
        print(f"📄 Parsing resume: {filename}")
        
        # Parse resume
        resume_data = resume_parser.parse_file(filepath)
        
        if resume_data.get('is_fallback'):
            print(f"⚠️  Resume parsed with FALLBACK data (AI extraction failed)")
            if resume_data.get('warnings'):
                print(f"   Warnings: {resume_data['warnings']}")
        else:
            print(f"✅ Resume parsed successfully")
        
        return jsonify({
            'success': True,
            'data': resume_data,
            'message': 'Resume parsed successfully'
        })
    
    except Exception as e:
        print(f"❌ Error parsing resume: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/generate-description', methods=['POST'])
def generate_description():
    """
    Endpoint 2: Generate video description from resume data
    """
    try:
        if not GROQ_API_KEY:
            return jsonify({
                'success': False,
                'error': 'GROQ_API_KEY not configured'
            }), 500
        
        data = request.get_json()
        
        if not data or 'resume_data' not in data:
            return jsonify({
                'success': False,
                'error': 'No resume data provided'
            }), 400
        
        resume_data = data['resume_data']
        focus = data.get('focus', 'comprehensive')
        
        print(f"✨ Generating video description (focus: {focus})")
        
        # Generate description
        description = resume_parser.generate_video_description(
            resume_data=resume_data,
            focus=focus
        )
        
        print(f"✅ Description generated ({len(description)} chars)")
        
        return jsonify({
            'success': True,
            'description': description,
            'message': 'Description generated successfully'
        })
    
    except Exception as e:
        print(f"❌ Error generating description: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/generate', methods=['POST'])
def generate_video_jsons():
    """
    Endpoint 3: Generate master.json and clip JSONs
    """
    try:
        if not GROQ_API_KEY:
            return jsonify({
                'success': False,
                'error': 'GROQ_API_KEY not configured'
            }), 500
        
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['content_description', 'reference_image']
        for field in required_fields:
            if field not in data:
                return jsonify({
                    'success': False,
                    'error': f'Missing required field: {field}'
                }), 400
        
        # Extract parameters
        content_description = data['content_description']
        reference_image_base64 = data['reference_image']
        voice_tone = data.get('voice_tone', 'professional')
        speed = data.get('speed', '1x')
        num_clips = data.get('num_clips', 3)
        background_music = data.get('background_music', False)
        
        print(f"🎬 Generating video JSONs:")
        print(f"   - Clips: {num_clips}")
        print(f"   - Speed: {speed}")
        print(f"   - Tone: {voice_tone}")
        print(f"   - Music: {background_music}")
        
        # Save reference image
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        image_filename = f"reference_{timestamp}.jpg"
        image_path = save_base64_image(reference_image_base64, image_filename)
        
        print(f"📸 Reference image saved: {image_filename}")
        
        # Step 1: Build master JSON
        print("🏗️  Building master JSON...")
        master_json = master_builder.build_master(
            user_description=content_description,
            reference_image_path=image_path,
            num_clips=num_clips,
            speed=speed,
            background_music=background_music,
            user_tone=voice_tone,
            background_preset="keep_original"
        )
        
        # Step 2: Generate clip JSONs
        print("🎬 Generating clip JSONs...")
        clip_jsons = clip_generator.generate_all_clips(
            master_json=master_json,
            user_description=content_description
        )
        
        # Save JSONs to output folder (optional)
        master_output_path = os.path.join(OUTPUT_FOLDER, f'master_{timestamp}.json')
        master_builder.save_master_json(master_json, master_output_path)
        
        for i, clip in enumerate(clip_jsons):
            clip_output_path = os.path.join(OUTPUT_FOLDER, f'clip_{i+1}_{timestamp}.json')
            import json
            with open(clip_output_path, 'w', encoding='utf-8') as f:
                json.dump(clip, f, indent=2, ensure_ascii=False)
        
        print(f"✅ All JSONs generated successfully!")
        print(f"   - Master: {master_output_path}")
        print(f"   - Clips: {len(clip_jsons)} files")
        
        return jsonify({
            'success': True,
            'master': master_json,
            'clips': clip_jsons,
            'message': f'Generated master.json and {len(clip_jsons)} clip JSONs'
        })
    
    except Exception as e:
        print(f"❌ Error generating JSONs: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/test', methods=['GET'])
def test_endpoint():
    """
    Test endpoint to verify API key configuration
    """
    return jsonify({
        'success': True,
        'groq_api_configured': GROQ_API_KEY is not None,
        'components_initialized': {
            'resume_parser': resume_parser is not None,
            'master_builder': master_builder is not None,
            'clip_generator': clip_generator is not None
        },
        'message': 'Backend is ready!' if GROQ_API_KEY else 'Please configure GROQ_API_KEY in .env'
    })


# ============ ERROR HANDLERS ============

@app.errorhandler(404)
def not_found(error):
    return jsonify({
        'success': False,
        'error': 'Endpoint not found'
    }), 404


@app.errorhandler(500)
def internal_error(error):
    return jsonify({
        'success': False,
        'error': 'Internal server error'
    }), 500



# ============ MAIN ============

if __name__ == '__main__':
    print("\n" + "="*60)
    print("🎬 VEO DIALOGUE GENERATOR - BACKEND SERVER")
    print("="*60)
    
    # Get port from environment (Render sets this)
    port = int(os.getenv('PORT', 5001))
    
    print(f"📍 Server starting on port {port}")
    print(f"🔑 Groq API Key: {'✅ Configured' if GROQ_API_KEY else '❌ Not configured'}")
    print(f"📁 Upload folder: {UPLOAD_FOLDER}")
    print(f"📁 Output folder: {OUTPUT_FOLDER}")
    print("="*60)
    print("\n📋 Available Endpoints:")
    print("   GET  /              - Health check")
    print("   GET  /api/test      - Test API configuration")
    print("   POST /api/parse-resume        - Parse resume file")
    print("   POST /api/generate-description - Generate video script")
    print("   POST /api/generate            - Generate master & clip JSONs")
    print("="*60 + "\n")
    
    if not GROQ_API_KEY:
        print("⚠️  WARNING: GROQ_API_KEY not found!")
        print("Please create a .env file in the project root with:")
        print("GROQ_API_KEY=your_groq_api_key_here")
        print("\nGet your API key from: https://console.groq.com/keys")
        print("="*60 + "\n")
    
    # Run Flask app
    # When run with gunicorn, this code won't execute
    # When run locally with python app.py, it will use these settings
    app.run(
        host='0.0.0.0',
        port=port,
        debug=os.getenv('FLASK_ENV') != 'production'
    )

