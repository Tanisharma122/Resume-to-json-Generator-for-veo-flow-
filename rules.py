"""
VEO Consistency Rules
=====================
Immutable rules for VEO 3.1 video generation.
These rules ensure 99% face and voice consistency.
"""

from typing import Dict, Any


# ============ SPEED CONFIGURATIONS ============
SPEED_CONFIGS = {
    "1x": {
        "words_per_second": 3.0,
        "target_words": 24,
        "min_words": 20,
        "max_words": 28,
        "speed_label": "Normal",
        "speed_description": "Natural conversational pace"
    },
    "1.5x": {
        "words_per_second": 4.5,
        "target_words": 36,
        "min_words": 31,
        "max_words": 40,
        "speed_label": "Energetic",
        "speed_description": "Lively and engaging pace"
    },
    "2x": {
        "words_per_second": 5.4,
        "target_words": 43,
        "min_words": 38,
        "max_words": 48,
        "speed_label": "Fast",
        "speed_description": "Quick and dynamic pace"
    }
}


def calculate_words_for_speed(speed: str) -> Dict[str, Any]:
    """
    Returns word count targets for given speed.
    
    Args:
        speed: "1x", "1.5x", or "2x"
    
    Returns:
        Dictionary with speed configuration
    """
    if speed not in SPEED_CONFIGS:
        speed = "1x"  # Default
    
    return SPEED_CONFIGS[speed].copy()


# ============ VEO CONSISTENCY RULES ============
class VEOConsistencyRules:
    """
    Immutable rules for VEO 3.1 consistency.
    These rules NEVER change regardless of user input.
    """
    
    # Face preservation settings
    FACE_PRESERVATION = {
        "mode": "ABSOLUTE_LOCK",
        "consistency_threshold": 0.99,
        "validation_method": "pixel_level_facial_recognition",
        "locked_features": [
            "facial_structure",
            "eye_shape",
            "eye_color",
            "eye_spacing",
            "nose_geometry",
            "mouth_shape",
            "lip_fullness",
            "skin_tone",
            "age_appearance",
            "facial_hair",
            "eyebrow_shape",
            "distinctive_marks"
        ],
        "forbidden_modifications": [
            "beautification_filters",
            "skin_smoothing",
            "age_modification",
            "feature_enhancement",
            "skin_tone_changes"
        ],
        "enforcement": "auto_reject_if_below_97_percent"
    }
    
    # Lip sync configuration
    LIP_SYNC_CONFIG = {
        "method": "phoneme_accurate",
        "sync_precision": "frame_perfect",
        "max_deviation_ms": 16.67,
        "phoneme_mapping": "detailed_IPA_with_coarticulation",
        "mouth_closure": "automatic_when_silent",
        "breathing_sync": "natural_pauses_synchronized"
    }
    
    # Visual settings
    VISUAL_SETTINGS = {
        "camera": {
            "shot_type": "medium_close_up",
            "angle": "eye_level",
            "movement": "static_locked",
            "framing": "professional_portrait"
        },
        "lighting": {
            "setup": "three_point_studio",
            "key_light": "soft_frontal_45deg",
            "fill_light": "opposite_side_subtle",
            "back_light": "separation_from_background",
            "consistency": "IDENTICAL_across_all_clips"
        },
        "background_presets": {
            "professional_gradient": {
                "type": "gradient",
                "primary_color": "#1a365d",
                "secondary_color": "#2d5a8f",
                "description": "Professional blue gradient"
            },
            "warm_office": {
                "type": "gradient",
                "primary_color": "#78350f",
                "secondary_color": "#92400e",
                "description": "Warm brown office ambiance"
            },
            "modern_tech": {
                "type": "gradient",
                "primary_color": "#1e293b",
                "secondary_color": "#334155",
                "description": "Modern tech gray"
            },
            "creative_purple": {
                "type": "gradient",
                "primary_color": "#4c1d95",
                "secondary_color": "#6d28d9",
                "description": "Creative purple gradient"
            }
        },
        "background": {
            "type": "keep_original",
            "consistency": "PIXEL_PERFECT_match_across_all_clips"
        },
        "technical_specs": {
            "resolution": "1920x1080",
            "aspect_ratio": "16:9",
            "fps": 60,
            "color_space": "sRGB"
        }
    }
    
    # Audio profile
    AUDIO_PROFILE = {
        "voice_consistency": {
            "mode": "ABSOLUTE_VOICE_LOCK",
            "consistency_threshold": 0.99,
            "validation_method": "spectral_voice_fingerprint",
            "locked_voice_features": [
                "pitch_range",
                "vocal_timbre",
                "speech_rhythm",
                "accent_dialect",
                "pronunciation_style",
                "voice_texture",
                "resonance_frequencies",
                "breathiness_level",
                "vocal_register",
                "intonation_patterns"
            ],
            "forbidden_modifications": [
                "voice_change",
                "pitch_shifting",
                "timbre_modification",
                "accent_changes",
                "speed_modification_beyond_selected"
            ],
            "enforcement": "auto_reject_if_below_97_percent"
        },
        "audio_quality": {
            "sample_rate": "48kHz",
            "bit_depth": "24-bit",
            "channels": "stereo",
            "noise_floor": "-60dB",
            "dynamic_range": "professional_broadcast"
        },
        "background_audio": {
            "music": {
                "enabled": False,
                "type": "none",
                "volume_db": -100,
                "volume_percentage": 0.0,
                "fade_in_duration": 0.0,
                "fade_out_duration": 0.0,
                "consistency": "IDENTICAL_ACROSS_ALL_CLIPS"
            }
        }
    }
    
    # Timing configuration (base - overridden by speed selection)
    TIMING_CONFIG = {
        "duration_seconds": 8,
        "dialogue_completion_target": 7.9,
        "buffer_seconds": 0.1,
        "words_per_second": 3.0,
        "target_words_per_clip": 24,
        "min_words_per_clip": 20,
        "max_words_per_clip": 28
    }
    
    # Transition rules
    TRANSITION_RULES = {
        "clip_to_clip": "seamless_cut",
        "face_position": "EXACT_MATCH_required",
        "voice_continuity": "EXACT_MATCH_required",
        "visual_continuity": "EXACT_MATCH_required",
        "background_continuity": "PIXEL_PERFECT_required",
        "lighting_continuity": "IDENTICAL_required",
        "cut_timing": "on_natural_pause",
        "no_fades_between_clips": True
    }


def get_immutable_rules() -> Dict[str, Any]:
    """
    Returns all immutable VEO rules as a dictionary.
    These rules are copied into master.json.
    """
    return {
        "face_preservation": VEOConsistencyRules.FACE_PRESERVATION,
        "lip_sync_config": VEOConsistencyRules.LIP_SYNC_CONFIG,
        "visual_settings": VEOConsistencyRules.VISUAL_SETTINGS,
        "audio_profile": VEOConsistencyRules.AUDIO_PROFILE,
        "timing_config": VEOConsistencyRules.TIMING_CONFIG,
        "transition_rules": VEOConsistencyRules.TRANSITION_RULES
    }


def get_veo_prompt_requirements(speed_config: Dict[str, Any]) -> str:
    """
    Returns the VEO prompt requirements text with speed configuration.
    
    Args:
        speed_config: Dictionary with words_per_second and target_words
    
    Returns:
        Formatted requirements string
    """
    return f"""
⚠️ CRITICAL VEO 3.1 REQUIREMENTS - READ CAREFULLY

🔒 FACE & VOICE CONSISTENCY:
- Face similarity: 99% threshold (ABSOLUTE REQUIREMENT)
- Voice similarity: 99% threshold (ABSOLUTE REQUIREMENT)
- Any clip below 97% similarity: AUTO-REJECT
- Validation: Pixel-level facial recognition + spectral voice analysis

⏱️ TIMING REQUIREMENTS:
- Clip duration: EXACTLY 8 seconds
- Dialogue MUST complete within 7.9 seconds
- Speaking pace: {speed_config['words_per_second']} words/second
- Target word count: ~{speed_config['target_words']} words
- Buffer: 0.1 seconds before clip end

🎙️ VOICE PROCESSING ORDER (CRITICAL):
1. GENERATE VOICE FIRST - completely independently
2. LOCK VOICE at 99% similarity to first clip
3. ADD MUSIC AFTER - as separate layer (if enabled)
4. Voice and music are SEPARATE tracks
5. Music CANNOT affect voice characteristics

🎬 GENERATION REQUIREMENTS:
- All clips MUST use IDENTICAL visual settings
- Background MUST be pixel-perfect match across clips
- Lighting MUST be identical across clips
- Camera position MUST be locked (no movement)
- Face position MUST match exactly at clip boundaries
- Voice characteristics MUST be locked from Clip 1
""".strip()
