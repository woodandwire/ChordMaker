"""
Guitar Chord Fingering Validator

This module provides a validation system to check if guitar chord fingerings 
are physically possible to play. It uses a rule-based system to evaluate
various constraints such as finger reach, hand position, and ergonomics.
"""

from typing import List, Tuple, Dict, Any, Optional, Union
from enum import Enum
from dataclasses import dataclass
import math


class ValidationResult(Enum):
    """HTTP-style validation result codes."""
    # 2xx - Success
    VALID = 200
    VALID_WITH_WARNINGS = 201
    
    # 4xx - Client/Input Errors
    INVALID_INPUT = 400
    PHYSICALLY_IMPOSSIBLE = 401
    EXCESSIVE_STRETCH = 402
    FINGER_COLLISION = 403
    THUMB_POSITION_ERROR = 404
    TOO_MANY_FINGERS = 405
    INCONSISTENT_BARRE = 406
    
    # 5xx - Validator Errors
    VALIDATION_ENGINE_ERROR = 500


@dataclass
class ValidationMessage:
    """A validation message with severity and description."""
    code: ValidationResult
    severity: str  # 'error', 'warning', 'info'
    message: str
    rule_name: str
    affected_strings: Optional[List[int]] = None


@dataclass
class FingerPosition:
    """Represents a finger position on the fretboard."""
    finger: str  # '1', '2', '3', '4', 'T' (thumb)
    string: int  # String number (1-6, where 1 is high E)
    fret: int    # Fret number (0 = open)


@dataclass
class HandPosition:
    """Represents the overall hand position and constraints."""
    min_fret: int
    max_fret: int
    fret_span: int
    thumb_fret: Optional[int] = None
    barre_fret: Optional[int] = None
    barre_strings: Optional[List[int]] = None
    
    def __post_init__(self):
        if self.barre_strings is None:
            self.barre_strings = []


class ChordFingeringValidator:
    """
    Validates guitar chord fingerings for physical playability.
    
    The validator uses a rule-based system to check various constraints
    and returns HTTP-style status codes with detailed messages.
    """
    
    def __init__(self, thumb_reach_strings: int = 1):
        """
        Initialize the validator with default settings.
        
        Args:
            thumb_reach_strings: Number of strings the thumb can reach (1-6)
                                1 = only 6th string (most common)
                                2 = 6th and 5th strings (larger hands)
                                3+ = exceptional reach (rare)
                                0 = no thumb fretting allowed
        """
        # Configuration settings
        self.max_fret_span = 4  # Maximum fret span for most players
        self.max_finger_stretch = 5  # Maximum stretch between fingers
        self.thumb_reach_strings = max(0, min(6, thumb_reach_strings))  # Clamp to 0-6
        self.max_simultaneous_fingers = 4  # Maximum fingers used at once
        
        # Rule weights for scoring
        self.rule_weights = {
            'basic_validation': 1.0,
            'fret_span_check': 0.9,
            'finger_stretch_check': 0.8,
            'finger_collision_check': 1.0,
            'thumb_position_check': 0.7,
            'barre_consistency_check': 0.9,
            'ergonomic_assessment': 0.6
        }
        
        # Initialize validation results
        self.reset_validation()
    
    def reset_validation(self) -> None:
        """Reset validation state for a new chord."""
        self.messages: List[ValidationMessage] = []
        self.finger_positions: List[FingerPosition] = []
        self.hand_position: Optional[HandPosition] = None
        self.overall_result: ValidationResult = ValidationResult.VALID
    
    def validate_chord(self, chord_data: List[Tuple[str, int]]) -> Dict[str, Any]:
        """
        Main validation method that processes a chord pattern.
        
        Args:
            chord_data: List of tuples (finger_indicator, fret_number) for each string
                       finger_indicator: 'X' (muted), 'O' (open), '1'-'4' (fingers), 'T' (thumb)
                       fret_number: Fret position (ignored for 'X' and 'O')
        
        Returns:
            Dict containing validation results with HTTP-style status codes
        """
        self.reset_validation()
        
        try:
            # Parse input data
            if not self._parse_chord_data(chord_data):
                return self._build_result(ValidationResult.INVALID_INPUT)
            
            # Calculate hand position
            self._calculate_hand_position()
            
            # Run validation rules
            self._run_validation_rules()
            
            # Determine overall result
            self._determine_overall_result()
            
            return self._build_result(self.overall_result)
            
        except Exception as e:
            self.messages.append(ValidationMessage(
                code=ValidationResult.VALIDATION_ENGINE_ERROR,
                severity='error',
                message=f"Validation engine error: {str(e)}",
                rule_name='system'
            ))
            return self._build_result(ValidationResult.VALIDATION_ENGINE_ERROR)
    
    def _parse_chord_data(self, chord_data: List[Tuple[str, int]]) -> bool:
        """Parse chord data into finger positions."""
        if not chord_data or len(chord_data) != 6:
            self.messages.append(ValidationMessage(
                code=ValidationResult.INVALID_INPUT,
                severity='error',
                message="Chord data must contain exactly 6 string specifications",
                rule_name='input_validation'
            ))
            return False
        
        self.finger_positions = []
        
        for string_num, (finger, fret) in enumerate(chord_data, 1):
            
            # Skip muted and open strings
            if finger in ['X', 'O']:
                continue
            
            # Validate finger indicator
            if finger not in ['1', '2', '3', '4', 'T']:
                self.messages.append(ValidationMessage(
                    code=ValidationResult.INVALID_INPUT,
                    severity='error',
                    message=f"Invalid finger indicator '{finger}' on string {string_num}",
                    rule_name='input_validation',
                    affected_strings=[string_num]
                ))
                return False
            
            # Validate fret number
            if not (0 <= fret <= 24):  # Reasonable fret range
                self.messages.append(ValidationMessage(
                    code=ValidationResult.INVALID_INPUT,
                    severity='error',
                    message=f"Invalid fret number {fret} on string {string_num}",
                    rule_name='input_validation',
                    affected_strings=[string_num]
                ))
                return False
            
            # Check for logical inconsistency: finger on fret 0
            if fret == 0:
                self.messages.append(ValidationMessage(
                    code=ValidationResult.INVALID_INPUT,
                    severity='error',
                    message=f"Invalid input: finger '{finger}' specified for fret 0 on string {string_num}. Use 'O' for open strings instead.",
                    rule_name='input_validation',
                    affected_strings=[string_num]
                ))
                return False
            
            self.finger_positions.append(FingerPosition(finger, string_num, fret))
        
        return True
    
    def _calculate_hand_position(self) -> None:
        """Calculate overall hand position from finger positions."""
        if not self.finger_positions:
            self.hand_position = HandPosition(0, 0, 0)
            return
        
        frets = [pos.fret for pos in self.finger_positions if pos.fret > 0]
        
        if not frets:
            self.hand_position = HandPosition(0, 0, 0)
            return
        
        min_fret = min(frets)
        max_fret = max(frets)
        fret_span = max_fret - min_fret
        
        # Check for barre chords (same finger on multiple strings at same fret)
        # Also validate that barre doesn't skip over strings that should be fretted
        finger_fret_map = {}
        for pos in self.finger_positions:
            key = (pos.finger, pos.fret)
            if key not in finger_fret_map:
                finger_fret_map[key] = []
            finger_fret_map[key].append(pos.string)
        
        barre_fret = None
        barre_strings = []
        for (finger, fret), strings in finger_fret_map.items():
            if len(strings) > 1 and finger != 'T':  # Thumb can't barre
                # Sort strings to check for gaps
                strings_sorted = sorted(strings)
                
                # Check if there are gaps in the barre that would require open strings
                has_gaps = False
                for i in range(len(strings_sorted) - 1):
                    string_gap = strings_sorted[i + 1] - strings_sorted[i]
                    if string_gap > 1:  # There's a gap between strings
                        # Check if the skipped strings are actually open or muted
                        for skip_string in range(strings_sorted[i] + 1, strings_sorted[i + 1]):
                            # Look for this string in finger positions
                            string_is_fretted = any(pos.string == skip_string for pos in self.finger_positions)
                            if not string_is_fretted:
                                has_gaps = True
                                break
                    if has_gaps:
                        break
                
                # Only consider it a valid barre if there are no problematic gaps
                if not has_gaps:
                    barre_fret = fret
                    barre_strings = strings
                    break
        
        # Check thumb position
        thumb_fret = None
        for pos in self.finger_positions:
            if pos.finger == 'T':
                thumb_fret = pos.fret
                break
        
        self.hand_position = HandPosition(
            min_fret=min_fret,
            max_fret=max_fret,
            fret_span=fret_span,
            thumb_fret=thumb_fret,
            barre_fret=barre_fret,
            barre_strings=barre_strings
        )
    
    def _run_validation_rules(self) -> None:
        """Execute all validation rules."""
        self._rule_basic_validation()
        self._rule_fret_span_check()
        self._rule_finger_stretch_check()
        self._rule_finger_collision_check()
        self._rule_thumb_position_check()
        self._rule_barre_consistency_check()
        self._rule_ergonomic_assessment()
    
    def _rule_basic_validation(self) -> None:
        """Basic validation rules - finger count, impossible positions, etc."""
        rule_name = 'basic_validation'
        
        # Check for fingers on fret 0 (impossible - open strings can't have fingers)
        for pos in self.finger_positions:
            if pos.fret == 0:
                self.messages.append(ValidationMessage(
                    code=ValidationResult.PHYSICALLY_IMPOSSIBLE,
                    severity='error',
                    message=f"Finger {pos.finger} cannot be placed on fret 0 (open string) on string {pos.string}",
                    rule_name=rule_name,
                    affected_strings=[pos.string]
                ))
        
        # Check maximum number of fingers used simultaneously
        unique_fingers = set(pos.finger for pos in self.finger_positions if pos.finger != 'T')
        if len(unique_fingers) > self.max_simultaneous_fingers:
            self.messages.append(ValidationMessage(
                code=ValidationResult.TOO_MANY_FINGERS,
                severity='error',
                message=f"Using {len(unique_fingers)} fingers exceeds maximum of {self.max_simultaneous_fingers}",
                rule_name=rule_name
            ))
        
        # Check for duplicate finger usage on different frets (except barre chords)
        finger_fret_map = {}
        for pos in self.finger_positions:
            if pos.finger not in finger_fret_map:
                finger_fret_map[pos.finger] = []
            finger_fret_map[pos.finger].append(pos.fret)
        
        for finger, frets in finger_fret_map.items():
            unique_frets = set(frets)
            if len(unique_frets) > 1:
                self.messages.append(ValidationMessage(
                    code=ValidationResult.PHYSICALLY_IMPOSSIBLE,
                    severity='error',
                    message=f"Finger {finger} cannot be on multiple different frets: {sorted(unique_frets)}",
                    rule_name=rule_name
                ))
        
        # Check for impossible finger assignments (finger order)
        finger_frets = {}
        for pos in self.finger_positions:
            if pos.finger.isdigit():  # Only check numbered fingers, not thumb
                finger_frets[int(pos.finger)] = pos.fret
        
        # Sort fingers by number and check fret order makes anatomical sense
        sorted_fingers = sorted(finger_frets.items())
        for i in range(len(sorted_fingers) - 1):
            finger_num, fret = sorted_fingers[i]
            next_finger_num, next_fret = sorted_fingers[i + 1]
            
            # Higher numbered fingers should generally be on higher or equal frets
            # Allow some flexibility (1-2 fret difference) for chord shapes
            if next_fret < fret - 2:
                self.messages.append(ValidationMessage(
                    code=ValidationResult.PHYSICALLY_IMPOSSIBLE,
                    severity='warning',
                    message=f"Finger {next_finger_num} on fret {next_fret} is unusually far behind finger {finger_num} on fret {fret}",
                    rule_name=rule_name
                ))
        
        pass  # Additional rules placeholder
    
    def _rule_fret_span_check(self) -> None:
        """Check if the fret span is within human reach limits."""
        rule_name = 'fret_span_check'
        
        if not self.hand_position:
            return
        
        # Implement fret span validation
        if self.hand_position.fret_span > self.max_fret_span:
            severity = 'error' if self.hand_position.fret_span > self.max_fret_span + 2 else 'warning'
            self.messages.append(ValidationMessage(
                code=ValidationResult.EXCESSIVE_STRETCH,
                severity=severity,
                message=f"Fret span of {self.hand_position.fret_span} {'exceeds' if severity == 'error' else 'approaches'} maximum of {self.max_fret_span}",
                rule_name=rule_name
            ))
        
        # Consider player skill level adjustments
        # Beginners: reduce max span by 1, Advanced: can handle +1 fret span
        # This is handled by the configuration, but we can add warnings
        if self.hand_position.fret_span >= self.max_fret_span and self.hand_position.min_fret <= 3:
            self.messages.append(ValidationMessage(
                code=ValidationResult.EXCESSIVE_STRETCH,
                severity='warning',
                message=f"Wide span ({self.hand_position.fret_span} frets) in lower positions may be difficult for beginners",
                rule_name=rule_name
            ))
        # Beginner vs advanced player span limits
        
        pass  # Placeholder
    
    def _rule_finger_stretch_check(self) -> None:
        """Check for excessive stretches between adjacent fingers."""
        rule_name = 'finger_stretch_check'
        
        # Calculate distances between consecutive fingers
        finger_positions_by_number = {}
        for pos in self.finger_positions:
            if pos.finger.isdigit():
                finger_positions_by_number[int(pos.finger)] = pos
        
        # Check stretch between consecutive fingers
        for finger_num in range(1, 4):  # Check fingers 1-2, 2-3, 3-4
            if finger_num in finger_positions_by_number and finger_num + 1 in finger_positions_by_number:
                pos1 = finger_positions_by_number[finger_num]
                pos2 = finger_positions_by_number[finger_num + 1]
                
                fret_distance = abs(pos2.fret - pos1.fret)
                string_distance = abs(pos2.string - pos1.string)
                
                # Calculate difficulty based on fret and string distances
                stretch_difficulty = fret_distance + (string_distance * 0.5)
                
                if stretch_difficulty > 4:
                    self.messages.append(ValidationMessage(
                        code=ValidationResult.EXCESSIVE_STRETCH,
                        severity='error',
                        message=f"Excessive stretch between finger {finger_num} (string {pos1.string}, fret {pos1.fret}) and finger {finger_num + 1} (string {pos2.string}, fret {pos2.fret})",
                        rule_name=rule_name,
                        affected_strings=[pos1.string, pos2.string]
                    ))
                elif stretch_difficulty > 3:
                    self.messages.append(ValidationMessage(
                        code=ValidationResult.EXCESSIVE_STRETCH,
                        severity='warning',
                        message=f"Challenging stretch between finger {finger_num} and finger {finger_num + 1}",
                        rule_name=rule_name,
                        affected_strings=[pos1.string, pos2.string]
                    ))
        
        # Consider string-to-string stretch (diagonal stretches)
        # Diagonal stretches across strings are more difficult
        for pos1 in self.finger_positions:
            for pos2 in self.finger_positions:
                if pos1.finger != pos2.finger and pos1.finger.isdigit() and pos2.finger.isdigit():
                    string_diff = abs(pos1.string - pos2.string)
                    fret_diff = abs(pos1.fret - pos2.fret)
                    
                    # Large diagonal stretches are problematic
                    if string_diff >= 3 and fret_diff >= 3:
                        self.messages.append(ValidationMessage(
                            code=ValidationResult.EXCESSIVE_STRETCH,
                            severity='warning',
                            message=f"Large diagonal stretch between finger {pos1.finger} and finger {pos2.finger}",
                            rule_name=rule_name,
                            affected_strings=[pos1.string, pos2.string]
                        ))
        
        # Account for fret position (higher frets are closer together)
        # Stretches are easier higher up the neck (after 7th fret)
        if self.hand_position and self.hand_position.min_fret >= 7:
            # Reduce severity of stretch warnings for higher positions
            for msg in self.messages:
                if msg.rule_name == rule_name and msg.severity == 'error' and self.hand_position.fret_span <= 5:
                    msg.severity = 'warning'
                    msg.message += " (easier in higher fret positions)"
    
    def _rule_finger_collision_check(self) -> None:
        """Check for finger collisions and interference."""
        rule_name = 'finger_collision_check'
        
        # Check for fingers trying to occupy same physical space
        # Adjacent strings with fingers on same fret might collide
        for i, pos1 in enumerate(self.finger_positions):
            for j, pos2 in enumerate(self.finger_positions):
                if i >= j:  # Avoid checking same pair twice
                    continue
                
                # Check if fingers are too close on adjacent strings
                string_diff = abs(pos1.string - pos2.string)
                fret_diff = abs(pos1.fret - pos2.fret)
                
                # Adjacent strings with same fret = potential collision
                if string_diff == 1 and fret_diff == 0 and pos1.finger != pos2.finger:
                    # Allow if it's the same finger (barre)
                    if pos1.finger != pos2.finger:
                        self.messages.append(ValidationMessage(
                            code=ValidationResult.FINGER_COLLISION,
                            severity='warning',
                            message=f"Potential finger collision: finger {pos1.finger} and {pos2.finger} both on fret {pos1.fret} on adjacent strings",
                            rule_name=rule_name,
                            affected_strings=[pos1.string, pos2.string]
                        ))
                
                # Check if finger placement blocks adjacent strings
                if string_diff == 1 and fret_diff == 1:
                    # Higher finger might interfere with lower string
                    higher_fret_finger = pos1 if pos1.fret > pos2.fret else pos2
                    lower_string = min(pos1.string, pos2.string)
                    
                    self.messages.append(ValidationMessage(
                        code=ValidationResult.FINGER_COLLISION,
                        severity='info',
                        message=f"Finger {higher_fret_finger.finger} might interfere with string {lower_string} - ensure clean fretting",
                        rule_name=rule_name,
                        affected_strings=[pos1.string, pos2.string]
                    ))
        
        # Check finger order anatomical correctness
        # This overlaps with basic_validation but adds more specific collision checks
        finger_by_fret = {}
        for pos in self.finger_positions:
            if pos.fret not in finger_by_fret:
                finger_by_fret[pos.fret] = []
            finger_by_fret[pos.fret].append(pos)
        
        # Check for muted string interference
        # Fingers might accidentally mute adjacent strings that should be open
        for pos in self.finger_positions:
            # Check if finger might mute adjacent strings
            adjacent_strings = [pos.string - 1, pos.string + 1]
            for adj_string in adjacent_strings:
                if 1 <= adj_string <= 6:  # Valid string range
                    # Check if this adjacent string should be open but might be muted
                    is_adjacent_specified = any(
                        fp.string == adj_string for fp in self.finger_positions
                    )
                    
                    if not is_adjacent_specified and pos.fret > 0:
                        self.messages.append(ValidationMessage(
                            code=ValidationResult.FINGER_COLLISION,
                            severity='info',
                            message=f"Finger {pos.finger} on string {pos.string} might accidentally mute string {adj_string} - ensure finger arch",
                            rule_name=rule_name,
                            affected_strings=[pos.string, adj_string]
                        ))
    
    def _rule_thumb_position_check(self) -> None:
        """Validate thumb position and usage based on configured reach."""
        rule_name = 'thumb_position_check'
        
        thumb_positions = [pos for pos in self.finger_positions if pos.finger == 'T']
        
        if self.thumb_reach_strings == 0:
            # Check if thumb is being used for fretting when not allowed
            if thumb_positions:
                self.messages.append(ValidationMessage(
                    code=ValidationResult.THUMB_POSITION_ERROR,
                    severity='error',
                    message="Thumb fretting is not allowed in current configuration",
                    rule_name=rule_name,
                    affected_strings=[pos.string for pos in thumb_positions]
                ))
                return
        
        for thumb_pos in thumb_positions:
            # Check if thumb is within reach based on thumb_reach_strings
            # String 6 = bass E (easiest), String 1 = high E (hardest)
            max_reachable_string = 6  # Start with bass string
            min_reachable_string = max(1, 7 - self.thumb_reach_strings)  # Calculate minimum string
            
            if thumb_pos.string < min_reachable_string:
                # Convert reach to description for user-friendly message
                reach_descriptions = {
                    0: "no thumb fretting",
                    1: "6th string only",
                    2: "6th and 5th strings", 
                    3: "6th, 5th, and 4th strings",
                    4: "6th through 3rd strings",
                    5: "6th through 2nd strings",
                    6: "all strings"
                }
                reach_desc = reach_descriptions.get(self.thumb_reach_strings, f"{self.thumb_reach_strings} strings from bass")
                
                self.messages.append(ValidationMessage(
                    code=ValidationResult.THUMB_POSITION_ERROR,
                    severity='error',
                    message=f"Thumb cannot reach string {thumb_pos.string} with current reach setting ({reach_desc})",
                    rule_name=rule_name,
                    affected_strings=[thumb_pos.string]
                ))
            elif thumb_pos.string == min_reachable_string and self.thumb_reach_strings < 6:
                # Warn about difficult thumb positions at the limit of reach
                self.messages.append(ValidationMessage(
                    code=ValidationResult.THUMB_POSITION_ERROR,
                    severity='warning',
                    message=f"Thumb on string {thumb_pos.string} is at maximum reach - may be difficult for some players",
                    rule_name=rule_name,
                    affected_strings=[thumb_pos.string]
                ))
            
            # Check thumb fret position relative to hand position
            if self.hand_position:
                # Thumb should be at or behind the main hand position
                if thumb_pos.fret > self.hand_position.max_fret:
                    self.messages.append(ValidationMessage(
                        code=ValidationResult.THUMB_POSITION_ERROR,
                        severity='warning',
                        message=f"Thumb on fret {thumb_pos.fret} is ahead of hand position (max fret {self.hand_position.max_fret})",
                        rule_name=rule_name,
                        affected_strings=[thumb_pos.string]
                    ))
                
                # Validate thumb + finger combinations
                # Check if thumb position interferes with finger positions
                for finger_pos in self.finger_positions:
                    if finger_pos.finger != 'T' and finger_pos.string >= 4:  # Lower strings
                        fret_diff = abs(thumb_pos.fret - finger_pos.fret)
                        string_diff = abs(thumb_pos.string - finger_pos.string)
                        
                        # Thumb and fingers on nearby strings and frets can be awkward
                        if string_diff <= 2 and fret_diff > 2:
                            self.messages.append(ValidationMessage(
                                code=ValidationResult.THUMB_POSITION_ERROR,
                                severity='warning',
                                message=f"Thumb position may interfere with finger {finger_pos.finger} - check hand comfort",
                                rule_name=rule_name,
                                affected_strings=[thumb_pos.string, finger_pos.string]
                            ))
    
    def _rule_barre_consistency_check(self) -> None:
        """Check barre chord consistency and feasibility."""
        rule_name = 'barre_consistency_check'
        
        # First, check for invalid pseudo-barre patterns
        finger_fret_map = {}
        for pos in self.finger_positions:
            key = (pos.finger, pos.fret)
            if key not in finger_fret_map:
                finger_fret_map[key] = []
            finger_fret_map[key].append(pos.string)
        
        # Look for fingers on multiple strings at the same fret
        for (finger, fret), strings in finger_fret_map.items():
            if len(strings) > 1 and finger != 'T':  # Thumb can't barre
                strings_sorted = sorted(strings)
                
                # Check for impossible barre patterns (gaps with open strings)
                for i in range(len(strings_sorted) - 1):
                    string_gap = strings_sorted[i + 1] - strings_sorted[i]
                    if string_gap > 1:  # There's a gap between strings
                        # Check what's in the gap
                        gap_strings = []
                        for gap_string in range(strings_sorted[i] + 1, strings_sorted[i + 1]):
                            # Check if this string is fretted by another finger
                            gap_fretted = any(pos.string == gap_string and pos.fret > 0 
                                            for pos in self.finger_positions)
                            if not gap_fretted:
                                gap_strings.append(gap_string)
                        
                        if gap_strings:
                            self.messages.append(ValidationMessage(
                                code=ValidationResult.INCONSISTENT_BARRE,
                                severity='error',
                                message=f"Invalid barre: finger {finger} cannot span strings {min(strings_sorted)}-{max(strings_sorted)} with open/muted strings {gap_strings} in between",
                                rule_name=rule_name,
                                affected_strings=strings + gap_strings
                            ))
        
        # Continue with existing barre validation if we have a valid barre
        if not self.hand_position or not self.hand_position.barre_fret:
            return
        
        barre_strings = self.hand_position.barre_strings or []
        barre_fret = self.hand_position.barre_fret
        
        # Check barre spans reasonable number of strings
        if len(barre_strings) < 2:
            self.messages.append(ValidationMessage(
                code=ValidationResult.INCONSISTENT_BARRE,
                severity='warning',
                message=f"Barre chord detected but only spans {len(barre_strings)} string(s) - consider if barre is necessary",
                rule_name=rule_name,
                affected_strings=barre_strings
            ))
        elif len(barre_strings) > 6:
            self.messages.append(ValidationMessage(
                code=ValidationResult.INCONSISTENT_BARRE,
                severity='error',
                message="Barre cannot span more than 6 strings",
                rule_name=rule_name,
                affected_strings=barre_strings
            ))
        
        # Check if barre strings are contiguous (mostly)
        if len(barre_strings) > 2:
            barre_strings_sorted = sorted(barre_strings)
            for i in range(len(barre_strings_sorted) - 1):
                if barre_strings_sorted[i + 1] - barre_strings_sorted[i] > 2:
                    self.messages.append(ValidationMessage(
                        code=ValidationResult.INCONSISTENT_BARRE,
                        severity='warning',
                        message="Barre chord has large gaps between strings - ensure proper finger placement",
                        rule_name=rule_name,
                        affected_strings=barre_strings
                    ))
                    break
        
        # Ensure other fingers don't interfere with barre
        barre_finger = None
        for pos in self.finger_positions:
            if pos.fret == barre_fret and pos.string in barre_strings:
                barre_finger = pos.finger
                break
        
        if barre_finger:
            for pos in self.finger_positions:
                if pos.finger != barre_finger and pos.fret < barre_fret:
                    string_diff = min(abs(pos.string - s) for s in barre_strings)
                    if string_diff <= 1:  # Adjacent to barre
                        self.messages.append(ValidationMessage(
                            code=ValidationResult.INCONSISTENT_BARRE,
                            severity='warning',
                            message=f"Finger {pos.finger} behind barre might interfere - ensure proper hand position",
                            rule_name=rule_name,
                            affected_strings=[pos.string] + barre_strings
                        ))
        
        # Check barre finger strength requirements
        barre_span = max(barre_strings) - min(barre_strings) + 1
        if barre_span >= 5:
            severity = 'error' if barre_fret <= 2 else 'warning'
            position_desc = "low position" if barre_fret <= 2 else "higher position"
            self.messages.append(ValidationMessage(
                code=ValidationResult.INCONSISTENT_BARRE,
                severity=severity,
                message=f"Full barre in {position_desc} (fret {barre_fret}) requires significant finger strength",
                rule_name=rule_name,
                affected_strings=barre_strings
            ))
    
    def _rule_ergonomic_assessment(self) -> None:
        """Assess overall ergonomics and playability."""
        rule_name = 'ergonomic_assessment'
        
        # Rate chord difficulty based on multiple factors
        difficulty_score = 0
        difficulty_factors = []
        
        if self.hand_position:
            # Fret span contributes to difficulty
            span_factor = self.hand_position.fret_span / self.max_fret_span
            difficulty_score += span_factor * 2
            if span_factor > 0.8:
                difficulty_factors.append(f"wide fret span ({self.hand_position.fret_span})")
            
            # Low fret positions are harder for barres
            if self.hand_position.barre_fret and self.hand_position.barre_fret <= 3:
                difficulty_score += 1.5
                difficulty_factors.append("low position barre")
            
            # High fret positions (above 12th fret) can be cramped
            if self.hand_position.min_fret > 12:
                difficulty_score += 0.5
                difficulty_factors.append("very high position")
        
        # Count finger usage complexity
        finger_count = len(set(pos.finger for pos in self.finger_positions if pos.finger != 'T'))
        if finger_count >= 4:
            difficulty_score += 1.0
            difficulty_factors.append("uses all four fingers")
        
        # Check for thumb usage
        if any(pos.finger == 'T' for pos in self.finger_positions):
            difficulty_score += 1.0
            difficulty_factors.append("thumb fretting required")
        
        # Check for common problematic patterns
        problematic_patterns = []
        
        # Pattern: Wide stretch + barre combination
        if (self.hand_position and 
            self.hand_position.fret_span > 3 and 
            self.hand_position.barre_fret):
            problematic_patterns.append("wide stretch with barre")
            difficulty_score += 1.0
        
        # Pattern: Multiple fingers on same fret (crowding)
        fret_finger_count = {}
        for pos in self.finger_positions:
            if pos.fret > 0:
                fret_finger_count[pos.fret] = fret_finger_count.get(pos.fret, 0) + 1
        
        crowded_frets = [fret for fret, count in fret_finger_count.items() if count > 2]
        if crowded_frets:
            problematic_patterns.append(f"finger crowding on fret(s) {crowded_frets}")
            difficulty_score += 0.5 * len(crowded_frets)
        
        # Pattern: Finger 4 (pinky) on lower strings
        pinky_positions = [pos for pos in self.finger_positions if pos.finger == '4']
        for pos in pinky_positions:
            if pos.string >= 5:  # 5th or 6th string
                problematic_patterns.append("pinky on bass strings")
                difficulty_score += 0.5
                break
        
        # Provide overall difficulty assessment
        if difficulty_score <= 1.0:
            difficulty_level = "Easy"
            severity = 'info'
        elif difficulty_score <= 2.5:
            difficulty_level = "Moderate"
            severity = 'info'
        elif difficulty_score <= 4.0:
            difficulty_level = "Challenging"
            severity = 'warning'
        else:
            difficulty_level = "Very Difficult"
            severity = 'warning'
        
        message = f"Chord difficulty: {difficulty_level} (score: {difficulty_score:.1f})"
        if difficulty_factors:
            message += f" - Factors: {', '.join(difficulty_factors)}"
        
        self.messages.append(ValidationMessage(
            code=ValidationResult.VALID_WITH_WARNINGS if severity == 'warning' else ValidationResult.VALID,
            severity=severity,
            message=message,
            rule_name=rule_name
        ))
        
        if problematic_patterns:
            self.messages.append(ValidationMessage(
                code=ValidationResult.VALID_WITH_WARNINGS,
                severity='warning',
                message=f"Problematic patterns detected: {', '.join(problematic_patterns)}",
                rule_name=rule_name
            ))
        
        # Suggest alternative fingerings if available (basic suggestions)
        if difficulty_score > 3.0:
            suggestions = []
            
            if self.hand_position and self.hand_position.fret_span > 4:
                suggestions.append("try capo to reduce fret span")
            
            if self.hand_position and self.hand_position.barre_fret and self.hand_position.barre_fret <= 2:
                suggestions.append("consider partial barre instead of full barre")
            
            if finger_count >= 4:
                suggestions.append("look for simplified chord voicing")
            
            if suggestions:
                self.messages.append(ValidationMessage(
                    code=ValidationResult.VALID_WITH_WARNINGS,
                    severity='info',
                    message=f"Suggestions: {', '.join(suggestions)}",
                    rule_name=rule_name
                ))
        
        # Consider chord context (key, progression) - basic implementation
        # This would require additional context not available in current interface
        # For now, just add a note about context
        if difficulty_score > 2.5:
            self.messages.append(ValidationMessage(
                code=ValidationResult.VALID,
                severity='info',
                message="Consider chord context - difficult chords may be acceptable in slow songs or specific musical styles",
                rule_name=rule_name
            ))
    
    def _determine_overall_result(self) -> None:
        """Determine the overall validation result based on all messages."""
        has_errors = any(msg.severity == 'error' for msg in self.messages)
        has_warnings = any(msg.severity == 'warning' for msg in self.messages)
        
        if has_errors:
            # Find the most severe error code
            error_codes = [msg.code for msg in self.messages if msg.severity == 'error']
            # Use the first error code, or implement priority logic
            self.overall_result = error_codes[0]
        elif has_warnings:
            self.overall_result = ValidationResult.VALID_WITH_WARNINGS
        else:
            self.overall_result = ValidationResult.VALID
    
    def _build_result(self, result_code: ValidationResult) -> Dict[str, Any]:
        """Build the final validation result dictionary."""
        return {
            'status_code': result_code.value,
            'status_name': result_code.name,
            'is_valid': result_code.value < 400,
            'has_warnings': any(msg.severity == 'warning' for msg in self.messages),
            'messages': [
                {
                    'code': msg.code.value,
                    'severity': msg.severity,
                    'message': msg.message,
                    'rule': msg.rule_name,
                    'affected_strings': msg.affected_strings
                }
                for msg in self.messages
            ],
            'finger_positions': [
                {
                    'finger': pos.finger,
                    'string': pos.string,
                    'fret': pos.fret
                }
                for pos in self.finger_positions
            ],
            'hand_position': {
                'min_fret': self.hand_position.min_fret if self.hand_position else 0,
                'max_fret': self.hand_position.max_fret if self.hand_position else 0,
                'fret_span': self.hand_position.fret_span if self.hand_position else 0,
                'thumb_fret': self.hand_position.thumb_fret if self.hand_position else None,
                'barre_fret': self.hand_position.barre_fret if self.hand_position else None,
                'barre_strings': self.hand_position.barre_strings if self.hand_position else []
            }
        }


# Example usage and demonstration
def demonstrate_validator():
    """Demonstrate the chord fingering validator with various thumb reach examples."""
    
    print("=== Guitar Chord Fingering Validator Demo ===")
    print("Demonstrating configurable thumb reach settings\n")
    
    # Test chord with thumb on 5th string
    thumb_chord = [
        ('T', 2),  # 6th string, thumb on 2nd fret
        ('T', 2),  # 5th string, thumb on 2nd fret (testing reach)
        ('2', 3),  # 4th string, 3rd fret, 2nd finger
        ('3', 4),  # 3rd string, 4th fret, 3rd finger
        ('1', 2),  # 2nd string, 2nd fret, 1st finger
        ('O', 0)   # 1st string open
    ]
    
    # Test with different thumb reach settings
    reach_settings = [
        (1, "Standard reach (6th string only)"),
        (2, "Extended reach (6th and 5th strings)"),
        (3, "Large hands (6th, 5th, and 4th strings)"),
        (0, "No thumb fretting allowed")
    ]
    
    for reach_strings, description in reach_settings:
        print(f"Testing with {description}:")
        print("-" * 50)
        
        validator = ChordFingeringValidator(thumb_reach_strings=reach_strings)
        result = validator.validate_chord(thumb_chord)
        
        print(f"Status: {result['status_code']} - {result['status_name']}")
        print(f"Valid: {result['is_valid']}")
        
        if result['messages']:
            for msg in result['messages']:
                if msg['severity'] == 'error':
                    print(f"  ERROR: {msg['message']}")
                elif msg['severity'] == 'warning':
                    print(f"  WARNING: {msg['message']}")
                else:
                    print(f"  INFO: {msg['message']}")
        print()
    
    # Test Case: Valid C Major chord for comparison
    print("Reference: Standard C Major Chord (no thumb)")
    print("-" * 50)
    c_major = [
        ('X', 0),  # 6th string muted
        ('3', 3),  # 5th string, 3rd fret, 3rd finger
        ('2', 2),  # 4th string, 2nd fret, 2nd finger
        ('O', 0),  # 3rd string open
        ('1', 1),  # 2nd string, 1st fret, 1st finger
        ('O', 0)   # 1st string open
    ]
    
    standard_validator = ChordFingeringValidator(thumb_reach_strings=1)
    result = standard_validator.validate_chord(c_major)
    print(f"Status: {result['status_code']} - {result['status_name']}")
    print(f"Valid: {result['is_valid']}")
    print()


if __name__ == "__main__":
    demonstrate_validator()