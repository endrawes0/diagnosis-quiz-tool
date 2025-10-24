import json
import uuid
import hashlib
import threading
import shutil
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, asdict, field
import logging


@dataclass
class UserPreferences:
    """User preferences and settings."""
    difficulty_preference: str = "mixed"
    focus_areas: List[str] = field(default_factory=list)
    notifications: bool = True
    timer_enabled: bool = True
    theme: str = "default"
    language: str = "en"
    auto_save: bool = True
    privacy_mode: bool = False


@dataclass
class UserStatistics:
    """User performance statistics."""
    total_cases_attempted: int = 0
    total_correct: int = 0
    overall_accuracy: float = 0.0
    average_time_per_case: float = 0.0
    favorite_category: str = ""
    last_login: Optional[datetime] = None
    total_session_time: int = 0
    sessions_completed: int = 0
    
    def update_accuracy(self):
        """Update overall accuracy based on total and correct."""
        if self.total_cases_attempted > 0:
            self.overall_accuracy = (self.total_correct / self.total_cases_attempted) * 100


@dataclass
class CompletedCase:
    """Record of a completed case."""
    case_id: str
    completed_at: datetime
    xp_earned: int
    accuracy: float = 0.0
    time_taken: int = 0
    attempts: int = 1
    difficulty: str = "beginner"
    category: str = ""
    is_correct: bool = True
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            'case_id': self.case_id,
            'completed_at': self.completed_at.isoformat(),
            'xp_earned': self.xp_earned,
            'accuracy': self.accuracy,
            'time_taken': self.time_taken,
            'attempts': self.attempts,
            'difficulty': self.difficulty,
            'category': self.category,
            'is_correct': self.is_correct
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'CompletedCase':
        """Create from dictionary."""
        data['completed_at'] = datetime.fromisoformat(data['completed_at'])
        return cls(**data)


class UserProfile:
    """
    Comprehensive user profile management with persistence and security.
    """
    
    def __init__(self, user_id: str, username: str, data_dir: str = "data"):
        """
        Initialize user profile.
        
        Args:
            user_id: Unique user identifier
            username: Display username
            data_dir: Base data directory
        """
        self.user_id = user_id
        self.username = username
        self.data_dir = Path(data_dir)
        self.users_dir = self.data_dir / "users"
        self.backups_dir = self.users_dir / "backups"
        
        # Ensure directories exist
        self.users_dir.mkdir(parents=True, exist_ok=True)
        self.backups_dir.mkdir(parents=True, exist_ok=True)
        
        # Profile data
        self.created_at = datetime.now()
        self.last_updated = datetime.now()
        self.last_login = None
        
        # User preferences and statistics
        self.preferences = UserPreferences()
        self.statistics = UserStatistics()
        
        # Progress tracking - will be initialized lazily
        self._progress_data = None
        
        # Completed cases
        self.completed_cases: List[CompletedCase] = []
        
        # Session management
        self.session_id = None
        self.session_start = None
        self.is_active = False
        
        # Security
        self.password_hash = None
        self.salt = None
        self.failed_login_attempts = 0
        self.locked_until = None
        
        # Thread safety
        self._lock = threading.RLock()
        
        # Setup logging
        self.logger = logging.getLogger(f"{__name__}.{user_id}")
        if not self.logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            self.logger.addHandler(handler)
            self.logger.setLevel(logging.INFO)
    
    @property
    def progress(self):
        """Get or initialize UserProgress object."""
        if self._progress_data is None:
            # Import here to avoid circular imports
            try:
                from .progression import UserProgress
            except ImportError:
                # Fallback for different import paths
                import sys
                import os
                sys.path.append(os.path.dirname(os.path.dirname(__file__)))
                from modules.progression import UserProgress
            self._progress_data = UserProgress(self.user_id, self.username, str(self.data_dir))
        return self._progress_data
    
    def set_password(self, password: str) -> None:
        """
        Set user password with secure hashing.
        
        Args:
            password: Plain text password
        """
        self.salt = uuid.uuid4().hex
        self.password_hash = self._hash_password(password, self.salt)
        self.last_updated = datetime.now()
    
    def verify_password(self, password: str) -> bool:
        """
        Verify user password.
        
        Args:
            password: Password to verify
            
        Returns:
            True if password is correct
        """
        if not self.password_hash or not self.salt:
            return False
        
        # Check if account is locked
        if self.locked_until and datetime.now() < self.locked_until:
            return False
        
        hashed = self._hash_password(password, self.salt)
        if hashed == self.password_hash:
            self.failed_login_attempts = 0
            self.locked_until = None
            return True
        else:
            self.failed_login_attempts += 1
            # Lock account after 5 failed attempts for 30 minutes
            if self.failed_login_attempts >= 5:
                self.locked_until = datetime.now() + timedelta(minutes=30)
                self.logger.warning(f"Account {self.user_id} locked due to failed login attempts")
            return False
    
    def _hash_password(self, password: str, salt: str) -> str:
        """Hash password with salt using SHA-256."""
        return hashlib.sha256((password + salt).encode()).hexdigest()
    
    def start_session(self) -> str:
        """
        Start a new user session.
        
        Returns:
            Session ID
        """
        with self._lock:
            self.session_id = uuid.uuid4().hex
            self.session_start = datetime.now()
            self.is_active = True
            self.last_login = datetime.now()
            self.statistics.last_login = self.last_login
            self.logger.info(f"Session started for user {self.username}")
            return self.session_id
    
    def end_session(self) -> Dict[str, Any]:
        """
        End current session and return session statistics.
        
        Returns:
            Session statistics dictionary
        """
        with self._lock:
            if not self.is_active or not self.session_start:
                return {}
            
            session_duration = int((datetime.now() - self.session_start).total_seconds())
            self.statistics.total_session_time += session_duration
            self.statistics.sessions_completed += 1
            
            session_stats = {
                'session_id': self.session_id,
                'duration_seconds': session_duration,
                'cases_completed': len([c for c in self.completed_cases 
                                       if c.completed_at >= self.session_start]),
                'xp_earned': sum(c.xp_earned for c in self.completed_cases 
                               if c.completed_at >= self.session_start)
            }
            
            self.session_id = None
            self.session_start = None
            self.is_active = False
            
            self.logger.info(f"Session ended for user {self.username}: {session_stats}")
            return session_stats
    
    def add_completed_case(self, case_result: Dict[str, Any]) -> None:
        """
        Add a completed case to user history.
        
        Args:
            case_result: Dictionary containing case performance data
        """
        with self._lock:
            completed_case = CompletedCase(
                case_id=case_result['case_id'],
                completed_at=datetime.now(),
                xp_earned=case_result.get('xp_earned', 0),
                accuracy=case_result.get('accuracy', 0.0),
                time_taken=case_result.get('time_taken', 0),
                attempts=case_result.get('attempts', 1),
                difficulty=case_result.get('difficulty', 'beginner'),
                category=case_result.get('category', ''),
                is_correct=case_result.get('is_correct', True)
            )
            
            self.completed_cases.append(completed_case)
            
            # Update statistics
            self.statistics.total_cases_attempted += 1
            if completed_case.is_correct:
                self.statistics.total_correct += 1
            self.statistics.update_accuracy()
            
            # Update average time
            if self.statistics.total_cases_attempted > 0:
                total_time = self.statistics.average_time_per_case * (self.statistics.total_cases_attempted - 1)
                total_time += completed_case.time_taken
                self.statistics.average_time_per_case = total_time / self.statistics.total_cases_attempted
            
            # Update favorite category
            if completed_case.category:
                category_counts = {}
                for case in self.completed_cases:
                    category_counts[case.category] = category_counts.get(case.category, 0) + 1
                if category_counts:
                    self.statistics.favorite_category = max(category_counts.items(), key=lambda x: x[1])[0]
            
            # Update progress
            self.progress.update_performance_metrics(case_result)
            self.progress.update_streak(completed_case.is_correct)
            self.progress.update_specialty_proficiency(
                completed_case.category, 
                completed_case.is_correct,
                completed_case.time_taken,
                completed_case.xp_earned
            )
            
            # Add XP
            self.progress.add_xp(completed_case.xp_earned, "case_completion")
            
            self.last_updated = datetime.now()
    
    def get_recent_cases(self, limit: int = 10) -> List[CompletedCase]:
        """
        Get recently completed cases.
        
        Args:
            limit: Maximum number of cases to return
            
        Returns:
            List of recent completed cases
        """
        return sorted(self.completed_cases, key=lambda x: x.completed_at, reverse=True)[:limit]
    
    def get_cases_by_category(self, category: str) -> List[CompletedCase]:
        """
        Get completed cases by category.
        
        Args:
            category: Category to filter by
            
        Returns:
            List of completed cases in the category
        """
        return [case for case in self.completed_cases if case.category == category]
    
    def get_cases_by_difficulty(self, difficulty: str) -> List[CompletedCase]:
        """
        Get completed cases by difficulty.
        
        Args:
            difficulty: Difficulty to filter by
            
        Returns:
            List of completed cases at the difficulty level
        """
        return [case for case in self.completed_cases if case.difficulty == difficulty]
    
    def update_preferences(self, preferences: Dict[str, Any]) -> None:
        """
        Update user preferences.
        
        Args:
            preferences: Dictionary of preferences to update
        """
        with self._lock:
            for key, value in preferences.items():
                if hasattr(self.preferences, key):
                    setattr(self.preferences, key, value)
            self.last_updated = datetime.now()
    
    def get_profile_summary(self) -> Dict[str, Any]:
        """
        Get comprehensive profile summary.
        
        Returns:
            Dictionary containing profile summary
        """
        return {
            'user_id': self.user_id,
            'username': self.username,
            'created_at': self.created_at.isoformat(),
            'last_login': self.last_login.isoformat() if self.last_login else None,
            'level': self.progress.level,
            'total_xp': self.progress.total_xp,
            'xp_to_next_level': self.progress.xp_to_next_level,
            'completed_cases_count': len(self.completed_cases),
            'achievements_count': len(self.progress.earned_achievements),
            'current_streak': self.progress.streak_data.current_streak,
            'longest_streak': self.progress.streak_data.longest_streak,
            'overall_accuracy': self.statistics.overall_accuracy,
            'favorite_category': self.statistics.favorite_category,
            'sessions_completed': self.statistics.sessions_completed,
            'total_session_time': self.statistics.total_session_time,
            'is_active': self.is_active,
            'preferences': asdict(self.preferences)
        }
    
    def export_data(self) -> Dict[str, Any]:
        """
        Export all user data for backup or migration.
        
        Returns:
            Dictionary containing all user data
        """
        return {
            'user_id': self.user_id,
            'username': self.username,
            'created_at': self.created_at.isoformat(),
            'last_updated': self.last_updated.isoformat(),
            'last_login': self.last_login.isoformat() if self.last_login else None,
            'preferences': asdict(self.preferences),
            'statistics': asdict(self.statistics),
            'completed_cases': [case.to_dict() for case in self.completed_cases],
            'progress_data': self.progress.to_dict(),
            'export_timestamp': datetime.now().isoformat(),
            'version': '1.0'
        }
    
    def import_data(self, data: Dict[str, Any], merge: bool = False) -> bool:
        """
        Import user data from export.
        
        Args:
            data: Exported user data
            merge: Whether to merge with existing data or replace
            
        Returns:
            True if import was successful
        """
        try:
            with self._lock:
                if not merge:
                    # Replace all data
                    self.username = data.get('username', self.username)
                    self.created_at = datetime.fromisoformat(data['created_at'])
                    self.preferences = UserPreferences(**data.get('preferences', {}))
                    
                    # Import statistics
                    stats_data = data.get('statistics', {})
                    if stats_data.get('last_login'):
                        stats_data['last_login'] = datetime.fromisoformat(stats_data['last_login'])
                    self.statistics = UserStatistics(**stats_data)
                    
                    # Import completed cases
                    self.completed_cases = [
                        CompletedCase.from_dict(case_data) 
                        for case_data in data.get('completed_cases', [])
                    ]
                    
                    # Import progress data
                    if 'progress_data' in data:
                        self.progress.from_dict(data['progress_data'])
                else:
                    # Merge data (prioritize newer data)
                    if data.get('last_updated'):
                        import_time = datetime.fromisoformat(data['last_updated'])
                        if import_time > self.last_updated:
                            # Import newer preferences
                            if 'preferences' in data:
                                for key, value in data['preferences'].items():
                                    if hasattr(self.preferences, key):
                                        setattr(self.preferences, key, value)
                            
                            # Import newer statistics
                            if 'statistics' in data:
                                stats_data = data['statistics']
                                if stats_data.get('last_login'):
                                    stats_data['last_login'] = datetime.fromisoformat(stats_data['last_login'])
                                for key, value in stats_data.items():
                                    if hasattr(self.statistics, key):
                                        setattr(self.statistics, key, value)
                            
                            # Merge completed cases (avoid duplicates)
                            existing_case_ids = {case.case_id for case in self.completed_cases}
                            for case_data in data.get('completed_cases', []):
                                if case_data['case_id'] not in existing_case_ids:
                                    self.completed_cases.append(CompletedCase.from_dict(case_data))
                
                self.last_updated = datetime.now()
                self.logger.info(f"Data imported successfully for user {self.username}")
                return True
                
        except Exception as e:
            self.logger.error(f"Failed to import data for user {self.username}: {e}")
            return False
    
    def validate_data_integrity(self) -> List[str]:
        """
        Validate data integrity and return list of issues.
        
        Returns:
            List of integrity issues found
        """
        issues = []
        
        # Check for duplicate case IDs
        case_ids = [case.case_id for case in self.completed_cases]
        if len(case_ids) != len(set(case_ids)):
            issues.append("Duplicate case IDs found in completed cases")
        
        # Check for invalid dates
        for case in self.completed_cases:
            if case.completed_at > datetime.now():
                issues.append(f"Case {case.case_id} has future completion date")
        
        # Check statistics consistency
        if self.statistics.total_cases_attempted != len(self.completed_cases):
            issues.append("Statistics case count doesn't match completed cases count")
        
        correct_count = sum(1 for case in self.completed_cases if case.is_correct)
        if self.statistics.total_correct != correct_count:
            issues.append("Statistics correct count doesn't match completed cases")
        
        # Check XP consistency
        total_xp_from_cases = sum(case.xp_earned for case in self.completed_cases)
        if abs(self.progress.total_xp - total_xp_from_cases) > 1000:  # Allow some tolerance for achievements
            issues.append("Total XP doesn't match sum of case XP")
        
        return issues
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert profile to dictionary for serialization."""
        return {
            'user_id': self.user_id,
            'username': self.username,
            'created_at': self.created_at.isoformat(),
            'last_updated': self.last_updated.isoformat(),
            'last_login': self.last_login.isoformat() if self.last_login else None,
            'preferences': asdict(self.preferences),
            'statistics': {
                **asdict(self.statistics),
                'last_login': self.statistics.last_login.isoformat() if self.statistics.last_login else None
            },
            'completed_cases': [case.to_dict() for case in self.completed_cases],
            'progress_data': self.progress.to_dict(),
            'password_hash': self.password_hash,
            'salt': self.salt,
            'failed_login_attempts': self.failed_login_attempts,
            'locked_until': self.locked_until.isoformat() if self.locked_until else None
        }
    
    def from_dict(self, data: Dict[str, Any]) -> None:
        """Load profile from dictionary."""
        self.user_id = data['user_id']
        self.username = data['username']
        self.created_at = datetime.fromisoformat(data['created_at'])
        self.last_updated = datetime.fromisoformat(data['last_updated'])
        
        if data.get('last_login'):
            self.last_login = datetime.fromisoformat(data['last_login'])
        
        # Load preferences
        self.preferences = UserPreferences(**data.get('preferences', {}))
        
        # Load statistics
        stats_data = data.get('statistics', {})
        if stats_data.get('last_login'):
            stats_data['last_login'] = datetime.fromisoformat(stats_data['last_login'])
        self.statistics = UserStatistics(**stats_data)
        
        # Load completed cases
        self.completed_cases = [
            CompletedCase.from_dict(case_data) 
            for case_data in data.get('completed_cases', [])
        ]
        
        # Load progress data
        if 'progress_data' in data:
            try:
                self.progress.from_dict(data['progress_data'])
            except Exception as e:
                self.logger.error(f"Failed to load progress data: {e}")
                # Initialize fresh progress if loading fails
                pass
        
        # Load security data
        self.password_hash = data.get('password_hash')
        self.salt = data.get('salt')
        self.failed_login_attempts = data.get('failed_login_attempts', 0)
        if data.get('locked_until'):
            self.locked_until = datetime.fromisoformat(data['locked_until'])


class UserManager:
    """
    Manages multiple user profiles with file-based persistence.
    """
    
    def __init__(self, data_dir: str = "data"):
        """
        Initialize user manager.
        
        Args:
            data_dir: Base data directory
        """
        self.data_dir = Path(data_dir)
        self.users_dir = self.data_dir / "users"
        self.backups_dir = self.users_dir / "backups"
        
        # Ensure directories exist
        self.users_dir.mkdir(parents=True, exist_ok=True)
        self.backups_dir.mkdir(parents=True, exist_ok=True)
        
        # Active sessions
        self.active_sessions: Dict[str, UserProfile] = {}
        
        # Thread safety
        self._lock = threading.RLock()
        
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
        
        # Load existing users
        self._load_user_index()
    
    def _load_user_index(self) -> None:
        """Load user index from file."""
        self.user_index_file = self.users_dir / "user_index.json"
        self.user_index = {}
        
        if self.user_index_file.exists():
            try:
                with open(self.user_index_file, 'r', encoding='utf-8') as f:
                    self.user_index = json.load(f)
                self.logger.info(f"Loaded user index with {len(self.user_index)} users")
            except Exception as e:
                self.logger.error(f"Failed to load user index: {e}")
                self.user_index = {}
    
    def _save_user_index(self) -> None:
        """Save user index to file."""
        try:
            with open(self.user_index_file, 'w', encoding='utf-8') as f:
                json.dump(self.user_index, f, indent=2, ensure_ascii=False)
        except Exception as e:
            self.logger.error(f"Failed to save user index: {e}")
    
    def _get_user_file(self, user_id: str) -> Path:
        """Get the file path for a user profile."""
        return self.users_dir / f"{user_id}.json"
    
    def _get_backup_file(self, user_id: str, timestamp: datetime) -> Path:
        """Get backup file path for a user."""
        return self.backups_dir / f"{user_id}_{timestamp.strftime('%Y%m%d_%H%M%S')}.json"
    
    def create_user(self, username: str, password: Optional[str] = None) -> Tuple[Optional[UserProfile], str]:
        """
        Create a new user profile.
        
        Args:
            username: Display username
            password: Optional password for authentication
            
        Returns:
            Tuple of (UserProfile, message)
        """
        with self._lock:
            # Check if username already exists
            for user_id, user_data in self.user_index.items():
                if user_data.get('username') == username:
                    return None, "Username already exists"
            
            # Generate unique user ID
            user_id = f"user_{uuid.uuid4().hex[:8]}"
            
            # Create user profile
            profile = UserProfile(user_id, username, str(self.data_dir))
            
            # Set password if provided
            if password:
                profile.set_password(password)
            
            # Save profile
            if self._save_profile(profile):
                # Update index
                self.user_index[user_id] = {
                    'username': username,
                    'created_at': profile.created_at.isoformat(),
                    'last_login': profile.last_login.isoformat() if profile.last_login else None
                }
                self._save_user_index()
                
                self.logger.info(f"Created new user: {username} ({user_id})")
                return profile, "User created successfully"
            else:
                return None, "Failed to save user profile"
    
    def load_user(self, user_id: str) -> Optional[UserProfile]:
        """
        Load user profile from file.
        
        Args:
            user_id: User ID to load
            
        Returns:
            UserProfile or None if not found
        """
        user_file = self._get_user_file(user_id)
        
        if not user_file.exists():
            return None
        
        try:
            with open(user_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            profile = UserProfile(data['user_id'], data['username'], str(self.data_dir))
            profile.from_dict(data)
            
            self.logger.info(f"Loaded user profile: {profile.username} ({user_id})")
            return profile
            
        except Exception as e:
            self.logger.error(f"Failed to load user {user_id}: {e}")
            return None
    
    def save_user(self, profile: UserProfile, create_backup: bool = True) -> bool:
        """
        Save user profile to file.
        
        Args:
            profile: UserProfile to save
            create_backup: Whether to create backup before saving
            
        Returns:
            True if save was successful
        """
        return self._save_profile(profile, create_backup)
    
    def _save_profile(self, profile: UserProfile, create_backup: bool = True) -> bool:
        """Internal method to save profile."""
        user_file = self._get_user_file(profile.user_id)
        
        try:
            # Create backup if requested and file exists
            if create_backup and user_file.exists():
                backup_file = self._get_backup_file(profile.user_id, datetime.now())
                shutil.copy2(user_file, backup_file)
                
                # Clean old backups (keep last 10)
                self._clean_old_backups(profile.user_id)
            
            # Save profile
            with open(user_file, 'w', encoding='utf-8') as f:
                json.dump(profile.to_dict(), f, indent=2, ensure_ascii=False)
            
            # Update index
            self.user_index[profile.user_id] = {
                'username': profile.username,
                'created_at': profile.created_at.isoformat(),
                'last_login': profile.last_login.isoformat() if profile.last_login else None
            }
            self._save_user_index()
            
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to save user {profile.user_id}: {e}")
            return False
    
    def _clean_old_backups(self, user_id: str, keep_count: int = 10) -> None:
        """Clean old backup files for a user."""
        backup_pattern = f"{user_id}_*.json"
        backup_files = list(self.backups_dir.glob(backup_pattern))
        
        # Sort by modification time (newest first)
        backup_files.sort(key=lambda x: x.stat().st_mtime, reverse=True)
        
        # Remove old backups
        for backup_file in backup_files[keep_count:]:
            try:
                backup_file.unlink()
            except Exception as e:
                self.logger.warning(f"Failed to remove backup {backup_file}: {e}")
    
    def authenticate_user(self, username: str, password: str) -> Optional[UserProfile]:
        """
        Authenticate user with username and password.
        
        Args:
            username: Username to authenticate
            password: Password to verify
            
        Returns:
            UserProfile if authentication successful, None otherwise
        """
        with self._lock:
            # Find user by username
            user_id = None
            for uid, user_data in self.user_index.items():
                if user_data.get('username') == username:
                    user_id = uid
                    break
            
            if not user_id:
                return None
            
            # Load user profile
            profile = self.load_user(user_id)
            if not profile:
                return None
            
            # Verify password
            if profile.verify_password(password):
                # Start session
                session_id = profile.start_session()
                self.active_sessions[session_id] = profile
                
                # Update index
                self.user_index[user_id]['last_login'] = profile.last_login.isoformat() if profile.last_login else None
                self._save_user_index()
                
                self.logger.info(f"User authenticated: {username}")
                return profile
            else:
                self.logger.warning(f"Authentication failed for user: {username}")
                return None
    
    def get_user_by_session(self, session_id: str) -> Optional[UserProfile]:
        """
        Get user profile by session ID.
        
        Args:
            session_id: Session ID to look up
            
        Returns:
            UserProfile if session found, None otherwise
        """
        return self.active_sessions.get(session_id)
    
    def end_session(self, session_id: str) -> Dict[str, Any]:
        """
        End user session.
        
        Args:
            session_id: Session ID to end
            
        Returns:
            Session statistics
        """
        with self._lock:
            profile = self.active_sessions.get(session_id)
            if not profile:
                return {}
            
            session_stats = profile.end_session()
            
            # Remove from active sessions
            del self.active_sessions[session_id]
            
            # Save profile
            self.save_user(profile)
            
            return session_stats
    
    def get_all_users(self) -> List[Dict[str, Any]]:
        """
        Get list of all users.
        
        Returns:
            List of user information dictionaries
        """
        users = []
        for user_id, user_data in self.user_index.items():
            users.append({
                'user_id': user_id,
                'username': user_data['username'],
                'created_at': user_data['created_at'],
                'last_login': user_data.get('last_login')
            })
        return users
    
    def delete_user(self, user_id: str, confirm: bool = False) -> bool:
        """
        Delete user profile.
        
        Args:
            user_id: User ID to delete
            confirm: Confirmation flag for safety
            
        Returns:
            True if deletion was successful
        """
        if not confirm:
            return False
        
        with self._lock:
            # Remove from index
            if user_id in self.user_index:
                del self.user_index[user_id]
                self._save_user_index()
            
            # Remove profile file
            user_file = self._get_user_file(user_id)
            try:
                if user_file.exists():
                    user_file.unlink()
            except Exception as e:
                self.logger.error(f"Failed to delete user file {user_file}: {e}")
                return False
            
            # Remove from active sessions
            sessions_to_remove = []
            for session_id, profile in self.active_sessions.items():
                if profile.user_id == user_id:
                    sessions_to_remove.append(session_id)
            
            for session_id in sessions_to_remove:
                del self.active_sessions[session_id]
            
            self.logger.info(f"Deleted user: {user_id}")
            return True
    
    def backup_all_users(self) -> str:
        """
        Create backup of all user profiles.
        
        Returns:
            Path to backup directory
        """
        backup_timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        backup_dir = self.backups_dir / f"full_backup_{backup_timestamp}"
        backup_dir.mkdir(exist_ok=True)
        
        try:
            # Backup user index
            shutil.copy2(self.user_index_file, backup_dir / "user_index.json")
            
            # Backup all user profiles
            for user_id in self.user_index.keys():
                user_file = self._get_user_file(user_id)
                if user_file.exists():
                    shutil.copy2(user_file, backup_dir / f"{user_id}.json")
            
            self.logger.info(f"Created full backup: {backup_dir}")
            return str(backup_dir)
            
        except Exception as e:
            self.logger.error(f"Failed to create backup: {e}")
            return ""
    
    def restore_from_backup(self, backup_dir: str) -> bool:
        """
        Restore user profiles from backup.
        
        Args:
            backup_dir: Path to backup directory
            
        Returns:
            True if restore was successful
        """
        backup_path = Path(backup_dir)
        if not backup_path.exists():
            return False
        
        try:
            # Create current backup before restore
            self.backup_all_users()
            
            # Restore user index
            index_file = backup_path / "user_index.json"
            if index_file.exists():
                shutil.copy2(index_file, self.user_index_file)
                self._load_user_index()
            
            # Restore user profiles
            for user_file in backup_path.glob("user_*.json"):
                shutil.copy2(user_file, self.users_dir / user_file.name)
            
            self.logger.info(f"Restored from backup: {backup_dir}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to restore from backup: {e}")
            return False
    
    def get_user_statistics(self) -> Dict[str, Any]:
        """
        Get overall user statistics.
        
        Returns:
            Dictionary with user statistics
        """
        total_users = len(self.user_index)
        active_sessions = len(self.active_sessions)
        
        # Calculate additional stats
        total_cases = 0
        total_xp = 0
        recent_logins = 0
        
        for user_id in self.user_index.keys():
            profile = self.load_user(user_id)
            if profile:
                total_cases += len(profile.completed_cases)
                total_xp += profile.progress.total_xp
                
                if profile.last_login:
                    days_since_login = (datetime.now() - profile.last_login).days
                    if days_since_login <= 7:
                        recent_logins += 1
        
        return {
            'total_users': total_users,
            'active_sessions': active_sessions,
            'total_cases_completed': total_cases,
            'total_xp_earned': total_xp,
            'recent_active_users': recent_logins,
            'average_cases_per_user': total_cases / total_users if total_users > 0 else 0,
            'average_xp_per_user': total_xp / total_users if total_users > 0 else 0
        }