"""
Unified Scoring Schema - Ensures ALL agents score consistently

This module defines the SINGLE SOURCE OF TRUTH for how all agents calculate scores.
All agents MUST use these functions to ensure consistency.

Problems Fixed:
1. Requirement agent scores differently than test agent
2. LLM doesn't know what score range means
3. Aggregation gets confused by inconsistent scoring

Solution: ONE scoring system for all agents
"""

from typing import Dict, List, Any


class ScoringSchema:
    """
    Unified scoring schema for all evaluation agents.
    
    Score Range: 0-20 points (scaled to 0-100 in aggregation)
    
    Scoring Rules:
    1. All scores normalized to 0-20 scale
    2. Proportional scoring: (achieved / total) * 20
    3. Binary scoring only for syntax (0 or 20)
    4. Minimum score: 0 (fail)
    5. Maximum score: 20 (perfect)
    """
    
    # ============================================================================
    # SYNTAX SCORING (Binary - either works or doesn't)
    # ============================================================================
    
    @staticmethod
    def syntax_score(success: bool, is_snippet: bool = False) -> int:
        """
        Calculate syntax score.
        
        Args:
            success: True if code parses and runs
            is_snippet: True if code is snippet (missing boilerplate)
            
        Returns:
            int: 0-20 score
            
        Logic:
        - Valid code: 20 points
        - Valid snippet: 15 points (shows correct logic)
        - Syntax error: 0 points
        """
        if success:
            return 20 if not is_snippet else 15
        return 0
    
    # ============================================================================
    # PROPORTIONAL SCORING (Most common - based on fulfillment rate)
    # ============================================================================
    
    @staticmethod
    def proportional_score(achieved: int, total: int, min_score: int = 0) -> int:
        """
        Calculate proportional score based on achievement rate.
        
        Formula: (achieved / total) * 20, clamped to [min_score, 20]
        
        Args:
            achieved: Number of items achieved (met requirements, passed tests, etc.)
            total: Total number of items to achieve
            min_score: Minimum score if total > 0 (default 0)
            
        Returns:
            int: 0-20 score
            
        Examples:
        - 3/3 achieved: (3/3) * 20 = 20 points (PERFECT)
        - 2/3 achieved: (2/3) * 20 = 13.33 → 13 points (GOOD)
        - 1/3 achieved: (1/3) * 20 = 6.67 → 6 points (FAIR)
        - 0/3 achieved: (0/3) * 20 = 0 points (FAIL)
        """
        if total == 0:
            # No items to check = perfect score (nothing to fail)
            return 20
        
        if achieved <= 0:
            return min_score
        
        score = int((achieved / total) * 20)
        return max(min(score, 20), min_score)
    
    # ============================================================================
    # COMPONENT SCORING (For agents with multiple sub-criteria)
    # ============================================================================
    
    @staticmethod
    def component_score(components: Dict[str, int], weights: Dict[str, float] = None) -> int:
        """
        Calculate score from weighted components.
        
        Formula: SUM(component_score * weight) for all components
        
        Args:
            components: Dict of {"component_name": score_0_to_20}
            weights: Dict of {"component_name": weight}, sums to 1.0
                    If None, equal weight for all components
                    
        Returns:
            int: 0-20 score
            
        Example (Structure agent with 6 components):
        - Functions (weight 0.2): 16 points
        - Classes (weight 0.15): 12 points
        - Naming (weight 0.2): 18 points
        - Imports (weight 0.1): 20 points
        - Docstrings (weight 0.2): 10 points
        - Complexity (weight 0.15): 14 points
        - Total: 16*0.2 + 12*0.15 + 18*0.2 + 20*0.1 + 10*0.2 + 14*0.15 = 14.8 → 14 points
        """
        if not components:
            return 0
        
        # If no weights provided, use equal weights
        if weights is None:
            weights = {name: 1.0 / len(components) for name in components}
        
        # Validate weights sum to ~1.0
        total_weight = sum(weights.values())
        if abs(total_weight - 1.0) > 0.01:
            raise ValueError(f"Weights must sum to 1.0, got {total_weight}")
        
        # Calculate weighted score
        weighted_sum = sum(components.get(name, 0) * weights[name] 
                          for name in weights.keys())
        
        score = int(weighted_sum)
        return max(min(score, 20), 0)
    
    # ============================================================================
    # SCORE INTERPRETATION (What does each score mean?)
    # ============================================================================
    
    @staticmethod
    def score_to_grade(score: int) -> str:
        """
        Convert 0-20 score to letter grade.
        
        Args:
            score: Score from 0-20
            
        Returns:
            str: Letter grade (A+, A, B, C, F)
        """
        if score >= 19:
            return "A+"
        elif score >= 17:
            return "A"
        elif score >= 15:
            return "B"
        elif score >= 10:
            return "C"
        else:
            return "F"
    
    @staticmethod
    def score_to_description(score: int) -> str:
        """
        Convert 0-20 score to human-readable description.
        
        Args:
            score: Score from 0-20
            
        Returns:
            str: Description of score quality
        """
        if score >= 18:
            return "Excellent - Professional quality"
        elif score >= 15:
            return "Good - Meets all requirements"
        elif score >= 12:
            return "Fair - Mostly correct"
        elif score >= 10:
            return "Acceptable - Has issues but functional"
        elif score >= 5:
            return "Poor - Multiple issues"
        else:
            return "Fail - Does not work"


# ============================================================================
# SCORING CONSISTENCY CHECKER
# ============================================================================

class ScoringConsistencyChecker:
    """
    Validates that all agents score consistently using the unified schema.
    """
    
    @staticmethod
    def validate_agent_result(agent_name: str, result: Dict[str, Any]) -> List[str]:
        """
        Validate that an agent's result uses consistent scoring.
        
        Args:
            agent_name: Name of the agent (syntax, requirement, test, structure, etc.)
            result: Agent's result dict
            
        Returns:
            List[str]: List of validation errors (empty if valid)
        """
        errors = []
        
        # Check score exists and is in range
        if 'score' not in result:
            errors.append(f"{agent_name}: Missing 'score' field")
        elif not isinstance(result['score'], (int, float)):
            errors.append(f"{agent_name}: Score must be number, got {type(result['score'])}")
        elif result['score'] < 0 or result['score'] > 20:
            errors.append(f"{agent_name}: Score out of range [0-20], got {result['score']}")
        
        # Agent-specific validations
        if agent_name == 'requirement':
            if 'fulfilled_count' not in result or 'total_count' not in result:
                errors.append(f"{agent_name}: Missing fulfilled_count or total_count")
            expected_score = ScoringSchema.proportional_score(
                result.get('fulfilled_count', 0),
                result.get('total_count', 1)
            )
            if result.get('score') != expected_score:
                errors.append(
                    f"{agent_name}: Score mismatch. Got {result['score']}, "
                    f"expected {expected_score} from ({result.get('fulfilled_count')}/{result.get('total_count')})"
                )
        
        elif agent_name == 'test':
            if 'passed_count' not in result or 'total_tests' not in result:
                errors.append(f"{agent_name}: Missing passed_count or total_tests")
            # For test agent, score should match passed_count / total_tests
            expected_score = ScoringSchema.proportional_score(
                result.get('passed_count', 0),
                result.get('total_tests', 1)
            )
            if result.get('score') != expected_score:
                errors.append(
                    f"{agent_name}: Score mismatch. Got {result['score']}, "
                    f"expected {expected_score} from ({result.get('passed_count')}/{result.get('total_tests')})"
                )
        
        elif agent_name == 'syntax':
            if result.get('score') not in [0, 15, 20]:
                errors.append(
                    f"{agent_name}: Syntax score must be 0, 15, or 20. Got {result['score']}"
                )
        
        return errors
    
    @staticmethod
    def check_all_agents(results: Dict[str, Dict]) -> Dict[str, List[str]]:
        """
        Check consistency across all agent results.
        
        Args:
            results: Dict of all agent results {agent_name: result_dict}
            
        Returns:
            Dict: {agent_name: [list_of_errors]}
        """
        consistency_report = {}
        
        for agent_name, result in results.items():
            errors = ScoringConsistencyChecker.validate_agent_result(agent_name, result)
            if errors:
                consistency_report[agent_name] = errors
        
        return consistency_report


# ============================================================================
# EXAMPLES & TESTS
# ============================================================================

if __name__ == "__main__":
    print("=" * 70)
    print("UNIFIED SCORING SCHEMA - Examples")
    print("=" * 70)
    
    # Example 1: Proportional scoring
    print("\n1. PROPORTIONAL SCORING (Requirements & Tests)")
    print("-" * 70)
    print(f"3/3 requirements met: {ScoringSchema.proportional_score(3, 3)} pts")
    print(f"2/3 requirements met: {ScoringSchema.proportional_score(2, 3)} pts")
    print(f"1/3 requirements met: {ScoringSchema.proportional_score(1, 3)} pts")
    print(f"0/3 requirements met: {ScoringSchema.proportional_score(0, 3)} pts")
    
    # Example 2: Component scoring
    print("\n2. COMPONENT SCORING (Structure with 6 sub-criteria)")
    print("-" * 70)
    components = {
        "functions": 16,
        "classes": 12,
        "naming": 18,
        "imports": 20,
        "docstrings": 10,
        "complexity": 14
    }
    weights = {
        "functions": 0.2,
        "classes": 0.15,
        "naming": 0.2,
        "imports": 0.1,
        "docstrings": 0.2,
        "complexity": 0.15
    }
    final = ScoringSchema.component_score(components, weights)
    print(f"Components: {components}")
    print(f"Weights: {weights}")
    print(f"Final score: {final} pts")
    
    # Example 3: Score interpretation
    print("\n3. SCORE INTERPRETATION")
    print("-" * 70)
    for score in [20, 18, 15, 12, 8, 2]:
        grade = ScoringSchema.score_to_grade(score)
        desc = ScoringSchema.score_to_description(score)
        print(f"Score {score:2d}: Grade {grade} - {desc}")
    
    print("\n" + "=" * 70)
