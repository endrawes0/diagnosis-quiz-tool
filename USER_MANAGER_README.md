# User Profile Persistence System

This document describes the comprehensive user profile persistence system implemented for the diagnosis quiz tool.

## Overview

The user management system provides:
- Multi-user support with unique IDs
- Secure authentication and session management
- File-based persistence with JSON storage
- Thread-safe operations
- Automatic backup and recovery
- Data integrity validation
- Privacy and security considerations
- Easy migration path to database systems

## Architecture

### Core Components

#### 1. UserProfile Class (`src/modules/user_manager.py`)

The `UserProfile` class manages individual user data including:
- Basic profile information (ID, username, creation date)
- User preferences and settings
- Performance statistics
- Completed case history
- Progress tracking integration
- Session management
- Security features

#### 2. UserManager Class (`src/modules/user_manager.py`)

The `UserManager` class handles:
- Multi-user profile management
- Authentication and authorization
- File-based persistence operations
- Backup and recovery systems
- User statistics and reporting

#### 3. Data Structures

##### UserPreferences
```python
@dataclass
class UserPreferences:
    difficulty_preference: str = "mixed"
    focus_areas: List[str] = []
    notifications: bool = True
    timer_enabled: bool = True
    theme: str = "default"
    language: str = "en"
    auto_save: bool = True
    privacy_mode: bool = False
```

##### UserStatistics
```python
@dataclass
class UserStatistics:
    total_cases_attempted: int = 0
    total_correct: int = 0
    overall_accuracy: float = 0.0
    average_time_per_case: float = 0.0
    favorite_category: str = ""
    last_login: Optional[datetime] = None
    total_session_time: int = 0
    sessions_completed: int = 0
```

##### CompletedCase
```python
@dataclass
class CompletedCase:
    case_id: str
    completed_at: datetime
    xp_earned: int
    accuracy: float = 0.0
    time_taken: int = 0
    attempts: int = 1
    difficulty: str = "beginner"
    category: str = ""
    is_correct: bool = True
```

## Features

### 1. User Authentication

- **Password Security**: SHA-256 hashing with unique salts
- **Account Locking**: Automatic lock after 5 failed attempts (30 minutes)
- **Session Management**: Unique session IDs with timeout handling

```python
# Create user with password
profile, message = manager.create_user("username", "password123")

# Authenticate user
profile = manager.authenticate_user("username", "password123")
```

### 2. Profile Management

- **Profile Creation**: Automatic unique ID generation
- **Profile Loading**: Lazy loading with error handling
- **Profile Updates**: Real-time preference and statistics updates
- **Profile Deletion**: Safe deletion with confirmation

```python
# Create new profile
profile = UserProfile("user_123", "username", "data")

# Update preferences
profile.update_preferences({
    'difficulty_preference': 'advanced',
    'focus_areas': ['mood_disorders']
})
```

### 3. Progress Tracking Integration

- **XP System**: Experience points from case completion
- **Level Progression**: Automatic level calculation
- **Achievement Tracking**: Integration with achievement system
- **Specialty Proficiency**: Category-specific skill tracking

```python
# Add completed case
case_result = {
    'case_id': 'case_001',
    'xp_earned': 50,
    'accuracy': 100.0,
    'time_taken': 120,
    'difficulty': 'beginner',
    'category': 'mood_disorders',
    'is_correct': True
}
profile.add_completed_case(case_result)
```

### 4. Data Persistence

- **JSON Storage**: Human-readable file format
- **Thread Safety**: RLock protection for concurrent access
- **Atomic Operations**: Safe read/write operations
- **Data Validation**: Integrity checks on load/save

```python
# Save profile
manager.save_user(profile)

# Load profile
profile = manager.load_user("user_123")
```

### 5. Backup and Recovery

- **Automatic Backups**: Created before each save operation
- **Full System Backups**: Complete system state snapshots
- **Backup Cleanup**: Automatic cleanup of old backups (keep last 10)
- **Restore Functionality**: Complete system restoration

```python
# Create full backup
backup_path = manager.backup_all_users()

# Restore from backup
success = manager.restore_from_backup(backup_path)
```

### 6. Data Export/Import

- **Profile Export**: Complete user data export
- **Profile Import**: Data migration and merging
- **Version Control**: Export format versioning
- **Data Validation**: Import integrity checks

```python
# Export user data
export_data = profile.export_data()

# Import user data
new_profile = UserProfile("new_user", "username", "data")
success = new_profile.import_data(export_data, merge=True)
```

## File Structure

```
data/
├── users/
│   ├── user_index.json          # User registry
│   ├── user_abc12345.json       # Individual user profiles
│   ├── user_def67890.json
│   └── backups/
│       ├── full_backup_20231023_120000/
│       │   ├── user_index.json
│       │   ├── user_abc12345.json
│       │   └── user_def67890.json
│       ├── user_abc12345_20231023_120000.json
│       └── user_def67890_20231023_120000.json
└── schemas/
    └── user_profile_schema.json  # JSON schema validation
```

## Security Considerations

### 1. Password Security
- SHA-256 hashing with unique salts
- No plain text password storage
- Secure password verification

### 2. Account Protection
- Failed attempt tracking
- Automatic account locking
- Session timeout management

### 3. Data Privacy
- Privacy mode settings
- Sensitive data protection
- Optional data anonymization

### 4. Access Control
- Session-based authentication
- User-specific data isolation
- Secure session management

## Performance Optimizations

### 1. Lazy Loading
- Progress data loaded on demand
- Reduced memory footprint
- Faster initialization

### 2. Efficient Storage
- Compact JSON format
- Minimal file I/O operations
- Optimized data structures

### 3. Caching
- In-memory session storage
- Frequently accessed data caching
- Reduced database queries

## Error Handling

### 1. Data Validation
- Schema validation on load
- Integrity checks on save
- Automatic data repair

### 2. Graceful Degradation
- Fallback to default values
- Partial data recovery
- Error logging and reporting

### 3. Transaction Safety
- Atomic operations
- Rollback on failure
- Consistent state maintenance

## Migration Path

### 1. Database Migration
The system is designed for easy migration to database systems:

```python
# Example database adapter
class DatabaseUserManager(UserManager):
    def __init__(self, db_connection):
        self.db = db_connection
        # Override file-based methods with database operations
    
    def save_user(self, profile):
        # Database save implementation
        pass
    
    def load_user(self, user_id):
        # Database load implementation
        pass
```

### 2. Data Export
- Complete data export functionality
- Standardized JSON format
- Bulk migration support

## Usage Examples

### Basic User Management

```python
from src.modules.user_manager import UserManager

# Initialize manager
manager = UserManager("data")

# Create user
profile, message = manager.create_user("dr_smith", "password123")

# Authenticate
profile = manager.authenticate_user("dr_smith", "password123")

# Add completed case
case_result = {
    'case_id': 'case_001',
    'xp_earned': 50,
    'accuracy': 100.0,
    'time_taken': 120,
    'difficulty': 'beginner',
    'category': 'mood_disorders',
    'is_correct': True
}
profile.add_completed_case(case_result)

# End session
session_stats = manager.end_session(profile.session_id)
```

### Advanced Features

```python
# Get profile summary
summary = profile.get_profile_summary()

# Export data
export_data = profile.export_data()

# Validate integrity
issues = profile.validate_data_integrity()

# Get user statistics
stats = manager.get_user_statistics()

# Create backup
backup_path = manager.backup_all_users()
```

## Testing

The system includes comprehensive testing:

```bash
# Run user management tests
python3 test_user_manager.py
```

Test coverage includes:
- User creation and authentication
- Profile management operations
- Data persistence and recovery
- Security features
- Performance benchmarks
- Error handling scenarios

## Future Enhancements

### 1. Database Integration
- PostgreSQL/MySQL support
- Connection pooling
- Query optimization

### 2. Advanced Security
- Two-factor authentication
- OAuth integration
- Role-based access control

### 3. Analytics
- Learning analytics
- Performance insights
- Predictive modeling

### 4. Synchronization
- Cloud synchronization
- Multi-device support
- Real-time updates

## Conclusion

The user profile persistence system provides a robust, secure, and scalable foundation for managing user data in the diagnosis quiz tool. With comprehensive features for authentication, data management, and system administration, it ensures a reliable user experience while maintaining data integrity and security.

The modular design allows for easy extension and customization, while the file-based implementation provides simplicity and reliability. The system is ready for production use and can be easily migrated to database systems as requirements grow.