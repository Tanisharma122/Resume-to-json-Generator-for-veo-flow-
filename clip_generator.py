"""
Clip JSON Generator
===================
Generates individual clip JSONs with structured dialogue:
1. First clip: Introduction (name + brief intro)
2. Subsequent clips: Content based on description
3. Speed-adaptive word counts ensuring 7.9s completion
"""

import json
import copy
import re
from typing import Dict, Any, List, Optional
from groq import Groq
from rules import get_veo_prompt_requirements


class ClipJSONGenerator:
    """
    Generates clip JSONs with structured, speed-adaptive dialogue.
    """
    
    def __init__(self, api_key: str, model: str = "llama-3.3-70b-versatile"):
        self.client = Groq(api_key=api_key)
        self.model = model
    
    def generate_all_clips(
        self,
        master_json: Dict[str, Any],
        user_description: str
    ) -> List[Dict[str, Any]]:
        """
        Generates all clip JSONs from master with structured dialogue.
        
        Args:
            master_json: The master JSON (from master_builder.py)
            user_description: User's original description
        
        Returns:
            List of clip JSON dictionaries
        """
        
        num_clips = master_json["project_metadata"]["total_clips"]
        
        # Get speed-based word limits from master
        timing_config = master_json["timing_config"]
        min_words = timing_config["min_words_per_clip"]
        target_words = timing_config["target_words_per_clip"]
        max_words = timing_config["max_words_per_clip"]
        speed_label = timing_config.get("speed_label", "Normal")
        words_per_second = timing_config["words_per_second"]
        
        # Get person name for intro
        person_name = master_json["person_identity"]["name"]
        person_role = master_json["person_identity"]["role"]
        
        print(f"⚡ Using speed: {speed_label} ({words_per_second} words/sec)")
        print(f"📝 Target: {target_words} words per clip ({min_words}-{max_words} range)")
        print(f"👤 Person: {person_name} - {person_role}")
        
        # Step 1: Segment description into structured dialogue
        print(f"🎬 Generating structured dialogue for {num_clips} clips...")
        dialogue_segments = self._generate_structured_dialogue(
            person_name=person_name,
            person_role=person_role,
            user_description=user_description,
            num_clips=num_clips,
            min_words=min_words,
            target_words=target_words,
            max_words=max_words,
            words_per_second=words_per_second,
            speed_label=speed_label
        )
        
        # Step 2: Generate clip JSONs
        clips = []
        previous_end_line = None
        
        for i in range(num_clips):
            clip_num = i + 1
            dialogue = dialogue_segments[i]
            
            print(f"🔨 Building Clip {clip_num} JSON...")
            clip = self.generate_clip(
                clip_number=clip_num,
                master_json=master_json,
                dialogue_text=dialogue,
                previous_clip_end=previous_end_line
            )
            
            clips.append(clip)
            
            # Store end of this dialogue for next clip's transition
            previous_end_line = self._get_last_sentence(dialogue)
        
        print(f"✅ All {num_clips} clip JSONs generated!")
        return clips
    
    def _generate_structured_dialogue(
        self,
        person_name: str,
        person_role: str,
        user_description: str,
        num_clips: int,
        min_words: int,
        target_words: int,
        max_words: int,
        words_per_second: float,
        speed_label: str
    ) -> List[str]:
        """
        Generates structured dialogue with intro first, then content.
        CRITICAL: First clip MUST be introduction only.
        """
        
        prompt = f"""
You are an expert dialogue creator for video generation.

PERSON INFORMATION:
- Name: {person_name}
- Role: {person_role}

CONTENT TO COVER:
{user_description}

YOUR TASK:
Create {num_clips} dialogue segments for video clips. Each segment will be spoken in an 8-second clip.

🔒 CRITICAL STRUCTURE RULES:

CLIP 1 (INTRODUCTION - MANDATORY FORMAT):
- MUST start with: "Hello, I'm {person_name}" or "Hi, I'm {person_name}"
- Follow with brief role/title introduction
- Keep it warm and welcoming
- Target: {target_words} words
- Complete introduction only - NO content details yet

CLIPS 2-{num_clips} (CONTENT):
- Cover the main content from the description above
- Build logically: overview → details → conclusion/call-to-action
- Each segment: complete, substantial thoughts
- Flow naturally between segments

⏱️ TIMING REQUIREMENTS (CRITICAL):
- Speed: {speed_label} ({words_per_second} words/second)
- Each dialogue MUST complete within 7.9 seconds
- Target words per clip: {target_words} words
- Acceptable range: {min_words}-{max_words} words
- At {words_per_second} words/sec, {target_words} words = ~{target_words/words_per_second:.1f} seconds
- YOU MUST hit the target word count for perfect timing

🎯 WORD COUNT PRECISION:
- If speed is NORMAL (3.0 w/s): Use {target_words} words (completes in ~{target_words/3.0:.1f}s)
- If speed is ENERGETIC (4.5 w/s): Use {target_words} words (completes in ~{target_words/4.5:.1f}s)  
- If speed is FAST (5.4 w/s): Use {target_words} words (completes in ~{target_words/5.4:.1f}s)

📝 DIALOGUE QUALITY:
- Natural, conversational, professional tone
- Complete sentences and thoughts
- NO filler words ("um", "uh", "like", "you know")
- Smooth transitions between clips
- First-person perspective ("I", "my", "we")
- Engaging and clear

EXAMPLE STRUCTURE:

For 3 clips at {speed_label} speed:
{{
  "segment_1": "Hello, I'm {person_name}, a {person_role}. I'm excited to share my journey and expertise with you today. Let me take you through what makes my experience unique and valuable.",
  "segment_2": "[Cover main content points from description - {target_words} words]",
  "segment_3": "[Conclude with impact/call-to-action - {target_words} words]"
}}

RETURN ONLY THIS JSON (no explanations):
{{
  "segment_1": "Introduction dialogue with exactly {target_words} words...",
  "segment_2": "Content dialogue with exactly {target_words} words...",
  "segment_3": "More content with exactly {target_words} words..."
}}

Add more segments if num_clips > 3. Use "segment_4", "segment_5", etc.

CRITICAL: 
- Return ONLY valid JSON
- No markdown formatting
- No extra text
- Each segment must be {min_words}-{max_words} words
- Segment 1 MUST be introduction with name
"""
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": f"You create structured dialogue hitting EXACT word counts. First segment MUST be introduction with person's name. Each segment must be {target_words} words (±{max_words-target_words} words). Return ONLY valid JSON."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.7,
                max_tokens=2000
            )
            
            raw_response = response.choices[0].message.content
            cleaned = self._clean_json_response(raw_response)
            segments_dict = json.loads(cleaned)
            
            # Extract segments with validation
            segments = []
            for i in range(1, num_clips + 1):
                key = f"segment_{i}"
                if key in segments_dict:
                    segment = segments_dict[key]
                    word_count = len(segment.split())
                    estimated_duration = word_count / words_per_second
                    
                    # Validate first clip is introduction
                    if i == 1:
                        if not any(greeting in segment.lower()[:20] for greeting in ['hello', 'hi', 'hey', 'greetings']):
                            print(f"⚠️  Clip 1 missing greeting! Adding introduction...")
                            segment = f"Hello, I'm {person_name}. {segment}"
                            word_count = len(segment.split())
                    
                    # Check timing
                    if estimated_duration > 7.9:
                        print(f"⚠️  Segment {i}: {word_count} words = {estimated_duration:.1f}s (TOO LONG, will cut at 7.9s)")
                    elif word_count < min_words:
                        print(f"⚠️  Segment {i}: {word_count} words (target: {target_words}) - too short")
                    else:
                        print(f"✅ Segment {i}: {word_count} words = {estimated_duration:.1f}s (perfect timing)")
                    
                    segments.append(segment)
                else:
                    # Fallback if segment missing
                    if i == 1:
                        segments.append(f"Hello, I'm {person_name}, a {person_role}. I'm excited to share my experience with you.")
                    else:
                        segments.append(f"Continuing from previous segment... [Clip {i}]")
            
            return segments
            
        except Exception as e:
            print(f"⚠️  Error generating dialogue: {e}")
            print("Using fallback structured dialogue...")
            return self._fallback_structured_dialogue(
                person_name, person_role, user_description, num_clips, target_words
            )
    
    def _fallback_structured_dialogue(
        self,
        person_name: str,
        person_role: str,
        description: str,
        num_clips: int,
        target_words: int
    ) -> List[str]:
        """
        Fallback: structured dialogue if LLM fails.
        First clip is ALWAYS introduction.
        """
        segments = []
        
        # Clip 1: Introduction (MANDATORY)
        intro = f"Hello, I'm {person_name}, a {person_role}. I'm excited to share my journey and expertise with you today."
        segments.append(intro)
        
        # Remaining clips: content
        if num_clips > 1:
            words = description.split()
            words_per_clip = len(words) // (num_clips - 1)
            
            for i in range(1, num_clips):
                start_idx = (i - 1) * words_per_clip
                end_idx = i * words_per_clip if i < num_clips - 1 else len(words)
                segment = ' '.join(words[start_idx:end_idx])
                segments.append(segment)
        
        return segments
    
    def generate_clip(
        self,
        clip_number: int,
        master_json: Dict[str, Any],
        dialogue_text: str,
        previous_clip_end: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Generates a single clip JSON.
        """
        
        # Calculate timing
        duration = master_json["timing_config"]["duration_seconds"]
        start_time = (clip_number - 1) * duration
        end_time = clip_number * duration
        
        # Deep copy ALL settings from master
        clip = {
            "clip_metadata": {
                "clip_number": clip_number,
                "start_time_seconds": start_time,
                "end_time_seconds": end_time,
                "duration_seconds": duration,
                "sequence_position": f"{clip_number}/{master_json['project_metadata']['total_clips']}"
            },
            
            # EXACT COPY from master
            "person_identity": copy.deepcopy(master_json["person_identity"]),
            "face_preservation": copy.deepcopy(master_json["face_preservation"]),
            "lip_sync_config": copy.deepcopy(master_json["lip_sync_config"]),
            "visual_settings": copy.deepcopy(master_json["visual_settings"]),
            "audio_profile": copy.deepcopy(master_json["audio_profile"]),
            "timing_config": copy.deepcopy(master_json["timing_config"]),
            "transition_rules": copy.deepcopy(master_json["transition_rules"]),
            
            # Reference to master
            "inherited_from_master": True,
            "master_reference": master_json["project_metadata"]["created_at"],
            
            # DIALOGUE (changes per clip)
            "dialogue": {
                "text": dialogue_text,
                "word_count": len(dialogue_text.split()),
                "estimated_duration_seconds": len(dialogue_text.split()) / master_json["timing_config"]["words_per_second"],
                "tone": master_json["person_identity"]["tone"],
                "speaking_style": master_json["person_identity"]["speaking_style"],
                "is_introduction": clip_number == 1
            },
            
            # Transition handling
            "transition": {
                "from_previous_clip": previous_clip_end if previous_clip_end else "Opening segment",
                "to_next_clip": self._get_transition_cue(dialogue_text, clip_number, master_json["project_metadata"]["total_clips"]),
                "continuity_check": "verify_face_position_matches_previous" if clip_number > 1 else "N/A",
                "voice_continuity_check": "verify_voice_matches_previous" if clip_number > 1 else "establish_voice_reference"
            },
            
            # VEO prompt
            "veo_prompt": self._build_veo_prompt(
                master=master_json,
                dialogue=dialogue_text,
                clip_num=clip_number
            ),
            
            # Keyframes
            "keyframes": self._generate_keyframes(
                clip_number=clip_number,
                duration=duration,
                is_last_clip=(clip_number == master_json["project_metadata"]["total_clips"])
            )
        }
        
        return clip
    
    def _build_veo_prompt(
        self,
        master: Dict[str, Any],
        dialogue: str,
        clip_num: int
    ) -> str:
        """
        Builds VEO prompt programmatically.
        """
        
        person = master["person_identity"]
        timing = master["timing_config"]
        visual = master["visual_settings"]
        total_clips = master["project_metadata"]["total_clips"]
        
        # Get background music status
        background_music_enabled = master["audio_profile"]["background_audio"]["music"]["enabled"]
        background_music_config = master["audio_profile"]["background_audio"]["music"]
        
        # Get rules text
        speed_config = {
            "words_per_second": timing["words_per_second"],
            "target_words": timing["target_words_per_clip"]
        }
        rules_text = get_veo_prompt_requirements(speed_config)
        
        # Build background music section
        if background_music_enabled:
            music_section = f"""
🎵 BACKGROUND MUSIC: {background_music_config['genre']} at {background_music_config['volume_percentage'] * 100}%
⚠️ CRITICAL: Voice generated FIRST, music added AFTER as separate layer
"""
        else:
            music_section = "🎵 BACKGROUND MUSIC: Disabled"
        
        prompt = f"""
🎬 SPEAKING PERSON VIDEO - CLIP {clip_num}/{total_clips}

{rules_text}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📋 PERSON: {person['name']} - {person['role']}
🎙️ TONE: {person['tone'].title()}
📹 BACKGROUND: {visual['background'].get('description', 'Original from reference image')}
{music_section}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🎙️ DIALOGUE (MUST COMPLETE IN 7.9 SECONDS):

"{dialogue}"

⏱️ TIMING:
- Word Count: {len(dialogue.split())} words
- Speed: {timing['words_per_second']} words/second
- Estimated Duration: {len(dialogue.split()) / timing['words_per_second']:.1f} seconds
- MUST complete by: 7.9 seconds
- Clip total: 8.0 seconds

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🔒 CONSISTENCY LOCKS:
- Face: 99% similarity to {"Clip 1 (establish reference)" if clip_num == 1 else "Clip 1 (LOCKED)"}
- Voice: 99% similarity to {"Clip 1 (establish reference)" if clip_num == 1 else "Clip 1 (LOCKED)"}
- Background: Pixel-perfect match across all clips
- Lighting: Identical across all clips

🙌 NATURAL GESTURES: 1-3 subtle gestures per clip, professional and organic

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

✅ GENERATE: Follow all rules strictly, complete dialogue in 7.9s
""".strip()
        
        return prompt
    
    def _generate_keyframes(
        self,
        clip_number: int,
        duration: int,
        is_last_clip: bool
    ) -> List[Dict[str, Any]]:
        """
        Generates keyframes programmatically.
        """
        
        keyframes = [
            {
                "time": 0.0,
                "action": "segment_start",
                "properties": {
                    "fade_in": "0.3s" if clip_number == 1 else "none",
                    "face_check": "verify_reference_match",
                    "voice_check": "verify_voice_reference_match" if clip_number > 1 else "establish_voice_reference",
                    "expression": "neutral_to_natural"
                }
            },
            {
                "time": 7.9,
                "action": "dialogue_completion",
                "properties": {
                    "description": "Dialogue must complete by this point",
                    "voice_level": "natural_completion",
                    "prepare_transition": True
                }
            },
            {
                "time": duration - 0.1,
                "action": "segment_end",
                "properties": {
                    "fade_out": "0.4s" if is_last_clip else "none",
                    "position": "exact_hold_for_cut",
                    "next_segment_sync": "position_match_required" if not is_last_clip else "final_frame"
                }
            }
        ]
        
        return keyframes
    
    def _get_transition_cue(self, dialogue: str, clip_num: int, total_clips: int) -> str:
        """
        Determines transition cue.
        """
        if clip_num == total_clips:
            return "Final segment - natural close"
        
        last_sentence = self._get_last_sentence(dialogue)
        return f"Continue from: {last_sentence}"
    
    def _get_last_sentence(self, text: str) -> str:
        """
        Extracts last sentence.
        """
        sentences = re.split(r'[.!?]+', text.strip())
        sentences = [s.strip() for s in sentences if s.strip()]
        return sentences[-1] if sentences else text.strip()
    
    def _clean_json_response(self, response: str) -> str:
        """
        Cleans LLM response to extract valid JSON.
        """
        response = re.sub(r'```json\s*', '', response)
        response = re.sub(r'```\s*', '', response)
        
        match = re.search(r'\{', response)
        if match:
            response = response[match.start():]
        
        match = re.search(r'\}[^}]*$', response)
        if match:
            response = response[:match.end()]
        
        return response.strip()
