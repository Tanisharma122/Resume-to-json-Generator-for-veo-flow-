"""
Master JSON Builder
===================
Builds the master.json file from user input.
LLM is used ONLY to extract person details.
All rules come from rules.py (immutable).
"""

import json
import re
from typing import Dict, Any, Optional
from datetime import datetime
from groq import Groq
from rules import get_immutable_rules, VEOConsistencyRules, calculate_words_for_speed


class MasterJSONBuilder:
    """
    Builds master.json with locked rules + user-specific person details.
    """
    
    def __init__(self, api_key: str, model: str = "llama-3.3-70b-versatile"):
        self.client = Groq(api_key=api_key)
        self.model = model
    
    def build_master(
        self,
        user_description: str,
        reference_image_path: str,
        num_clips: int = 3,
        speed: str = "1x",
        background_music: bool = False,
        user_tone: Optional[str] = None,
        background_preset: str = "keep_original",
        background_custom: Optional[str] = None,
        additional_instructions: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Main method: builds complete master.json
        """
        
        # Step 1: Calculate speed-based timing
        print(f"⚡ Calculating timing for speed: {speed}")
        speed_config = calculate_words_for_speed(speed)
        
        # Step 2: Extract person details using LLM
        print("🔍 Extracting person details from description...")
        person_details = self._extract_person_details(user_description)
        
        # Override tone if user provided one
        if user_tone:
            print(f"🎙️  Using user-selected tone: {user_tone}")
            person_details['tone'] = user_tone
        else:
            print(f"🎙️  Using AI-inferred tone: {person_details.get('tone', 'professional')}")
        
        # Step 3: Get immutable rules from rules.py
        print("🔒 Loading immutable VEO rules...")
        immutable_rules = get_immutable_rules()
        
        # Step 4: Apply background preset
        if background_preset == "keep_original":
            print("🎨 Keeping original background from reference image")
            background_config = {
                "type": "keep_original",
                "source": "reference_image",
                "description": "Use exact background from reference image - no modification",
                "consistency": "IDENTICAL_ACROSS_ALL_CLIPS",
                "extract_from": reference_image_path
            }
        elif background_preset == "custom":
            if background_custom:
                print(f"🎨 Using custom background: {background_custom[:50]}...")
                background_config = {
                    "type": "custom_description",
                    "description": background_custom,
                    "consistency": "IDENTICAL_ACROSS_ALL_CLIPS",
                    "user_provided": True
                }
            else:
                print("⚠️  No custom description provided, keeping original")
                background_config = {
                    "type": "keep_original",
                    "source": "reference_image",
                    "description": "Use exact background from reference image",
                    "consistency": "IDENTICAL_ACROSS_ALL_CLIPS",
                    "extract_from": reference_image_path
                }
        else:
            print(f"🎨 Applying background preset: {background_preset}")
            background_config = self._apply_background_preset(immutable_rules, background_preset)
        
        # Step 5: Configure background music settings
        background_music_config = self._get_background_music_config(background_music)
        
        # Step 6: Build master JSON
        print("🏗️  Building master JSON...")
        master = {
            "project_metadata": {
                "type": "speaking_person_video",
                "version": "VEO_3.1_compatible",
                "total_clips": num_clips,
                "clip_duration_seconds": 8,
                "total_duration_seconds": num_clips * 8,
                "speaking_speed": speed,
                "speed_config": speed_config,
                "background_music_enabled": background_music,
                "background_preset": background_preset,
                "background_custom": background_custom if background_custom else None,
                "has_additional_instructions": bool(additional_instructions),
                "created_at": datetime.utcnow().isoformat(),
                "generator": "VEO_JSON_Backend_v1.0"
            },
            
            "reference_image": {
                "path": reference_image_path,
                "usage": "STRICT_FACE_REFERENCE",
                "description": "This face MUST be preserved exactly across all clips",
                "requirements": [
                    "Frontal view (±15° max rotation)",
                    "Clear, well-lit face",
                    "Neutral or friendly expression",
                    "High resolution (1024x1024+ recommended)"
                ]
            },
            
            "person_identity": person_details,
            
            "additional_instructions": {
                "enabled": bool(additional_instructions),
                "instructions": additional_instructions if additional_instructions else None,
                "apply_to_all_clips": True,
                "description": "User-provided specific requirements (clothing, styling, modifications, etc.)"
            },
            
            **immutable_rules,
            
            "visual_settings": {
                **immutable_rules["visual_settings"],
                "background": background_config
            },
            
            "timing_config": {
                **immutable_rules["timing_config"],
                "selected_speed": speed,
                "words_per_second": speed_config["words_per_second"],
                "target_words_per_clip": speed_config["target_words"],
                "min_words_per_clip": speed_config["min_words"],
                "max_words_per_clip": speed_config["max_words"],
                "speed_label": speed_config["speed_label"],
                "speed_description": speed_config["speed_description"]
            },
            
            "audio_profile": {
                **immutable_rules["audio_profile"],
                "background_audio": {
                    **immutable_rules["audio_profile"]["background_audio"],
                    "music": background_music_config
                }
            },
            
            "continuity_settings": {
                "narrative_flow": "connected_story",
                "transition_style": "seamless",
                "maintain_across_clips": [
                    "person_identity",
                    "face_appearance",
                    "voice_characteristics",
                    "visual_settings",
                    "audio_profile",
                    "background",
                    "lighting",
                    "camera_setup",
                    "background_music_settings"
                ]
            },
            
            "quality_requirements": {
                "minimum_face_similarity": 0.99,
                "minimum_voice_similarity": 0.99,
                "lip_sync_accuracy": "frame_perfect",
                "transition_smoothness": "invisible_cuts",
                "audio_video_sync": "perfect",
                "voice_consistency_check": "REQUIRED",
                "reject_if_any_rule_violated": True
            }
        }
        
        print(f"✅ Master JSON built successfully!")
        print(f"   Tone: {person_details['tone'].title()}")
        print(f"   Speed: {speed_config['speed_label']} ({speed_config['words_per_second']} words/sec)")
        
        if background_preset == "keep_original":
            print(f"   Background: Original (from image)")
        elif background_preset == "custom":
            print(f"   Background: Custom - {background_custom[:50] if background_custom else 'None'}...")
        else:
            print(f"   Background: {background_preset.replace('_', ' ').title()}")
        
        print(f"   Background Music: {'Enabled (15% volume)' if background_music else 'Disabled'}")
        
        return master
    
    def _apply_background_preset(
        self,
        immutable_rules: Dict[str, Any],
        preset_name: str
    ) -> Dict[str, Any]:
        """Applies a background preset from rules.py"""
        presets = immutable_rules["visual_settings"]["background_presets"]
        
        if preset_name not in presets:
            print(f"⚠️  Unknown preset '{preset_name}', using default")
            preset_name = "professional_gradient"
        
        preset = presets[preset_name].copy()
        preset["consistency"] = "IDENTICAL_ACROSS_ALL_CLIPS"
        preset["preset_name"] = preset_name
        
        return preset
    
    def _get_background_music_config(self, enabled: bool) -> Dict[str, Any]:
        """Returns background music configuration"""
        base_config = VEOConsistencyRules.AUDIO_PROFILE["background_audio"]["music"].copy()
        
        if enabled:
            return {
                **base_config,
                "enabled": True,
                "type": "ambient_subtle",
                "genre": "ambient_subtle",
                "volume_db": -40,
                "volume_percentage": 0.15,
                "description": "Subtle ambient background music at 15% volume (-40dB)"
            }
        else:
            return {
                **base_config,
                "enabled": False,
                "type": "none",
                "volume_db": -100,
                "volume_percentage": 0.0,
                "description": "No background music"
            }
    
    def _extract_person_details(self, user_description: str) -> Dict[str, Any]:
        """Uses LLM to extract person details from description"""
        
        prompt = f"""
You are a person detail extractor for video generation.

USER DESCRIPTION:
{user_description}

TASK:
Extract the following details about the person. If not explicitly mentioned, make reasonable professional assumptions.

RETURN ONLY THIS JSON (no other text):
{{
  "name": "Full name of the person",
  "role": "Their role/title (e.g., 'LDRP College Student', 'Software Engineer')",
  "tone": "Speaking tone (choose one: professional, friendly, confident, enthusiastic, warm)",
  "appearance": {{
    "gender": "male/female/non-binary (infer from name/description)",
    "age_range": "Estimated age range (e.g., '20-25', '30-35')",
    "clothing": "What they're wearing (e.g., 'business casual', 'college attire', 'formal')",
    "distinctive_features": "Any mentioned features (e.g., 'glasses', 'long hair')"
  }},
  "key_points": [
    "Main point 1 from description",
    "Main point 2 from description",
    "Main point 3 from description"
  ],
  "speaking_style": "How they speak (e.g., 'clear and articulate', 'conversational')"
}}

CRITICAL: Return ONLY valid JSON. No markdown, no explanations, no extra text.
"""
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You extract person details and return ONLY valid JSON. No markdown formatting."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                max_tokens=500
            )
            
            raw_response = response.choices[0].message.content
            cleaned = self._clean_json_response(raw_response)
            person_details = json.loads(cleaned)
            
            required_fields = ["name", "role", "tone", "appearance", "key_points"]
            for field in required_fields:
                if field not in person_details:
                    raise ValueError(f"Missing required field: {field}")
            
            return person_details
            
        except Exception as e:
            print(f"⚠️  Error extracting person details: {e}")
            print("Using fallback default person details...")
            return self._fallback_person_details(user_description)
    
    def _clean_json_response(self, response: str) -> str:
        """Cleans LLM response to extract valid JSON"""
        response = re.sub(r'```json\s*', '', response)
        response = re.sub(r'```\s*', '', response)
        
        match = re.search(r'\{', response)
        if match:
            response = response[match.start():]
        
        match = re.search(r'\}[^}]*$', response)
        if match:
            response = response[:match.end()]
        
        return response.strip()
    
    def _fallback_person_details(self, description: str) -> Dict[str, Any]:
        """Fallback person details if LLM extraction fails"""
        name_match = re.search(r"(?:I'm|I am|My name is)\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)", description)
        name = name_match.group(1) if name_match else "Speaker"
        
        return {
            "name": name,
            "role": "Professional Speaker",
            "tone": "professional",
            "appearance": {
                "gender": "unknown",
                "age_range": "25-35",
                "clothing": "professional attire",
                "distinctive_features": "as shown in reference image"
            },
            "key_points": [
                "Professional background",
                "Relevant experience",
                "Call to action"
            ],
            "speaking_style": "clear and articulate"
        }
    
    def save_master_json(self, master: Dict[str, Any], output_path: str = "master.json") -> str:
        """Saves master JSON to file"""
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(master, f, indent=2, ensure_ascii=False)
        
        print(f"💾 Master JSON saved to: {output_path}")
        return output_path
