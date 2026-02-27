"""
Coding Coach - Your personal coding improvement assistant.

Uses insights from the learner to provide:
- Personalized improvement suggestions
- Progress tracking
- Skill development roadmaps
- Encouragement and recognition
"""

from datetime import datetime, timedelta
from typing import Optional
from dataclasses import dataclass

from .learner import CodingLearner, CodingInsight, CodingPattern


@dataclass
class ImprovementGoal:
    """A specific improvement goal."""
    goal_id: str
    title: str
    description: str
    target_pattern: str
    current_status: str  # 'not_started', 'in_progress', 'achieved'
    progress_percent: int
    tips: list
    resources: list


@dataclass
class ProgressReport:
    """A progress report summary."""
    period: str
    strengths_count: int
    improvements_made: int
    areas_to_work_on: int
    coding_streak: int
    highlight: str
    next_focus: str


class CodingCoach:
    """
    Personal coding coach that provides guidance based on learned patterns.

    Think of it as a friendly mentor who:
    - Knows your coding habits
    - Recognizes your strengths
    - Gently points out areas for improvement
    - Celebrates your progress
    """

    def __init__(self, learner: Optional[CodingLearner] = None):
        self.learner = learner or CodingLearner()

        # Improvement tips database
        self.improvement_tips = {
            'bare_except': [
                "Use specific exception types to handle expected errors",
                "Log unexpected exceptions with full traceback",
                "Consider using 'except Exception as e:' to catch most exceptions while allowing KeyboardInterrupt",
            ],
            'mutable_default_args': [
                "Use None as default: def func(items=None):",
                "Initialize inside the function: items = items if items is not None else []",
                "This is a common Python gotcha - you're not alone!",
            ],
            'long_functions': [
                "Apply the Single Responsibility Principle - one function, one job",
                "Extract logical blocks into helper functions",
                "Use descriptive function names that explain what each piece does",
                "Aim for functions under 20 lines when possible",
            ],
            'deep_nesting': [
                "Use early returns to flatten nested conditions",
                "Extract nested logic into separate functions",
                "Consider using guard clauses at the start of functions",
            ],
            'minimal_docs': [
                "Start with a one-line description of what the function does",
                "Add parameter descriptions for non-obvious arguments",
                "Document return values and any exceptions raised",
                "Future you will thank present you!",
            ],
            'single_letter_vars': [
                "Use descriptive names: 'user_count' instead of 'n'",
                "Loop variables like 'i' are okay for short loops",
                "If you're using 'x', ask yourself: what IS x?",
            ],
            'long_lines': [
                "Break after operators: result = (long_expression +",
                "Use intermediate variables for complex expressions",
                "Consider if the line is doing too much",
            ],
        }

        # Recognition messages
        self.recognition_messages = {
            'modern_f_strings': "Great job using f-strings! They're readable and efficient.",
            'well_documented': "Excellent documentation habits! Your future self will thank you.",
            'proper_none_check': "Nice use of 'is None' - shows you understand Python's identity vs equality.",
            'type_hints': "Type hints are a sign of mature Python code. Keep it up!",
            'descriptive_vars': "Your descriptive variable names make your code a joy to read.",
            'snake_case_functions': "Following PEP 8 naming conventions - very Pythonic!",
        }

    def get_daily_tip(self) -> dict:
        """Get a personalized daily coding tip based on patterns."""
        # Get areas needing improvement
        patterns = self.learner.get_patterns('error_prone')

        if patterns:
            # Focus on most frequent issue
            pattern = patterns[0]
            tips = self.improvement_tips.get(pattern.name, ["Keep practicing!"])

            return {
                'type': 'improvement',
                'title': f"Daily Focus: {pattern.name.replace('_', ' ').title()}",
                'tip': tips[0] if tips else "Keep up the good work!",
                'pattern': pattern.name,
                'reason': f"Detected {pattern.frequency} times in your code",
            }

        # No issues - give recognition
        strengths = self.learner.get_patterns('style')
        if strengths:
            strength = strengths[0]
            message = self.recognition_messages.get(strength.name, "Keep up the great work!")

            return {
                'type': 'recognition',
                'title': "You're Doing Great!",
                'tip': message,
                'pattern': strength.name,
                'reason': "Consistently good practice detected",
            }

        return {
            'type': 'general',
            'title': "Keep Coding!",
            'tip': "The more you code, the more I learn about you. Keep at it!",
            'pattern': None,
            'reason': "Building your coding profile",
        }

    def get_improvement_goals(self) -> list:
        """Generate personalized improvement goals."""
        goals = []

        # Get weaknesses
        weak_patterns = self.learner.get_patterns('error_prone')

        for i, pattern in enumerate(weak_patterns[:3]):  # Top 3 goals
            tips = self.improvement_tips.get(pattern.name, [])

            goals.append(ImprovementGoal(
                goal_id=f"goal_{pattern.name}",
                title=f"Address: {pattern.name.replace('_', ' ').title()}",
                description=pattern.description,
                target_pattern=pattern.name,
                current_status='in_progress' if pattern.frequency < 5 else 'not_started',
                progress_percent=max(0, 100 - (pattern.frequency * 10)),
                tips=tips,
                resources=self._get_resources(pattern.name),
            ))

        # Add documentation goal if needed
        doc_pattern = next(
            (p for p in self.learner.get_patterns('structure') if p.name == 'minimal_docs'),
            None
        )
        if doc_pattern:
            goals.append(ImprovementGoal(
                goal_id="goal_documentation",
                title="Improve Documentation",
                description="Add docstrings to your functions",
                target_pattern='minimal_docs',
                current_status='in_progress',
                progress_percent=30,
                tips=self.improvement_tips.get('minimal_docs', []),
                resources=[
                    "PEP 257 - Docstring Conventions",
                    "Google Python Style Guide - Docstrings",
                ],
            ))

        return goals

    def _get_resources(self, pattern_name: str) -> list:
        """Get learning resources for a pattern."""
        resources = {
            'bare_except': [
                "Python Exception Handling Best Practices",
                "The Hitchhiker's Guide to Python - Error Handling",
            ],
            'mutable_default_args': [
                "Python Gotchas - Mutable Default Arguments",
                "Effective Python Item 24",
            ],
            'long_functions': [
                "Clean Code by Robert C. Martin",
                "Refactoring by Martin Fowler",
            ],
            'deep_nesting': [
                "Flattening Arrow Code",
                "Guard Clauses Pattern",
            ],
        }
        return resources.get(pattern_name, ["Python Documentation"])

    def get_progress_report(self) -> ProgressReport:
        """Generate a progress report."""
        profile = self.learner.get_coding_profile()

        # Count strengths and weaknesses
        strengths_count = len(profile.get('strengths', []))
        weaknesses_count = len(profile.get('areas_to_improve', []))

        # Generate highlight
        if strengths_count > weaknesses_count:
            highlight = "Your code quality is strong! More good patterns than issues."
        elif strengths_count > 0:
            highlight = f"You're building good habits with {strengths_count} positive patterns detected."
        else:
            highlight = "Keep coding! I'm still learning your style."

        # Generate next focus
        areas = profile.get('areas_to_improve', [])
        if areas:
            next_focus = f"Focus on: {areas[0].get('name', 'writing clean code').replace('_', ' ')}"
        else:
            next_focus = "Keep up the great work!"

        return ProgressReport(
            period="Recent Analysis",
            strengths_count=strengths_count,
            improvements_made=profile.get('total_insights', 0),
            areas_to_work_on=weaknesses_count,
            coding_streak=self._calculate_streak(),
            highlight=highlight,
            next_focus=next_focus,
        )

    def _calculate_streak(self) -> int:
        """Calculate coding streak (consecutive days with commits)."""
        # Simplified - just return days since last analysis
        progress = self.learner.get_progress('commits_per_period', 30)
        return len([p for p in progress if p[0] > 0])

    def get_encouragement(self) -> str:
        """Get an encouraging message based on current progress."""
        profile = self.learner.get_coding_profile()

        strengths = profile.get('strengths', [])
        weaknesses = profile.get('areas_to_improve', [])

        messages = [
            "Every line of code you write is a step forward.",
            "Bugs are just features waiting to be understood.",
            "The best code is the code you'll understand tomorrow.",
        ]

        if strengths:
            return f"You're already showing strong {strengths[0].get('name', 'coding')} skills. Keep building on that foundation!"

        if len(weaknesses) == 1:
            return f"You have just one main area to focus on: {weaknesses[0].get('name', 'this pattern')}. Tackle it and you'll level up!"

        return messages[hash(datetime.now().date().isoformat()) % len(messages)]

    def get_coding_style_summary(self) -> dict:
        """Get a summary of the developer's coding style."""
        preferences = self.learner.get_preferences()
        patterns = self.learner.get_patterns()

        # Determine primary style
        paradigm = preferences.get('structure', {}).get('paradigm', {})
        naming = preferences.get('naming', {}).get('function_style', {})

        style_traits = []

        if paradigm.get('value') == 'functional_style':
            style_traits.append("Functional programming enthusiast")
        elif paradigm.get('value') == 'class_heavy':
            style_traits.append("Object-oriented design preference")

        if naming.get('value') == 'snake_case_functions':
            style_traits.append("Follows PEP 8 conventions")

        # Check for documentation habits
        doc_patterns = [p for p in patterns if 'doc' in p.name.lower()]
        if any(p.name == 'well_documented' for p in doc_patterns):
            style_traits.append("Documentation-focused")

        # Check for modern Python usage
        modern = [p for p in patterns if 'modern' in p.name or 'f_string' in p.name]
        if modern:
            style_traits.append("Uses modern Python features")

        # Type hints
        type_patterns = [p for p in patterns if 'type_hint' in p.name]
        if type_patterns:
            style_traits.append("Type-safety conscious")

        return {
            'style_traits': style_traits or ["Still learning your style..."],
            'primary_paradigm': paradigm.get('value', 'mixed').replace('_', ' '),
            'naming_convention': naming.get('value', 'varies').replace('_', ' '),
            'total_patterns_detected': len(patterns),
        }

    def acknowledge_insight(self, insight_id: int):
        """Mark an insight as acknowledged."""
        self.learner.conn.execute(
            "UPDATE insights SET acknowledged = 1 WHERE id = ?",
            (insight_id,)
        )
        self.learner.conn.commit()

    def get_skill_radar(self) -> dict:
        """
        Generate skill radar data for visualization.

        Returns scores for different coding aspects:
        - Code Quality
        - Documentation
        - Error Handling
        - Modern Practices
        - Maintainability
        """
        patterns = self.learner.get_patterns()

        # Calculate scores (0-100)
        scores = {
            'code_quality': 50,
            'documentation': 50,
            'error_handling': 50,
            'modern_practices': 50,
            'maintainability': 50,
        }

        for pattern in patterns:
            name = pattern.name.lower()
            confidence = pattern.confidence

            # Code Quality
            if 'descriptive' in name or 'snake_case' in name:
                scores['code_quality'] += 10 * confidence
            if 'single_letter' in name or 'long_function' in name:
                scores['code_quality'] -= 10 * confidence

            # Documentation
            if 'well_documented' in name or 'docstring' in name:
                scores['documentation'] += 20 * confidence
            if 'minimal_doc' in name:
                scores['documentation'] -= 20 * confidence

            # Error Handling
            if 'proper_none' in name:
                scores['error_handling'] += 10 * confidence
            if 'bare_except' in name or 'mutable_default' in name:
                scores['error_handling'] -= 15 * confidence

            # Modern Practices
            if 'f_string' in name or 'type_hint' in name or 'modern' in name:
                scores['modern_practices'] += 15 * confidence
            if 'format_method' in name or 'percent_format' in name:
                scores['modern_practices'] -= 10 * confidence

            # Maintainability
            if 'deep_nest' in name or 'long_function' in name or 'long_line' in name:
                scores['maintainability'] -= 10 * confidence
            if 'descriptive' in name or 'well_documented' in name:
                scores['maintainability'] += 10 * confidence

        # Normalize scores to 0-100
        for key in scores:
            scores[key] = max(0, min(100, int(scores[key])))

        return scores

    def close(self):
        """Close the learner connection."""
        self.learner.close()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
