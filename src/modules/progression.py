import json
import logging
import math
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple, Set
from dataclasses import dataclass, asdict
from enum import Enum
from pathlib import Path


class BadgeType(Enum):
    """Badge types for achievements."""
    BRONZE = "bronze"
    SILVER = "silver"
    GOLD = "gold"


class AchievementCategory(Enum):
    """Categories of achievements."""
    PROGRESSION = "progression"
    SKILL = "skill"
    SPECIALTY = "specialty"
    SPEED = "speed"
    STREAK = "streak"
    ADVANCED = "advanced"
    EXPLORATION = "exploration"
    CONSISTENCY = "consistency"
    TIME_BASED = "time_based"
    ENDURANCE = "endurance"
    RESILIENCE = "resilience"


@dataclass
class Achievement:
    """Achievement definition."""
    id: str
    name: str
    description: str
    category: AchievementCategory
    xp_reward: int
    badge_type: BadgeType
    requirements: Dict[str, Any]
    icon: str


@dataclass
class UserAchievement:
    """User's earned achievement."""
    achievement_id: str
    earned_at: datetime
    xp_awarded: int


@dataclass
class SpecialtyProficiency:
    """Proficiency level in a diagnostic category."""
    category: str
    level: int  # 1-10
    cases_completed: int
    accuracy: float
    xp_earned: int
    last_practiced: datetime


@dataclass
class StreakData:
    """Streak tracking data."""
    current_streak: int
    longest_streak: int
    streak_start_date: Optional[datetime]
    last_correct_date: Optional[datetime]
    streak_multiplier: float


@dataclass
class PerformanceMetrics:
    """Detailed performance metrics."""
    total_cases: int
    correct_diagnoses: int
    overall_accuracy: float
    average_time_per_case: float
    category_performance: Dict[str, Dict[str, Any]]
    difficulty_performance: Dict[str, Dict[str, Any]]
    recent_performance: List[Dict[str, Any]]
    improvement_trend: float


@dataclass
class UnlockStatus:
    """Unlock status for cases and features."""
    unlocked_difficulties: Set[str]
    unlocked_categories: Set[str]
    unlocked_special_features: Set[str]
    level_based_unlocks: Dict[str, int]
    achievement_based_unlocks: Dict[str, str]


class UserProgress:
    """
    Comprehensive user progression tracking system with gamification elements.
    """
    
    def __init__(self, user_id: str, username: str, data_dir: str = "data"):
        """
        Initialize user progress tracking.
        
        Args:
            user_id: Unique user identifier
            username: Display username
            data_dir: Directory containing data files
        """
        self.user_id = user_id
        self.username = username
        self.data_dir = Path(data_dir)
        
        # Core progression data
        self.level = 1
        self.total_xp = 0
        self.xp_to_next_level = self._calculate_xp_for_next_level()
        
        # Achievement system
        self.achievements: Dict[str, Achievement] = {}
        self.earned_achievements: List[UserAchievement] = []
        
        # Specialty proficiency
        self.specialties: Dict[str, SpecialtyProficiency] = {}
        
        # Streak tracking
        self.streak_data = StreakData(
            current_streak=0,
            longest_streak=0,
            streak_start_date=None,
            last_correct_date=None,
            streak_multiplier=1.0
        )
        
        # Performance tracking
        self.performance_metrics = PerformanceMetrics(
            total_cases=0,
            correct_diagnoses=0,
            overall_accuracy=0.0,
            average_time_per_case=0.0,
            category_performance={},
            difficulty_performance={},
            recent_performance=[],
            improvement_trend=0.0
        )
        
        # Unlock system
        self.unlock_status = UnlockStatus(
            unlocked_difficulties={"beginner"},
            unlocked_categories=set(),
            unlocked_special_features=set(),
            level_based_unlocks={},
            achievement_based_unlocks={}
        )
        
        # Session data
        self.session_data: Dict[str, Any] = {}
        self.daily_activity: Dict[str, int] = {}
        
        # Setup logging
        self.logger = logging.getLogger(__name__)
        if not self.logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            self.logger.addHandler(handler)
            self.logger.setLevel(logging.INFO)
        
        # Load data
        self._load_achievements()
        self._load_difficulty_tiers()
    
    def _load_achievements(self) -> None:
        """Load achievement definitions from file."""
        try:
            achievements_file = self.data_dir / "achievements.json"
            if achievements_file.exists():
                with open(achievements_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                for achievement_data in data.get('achievements', []):
                    achievement = Achievement(
                        id=achievement_data['id'],
                        name=achievement_data['name'],
                        description=achievement_data['description'],
                        category=AchievementCategory(achievement_data['category']),
                        xp_reward=achievement_data['xp_reward'],
                        badge_type=BadgeType(achievement_data['badge_type']),
                        requirements=achievement_data['requirements'],
                        icon=achievement_data['icon']
                    )
                    self.achievements[achievement.id] = achievement
                
                self.logger.info(f"Loaded {len(self.achievements)} achievements")
            else:
                self.logger.warning("Achievements file not found")
                
        except Exception as e:
            self.logger.error(f"Failed to load achievements: {e}")
    
    def _load_difficulty_tiers(self) -> None:
        """Load difficulty tier definitions."""
        try:
            tiers_file = self.data_dir / "difficulty_tiers.json"
            if tiers_file.exists():
                with open(tiers_file, 'r', encoding='utf-8') as f:
                    self.difficulty_tiers = json.load(f)
                self.logger.info("Loaded difficulty tiers")
            else:
                self.logger.warning("Difficulty tiers file not found")
                self.difficulty_tiers = {}
        except Exception as e:
            self.logger.error(f"Failed to load difficulty tiers: {e}")
            self.difficulty_tiers = {}
    
    def _calculate_xp_for_next_level(self) -> int:
        """Calculate XP needed for next level using exponential scaling."""
        return int(100 * (1.5 ** (self.level - 1)))
    
    def _calculate_level_from_xp(self, total_xp: int) -> int:
        """Calculate level from total XP."""
        level = 1
        xp_needed = 100
        
        while total_xp >= xp_needed:
            total_xp -= xp_needed
            level += 1
            xp_needed = int(100 * (1.5 ** (level - 1)))
        
        return level
    
    def add_xp(self, xp_amount: int, source: str = "case_completion") -> Tuple[int, bool, List[str]]:
        """
        Add XP to user and handle level ups.
        
        Args:
            xp_amount: Amount of XP to add
            source: Source of XP (case_completion, achievement, bonus)
            
        Returns:
            Tuple of (new_total_xp, leveled_up, achievement_ids)
        """
        old_level = self.level
        self.total_xp += xp_amount
        self.level = self._calculate_level_from_xp(self.total_xp)
        self.xp_to_next_level = self._calculate_xp_for_next_level()
        
        leveled_up = self.level > old_level
        new_achievements = []
        
        if leveled_up:
            self.logger.info(f"User {self.username} leveled up to {self.level}")
            # Check for level-based achievements
            new_achievements = self._check_level_achievements()
            # Update unlocks based on new level
            self._update_level_unlocks()
        
        return self.total_xp, leveled_up, new_achievements
    
    def _check_level_achievements(self) -> List[str]:
        """Check for level-based achievements."""
        new_achievements = []
        
        level_achievements = {
            10: "level_10",
            25: "level_25", 
            50: "level_50"
        }
        
        for level_req, achievement_id in level_achievements.items():
            if self.level >= level_req and achievement_id not in [ea.achievement_id for ea in self.earned_achievements]:
                if self.award_achievement(achievement_id):
                    new_achievements.append(achievement_id)
        
        return new_achievements
    
    def _update_level_unlocks(self) -> None:
        """Update unlocks based on current level."""
        if not self.difficulty_tiers:
            return
        
        tiers = self.difficulty_tiers.get('difficulty_tiers', {})
        
        for tier_name, tier_data in tiers.items():
            level_req = tier_data.get('level_requirement', 1)
            if self.level >= level_req and tier_name not in self.unlock_status.unlocked_difficulties:
                self.unlock_status.unlocked_difficulties.add(tier_name)
                self.logger.info(f"Unlocked {tier_name} difficulty tier")
    
    def award_achievement(self, achievement_id: str) -> bool:
        """
        Award an achievement to the user.
        
        Args:
            achievement_id: ID of achievement to award
            
        Returns:
            True if achievement was awarded, False if already earned or not found
        """
        if achievement_id not in self.achievements:
            self.logger.warning(f"Achievement {achievement_id} not found")
            return False
        
        # Check if already earned
        if achievement_id in [ea.achievement_id for ea in self.earned_achievements]:
            return False
        
        achievement = self.achievements[achievement_id]
        user_achievement = UserAchievement(
            achievement_id=achievement_id,
            earned_at=datetime.now(),
            xp_awarded=achievement.xp_reward
        )
        
        self.earned_achievements.append(user_achievement)
        
        # Add XP reward
        self.add_xp(achievement.xp_reward, f"achievement_{achievement_id}")
        
        # Update achievement-based unlocks
        self.unlock_status.achievement_based_unlocks[achievement_id] = datetime.now().isoformat()
        
        self.logger.info(f"Awarded achievement: {achievement.name} to {self.username}")
        return True
    
    def update_streak(self, is_correct: bool) -> Tuple[int, float]:
        """
        Update streak data based on answer correctness.
        
        Args:
            is_correct: Whether the answer was correct
            
        Returns:
            Tuple of (current_streak, streak_multiplier)
        """
        now = datetime.now()
        
        if is_correct:
            # Check if streak continues from previous day
            if self.streak_data.last_correct_date:
                days_since_last = (now.date() - self.streak_data.last_correct_date.date()).days
                if days_since_last > 1:
                    # Streak broken
                    self.streak_data.current_streak = 0
                    self.streak_data.streak_start_date = now
            
            self.streak_data.current_streak += 1
            self.streak_data.last_correct_date = now
            
            if self.streak_data.current_streak == 1:
                self.streak_data.streak_start_date = now
            
            # Update longest streak
            if self.streak_data.current_streak > self.streak_data.longest_streak:
                self.streak_data.longest_streak = self.streak_data.current_streak
            
            # Calculate streak multiplier
            self.streak_data.streak_multiplier = self._calculate_streak_multiplier()
            
            # Check for streak achievements
            self._check_streak_achievements()
            
        else:
            # Reset current streak but keep longest
            self.streak_data.current_streak = 0
            self.streak_data.streak_multiplier = 1.0
        
        return self.streak_data.current_streak, self.streak_data.streak_multiplier
    
    def _calculate_streak_multiplier(self) -> float:
        """Calculate XP multiplier based on current streak."""
        streak = self.streak_data.current_streak
        
        if streak >= 20:
            return 2.0
        elif streak >= 15:
            return 1.75
        elif streak >= 10:
            return 1.5
        elif streak >= 5:
            return 1.25
        elif streak >= 3:
            return 1.1
        else:
            return 1.0
    
    def _check_streak_achievements(self) -> None:
        """Check for streak-based achievements."""
        streak_achievements = {
            10: "perfect_streak"
        }
        
        for streak_req, achievement_id in streak_achievements.items():
            if self.streak_data.current_streak >= streak_req:
                self.award_achievement(achievement_id)
    
    def update_specialty_proficiency(self, category: str, is_correct: bool, 
                                  time_taken: float, xp_earned: int) -> None:
        """
        Update proficiency in a diagnostic category.
        
        Args:
            category: Diagnostic category
            is_correct: Whether diagnosis was correct
            time_taken: Time taken for diagnosis
            xp_earned: XP earned from this case
        """
        now = datetime.now()
        
        if category not in self.specialties:
            self.specialties[category] = SpecialtyProficiency(
                category=category,
                level=1,
                cases_completed=0,
                accuracy=0.0,
                xp_earned=0,
                last_practiced=now
            )
        
        proficiency = self.specialties[category]
        proficiency.cases_completed += 1
        proficiency.xp_earned += xp_earned
        proficiency.last_practiced = now
        
        # Update accuracy
        if is_correct:
            # Simple moving average for accuracy
            correct_count = int(proficiency.accuracy * (proficiency.cases_completed - 1) / 100) + 1
            proficiency.accuracy = (correct_count / proficiency.cases_completed) * 100
        else:
            correct_count = int(proficiency.accuracy * (proficiency.cases_completed - 1) / 100)
            proficiency.accuracy = (correct_count / proficiency.cases_completed) * 100
        
        # Update proficiency level (1-10 scale)
        proficiency.level = min(10, int(proficiency.accuracy / 10) + 1)
        
        # Check for specialty achievements
        self._check_specialty_achievements(category)
    
    def _check_specialty_achievements(self, category: str) -> None:
        """Check for specialty-based achievements."""
        proficiency = self.specialties.get(category)
        if not proficiency:
            return
        
        # Map categories to achievement IDs
        specialty_achievements = {
            "Depressive Disorders": "depressive_disorders_master",
            "Schizophrenia Spectrum and Other Psychotic Disorders": "schizophrenia_spectrum_expert",
            "Anxiety Disorders": "anxiety_disorders_specialist"
        }
        
        if category in specialty_achievements:
            achievement_id = specialty_achievements[category]
            achievement = self.achievements.get(achievement_id)
            
            if achievement:
                reqs = achievement.requirements
                if (proficiency.cases_completed >= reqs.get('count', 0) and 
                    proficiency.accuracy >= reqs.get('min_accuracy', 0)):
                    self.award_achievement(achievement_id)
    
    def calculate_adaptive_difficulty(self, recent_performance: List[Dict[str, Any]]) -> str:
        """
        Calculate adaptive difficulty recommendation based on performance.
        
        Args:
            recent_performance: List of recent case performances
            
        Returns:
            Recommended difficulty level
        """
        if not recent_performance:
            return "beginner"
        
        # Calculate recent accuracy and average time
        recent_accuracy = sum(p.get('accuracy', 0) for p in recent_performance) / len(recent_performance)
        recent_avg_time = sum(p.get('time_taken', 0) for p in recent_performance) / len(recent_performance)
        
        # Get current unlocked difficulties
        unlocked = list(self.unlock_status.unlocked_difficulties)
        
        # Determine appropriate difficulty
        if recent_accuracy >= 90 and recent_avg_time < 120:  # High accuracy, fast
            if "expert" in unlocked:
                return "expert"
            elif "advanced" in unlocked:
                return "advanced"
            elif "intermediate" in unlocked:
                return "intermediate"
        elif recent_accuracy >= 75:
            if "advanced" in unlocked:
                return "advanced"
            elif "intermediate" in unlocked:
                return "intermediate"
        elif recent_accuracy >= 60:
            if "intermediate" in unlocked:
                return "intermediate"
        
        return "beginner"
    
    def get_unlock_recommendations(self) -> Dict[str, Any]:
        """
        Get recommendations for unlocking new content.
        
        Returns:
            Dictionary with unlock recommendations
        """
        recommendations = {
            "next_difficulty": None,
            "xp_needed_for_next_level": self.xp_to_next_level,
            "achievements_close_to_completion": [],
            "recommended_focus_areas": []
        }
        
        # Check next difficulty unlock
        if not self.difficulty_tiers:
            return recommendations
        
        tiers = self.difficulty_tiers.get('difficulty_tiers', {})
        for tier_name, tier_data in tiers.items():
            if tier_name not in self.unlock_status.unlocked_difficulties:
                level_req = tier_data.get('level_requirement', 1)
                if self.level < level_req:
                    recommendations["next_difficulty"] = {
                        "tier": tier_name,
                        "level_required": level_req,
                        "levels_needed": level_req - self.level
                    }
                break
        
        # Check achievements close to completion
        for achievement_id, achievement in self.achievements.items():
            if achievement_id not in [ea.achievement_id for ea in self.earned_achievements]:
                progress = self._calculate_achievement_progress(achievement_id)
                if progress >= 0.7:  # 70% or more complete
                    recommendations["achievements_close_to_completion"].append({
                        "achievement_id": achievement_id,
                        "name": achievement.name,
                        "progress": progress
                    })
        
        # Recommend focus areas based on weak performance
        for category, proficiency in self.specialties.items():
            if proficiency.accuracy < 70:
                recommendations["recommended_focus_areas"].append({
                    "category": category,
                    "current_accuracy": proficiency.accuracy,
                    "cases_needed": max(5, 10 - proficiency.cases_completed)
                })
        
        return recommendations
    
    def _calculate_achievement_progress(self, achievement_id: str) -> float:
        """Calculate progress towards an achievement (0.0 to 1.0)."""
        achievement = self.achievements.get(achievement_id)
        if not achievement:
            return 0.0
        
        reqs = achievement.requirements
        req_type = reqs.get('type')
        
        if req_type == 'case_completion':
            completed = len(self.earned_achievements)  # Simplified
            return min(1.0, completed / reqs.get('count', 1))
        
        elif req_type == 'case_completion_with_accuracy':
            # Use overall accuracy
            accuracy = self.performance_metrics.overall_accuracy
            if accuracy >= reqs.get('min_accuracy', 0):
                return min(1.0, self.performance_metrics.total_cases / reqs.get('count', 1))
            return 0.0
        
        elif req_type == 'category_mastery':
            category = reqs.get('category')
            if category is None:
                return 0.0
            proficiency = self.specialties.get(category)
            if proficiency:
                count_progress = min(1.0, proficiency.cases_completed / reqs.get('count', 1))
                accuracy_progress = min(1.0, proficiency.accuracy / reqs.get('min_accuracy', 100))
                return (count_progress + accuracy_progress) / 2
        
        elif req_type == 'streak':
            return min(1.0, self.streak_data.current_streak / reqs.get('count', 1))
        
        elif req_type == 'level':
            return min(1.0, self.level / reqs.get('min_level', 1))
        
        return 0.0
    
    def update_performance_metrics(self, case_result: Dict[str, Any]) -> None:
        """
        Update performance metrics with new case result.
        
        Args:
            case_result: Dictionary containing case performance data
        """
        self.performance_metrics.total_cases += 1
        
        if case_result.get('is_correct', False):
            self.performance_metrics.correct_diagnoses += 1
        
        # Update overall accuracy
        self.performance_metrics.overall_accuracy = (
            self.performance_metrics.correct_diagnoses / self.performance_metrics.total_cases * 100
        )
        
        # Update average time
        total_time = self.performance_metrics.average_time_per_case * (self.performance_metrics.total_cases - 1)
        total_time += case_result.get('time_taken', 0)
        self.performance_metrics.average_time_per_case = total_time / self.performance_metrics.total_cases
        
        # Update category performance
        category = case_result.get('category', 'unknown')
        if category not in self.performance_metrics.category_performance:
            self.performance_metrics.category_performance[category] = {
                'total': 0,
                'correct': 0,
                'total_time': 0
            }
        
        cat_perf = self.performance_metrics.category_performance[category]
        cat_perf['total'] += 1
        if case_result.get('is_correct', False):
            cat_perf['correct'] += 1
        cat_perf['total_time'] += case_result.get('time_taken', 0)
        cat_perf['accuracy'] = (cat_perf['correct'] / cat_perf['total']) * 100
        cat_perf['avg_time'] = cat_perf['total_time'] / cat_perf['total']
        
        # Update difficulty performance
        difficulty = case_result.get('difficulty', 'beginner')
        if difficulty not in self.performance_metrics.difficulty_performance:
            self.performance_metrics.difficulty_performance[difficulty] = {
                'total': 0,
                'correct': 0,
                'total_time': 0
            }
        
        diff_perf = self.performance_metrics.difficulty_performance[difficulty]
        diff_perf['total'] += 1
        if case_result.get('is_correct', False):
            diff_perf['correct'] += 1
        diff_perf['total_time'] += case_result.get('time_taken', 0)
        diff_perf['accuracy'] = (diff_perf['correct'] / diff_perf['total']) * 100 if diff_perf['total'] > 0 else 0
        diff_perf['avg_time'] = diff_perf['total_time'] / diff_perf['total'] if diff_perf['total'] > 0 else 0
        
        # Update recent performance (keep last 20)
        self.performance_metrics.recent_performance.append({
            'timestamp': datetime.now().isoformat(),
            'accuracy': 100 if case_result.get('is_correct', False) else 0,
            'time_taken': case_result.get('time_taken', 0),
            'category': category,
            'difficulty': difficulty
        })
        
        if len(self.performance_metrics.recent_performance) > 20:
            self.performance_metrics.recent_performance.pop(0)
        
        # Calculate improvement trend
        self._calculate_improvement_trend()
    
    def _calculate_improvement_trend(self) -> None:
        """Calculate improvement trend based on recent performance."""
        recent = self.performance_metrics.recent_performance
        if len(recent) < 10:
            self.performance_metrics.improvement_trend = 0.0
            return
        
        # Compare first half with second half
        mid = len(recent) // 2
        first_half = recent[:mid]
        second_half = recent[mid:]
        
        first_avg = sum(p['accuracy'] for p in first_half) / len(first_half)
        second_avg = sum(p['accuracy'] for p in second_half) / len(second_half)
        
        self.performance_metrics.improvement_trend = second_avg - first_avg
    
    def generate_performance_report(self) -> Dict[str, Any]:
        """
        Generate comprehensive performance report.
        
        Returns:
            Dictionary containing detailed performance analysis
        """
        return {
            'user_info': {
                'user_id': self.user_id,
                'username': self.username,
                'level': self.level,
                'total_xp': self.total_xp,
                'xp_to_next_level': self.xp_to_next_level
            },
            'progression': {
                'level_progress': (self.total_xp % self._calculate_xp_for_next_level()) / self._calculate_xp_for_next_level(),
                'achievements_earned': len(self.earned_achievements),
                'total_achievements': len(self.achievements)
            },
            'streak': {
                'current_streak': self.streak_data.current_streak,
                'longest_streak': self.streak_data.longest_streak,
                'multiplier': self.streak_data.streak_multiplier
            },
            'specialties': {
                cat: asdict(prof) for cat, prof in self.specialties.items()
            },
            'performance': asdict(self.performance_metrics),
            'unlocks': {
                'unlocked_difficulties': list(self.unlock_status.unlocked_difficulties),
                'unlocked_categories': list(self.unlock_status.unlocked_categories),
                'special_features': list(self.unlock_status.unlocked_special_features)
            },
            'recommendations': self.get_unlock_recommendations()
        }
    
    def get_xp_breakdown(self) -> Dict[str, Any]:
        """
        Get detailed breakdown of XP sources.
        
        Returns:
            Dictionary with XP breakdown by source
        """
        xp_from_achievements = sum(ea.xp_awarded for ea in self.earned_achievements)
        xp_from_cases = self.total_xp - xp_from_achievements
        
        return {
            'total_xp': self.total_xp,
            'xp_from_cases': xp_from_cases,
            'xp_from_achievements': xp_from_achievements,
            'xp_breakdown_percentage': {
                'cases': (xp_from_cases / self.total_xp * 100) if self.total_xp > 0 else 0,
                'achievements': (xp_from_achievements / self.total_xp * 100) if self.total_xp > 0 else 0
            },
            'largest_xp_achievements': [
                {
                    'name': self.achievements[ea.achievement_id].name,
                    'xp': ea.xp_awarded
                }
                for ea in sorted(self.earned_achievements, key=lambda x: x.xp_awarded, reverse=True)[:5]
            ]
        }
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert user progress to dictionary for serialization."""
        return {
            'user_id': self.user_id,
            'username': self.username,
            'level': self.level,
            'total_xp': self.total_xp,
            'xp_to_next_level': self.xp_to_next_level,
            'earned_achievements': [
                {
                    'achievement_id': ea.achievement_id,
                    'earned_at': ea.earned_at.isoformat(),
                    'xp_awarded': ea.xp_awarded
                }
                for ea in self.earned_achievements
            ],
            'specialties': {
                cat: {
                    **asdict(prof),
                    'last_practiced': prof.last_practiced.isoformat() if prof.last_practiced else None
                } for cat, prof in self.specialties.items()
            },
            'streak_data': {
                **asdict(self.streak_data),
                'streak_start_date': self.streak_data.streak_start_date.isoformat() if self.streak_data.streak_start_date else None,
                'last_correct_date': self.streak_data.last_correct_date.isoformat() if self.streak_data.last_correct_date else None
            },
            'performance_metrics': asdict(self.performance_metrics),
            'unlock_status': {
                'unlocked_difficulties': list(self.unlock_status.unlocked_difficulties),
                'unlocked_categories': list(self.unlock_status.unlocked_categories),
                'unlocked_special_features': list(self.unlock_status.unlocked_special_features),
                'level_based_unlocks': self.unlock_status.level_based_unlocks,
                'achievement_based_unlocks': self.unlock_status.achievement_based_unlocks
            },
            'daily_activity': self.daily_activity,
            'last_updated': datetime.now().isoformat()
        }
    
    def from_dict(self, data: Dict[str, Any]) -> None:
        """Load user progress from dictionary."""
        self.user_id = data['user_id']
        self.username = data['username']
        self.level = data['level']
        self.total_xp = data['total_xp']
        self.xp_to_next_level = data['xp_to_next_level']
        
        # Load earned achievements
        self.earned_achievements = []
        for ea_data in data.get('earned_achievements', []):
            ea = UserAchievement(
                achievement_id=ea_data['achievement_id'],
                earned_at=datetime.fromisoformat(ea_data['earned_at']),
                xp_awarded=ea_data['xp_awarded']
            )
            self.earned_achievements.append(ea)
        
        # Load specialties
        self.specialties = {}
        for cat, prof_data in data.get('specialties', {}).items():
            if prof_data.get('last_practiced'):
                if isinstance(prof_data['last_practiced'], str):
                    prof_data['last_practiced'] = datetime.fromisoformat(prof_data['last_practiced'])
            self.specialties[cat] = SpecialtyProficiency(**prof_data)
        
        # Load streak data
        streak_data = data.get('streak_data', {})
        if streak_data.get('streak_start_date') and isinstance(streak_data['streak_start_date'], str):
            streak_data['streak_start_date'] = datetime.fromisoformat(streak_data['streak_start_date'])
        if streak_data.get('last_correct_date') and isinstance(streak_data['last_correct_date'], str):
            streak_data['last_correct_date'] = datetime.fromisoformat(streak_data['last_correct_date'])
        self.streak_data = StreakData(**streak_data)
        
        # Load performance metrics
        perf_data = data.get('performance_metrics', {})
        self.performance_metrics = PerformanceMetrics(**perf_data)
        
        # Load unlock status
        unlock_data = data.get('unlock_status', {})
        self.unlock_status = UnlockStatus(
            unlocked_difficulties=set(unlock_data.get('unlocked_difficulties', [])),
            unlocked_categories=set(unlock_data.get('unlocked_categories', [])),
            unlocked_special_features=set(unlock_data.get('unlocked_special_features', [])),
            level_based_unlocks=unlock_data.get('level_based_unlocks', {}),
            achievement_based_unlocks=unlock_data.get('achievement_based_unlocks', {})
        )
        
        self.daily_activity = data.get('daily_activity', {})