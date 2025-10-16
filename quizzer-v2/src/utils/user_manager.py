#!/usr/bin/env python3
"""
User Manager
Handles user authentication, registration, and profile management
"""

import sqlite3
import hashlib
import secrets
import re
from pathlib import Path
from typing import Optional, Dict, List
from datetime import datetime


class UserManager:
    """Manage user accounts and authentication."""
    
    def __init__(self, db_path: str = "user_data/users.db"):
        """Initialize user manager with database.
        
        Args:
            db_path: Path to SQLite database file
        """
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_database()
    
    def _init_database(self):
        """Initialize database schema."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Users table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                salt TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_login TIMESTAMP
            )
        ''')
        
        # Quiz sessions table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS quiz_sessions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                course TEXT NOT NULL,
                difficulty TEXT,
                num_questions INTEGER,
                started_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                completed_at TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
            )
        ''')
        
        # Question attempts table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS question_attempts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id INTEGER NOT NULL,
                user_id INTEGER NOT NULL,
                question_type TEXT,
                points_awarded INTEGER,
                points_possible INTEGER,
                is_correct BOOLEAN,
                answered_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (session_id) REFERENCES quiz_sessions(id) ON DELETE CASCADE,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
            )
        ''')
        
        # Stars earned table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS stars (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                session_id INTEGER NOT NULL,
                stars_earned INTEGER DEFAULT 0,
                earned_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
                FOREIGN KEY (session_id) REFERENCES quiz_sessions(id) ON DELETE CASCADE
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def _hash_password(self, password: str, salt: str = None) -> tuple:
        """Hash password with salt.
        
        Args:
            password: Plain text password
            salt: Optional salt (generated if not provided)
            
        Returns:
            Tuple of (password_hash, salt)
        """
        if salt is None:
            salt = secrets.token_hex(32)
        
        password_hash = hashlib.pbkdf2_hmac(
            'sha256',
            password.encode('utf-8'),
            salt.encode('utf-8'),
            100000
        ).hex()
        
        return password_hash, salt
    
    def validate_username(self, username: str) -> tuple:
        """Validate username format.
        
        Args:
            username: Username to validate
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        if not username:
            return False, "Username cannot be empty"
        
        if len(username) < 3:
            return False, "Username must be at least 3 characters"
        
        if len(username) > 20:
            return False, "Username must be at most 20 characters"
        
        # Only alphanumeric characters
        if not re.match(r'^[A-Za-z0-9]+$', username):
            return False, "Username can only contain letters and numbers (no symbols)"
        
        return True, ""
    
    def validate_password(self, password: str) -> tuple:
        """Validate password format.
        
        Args:
            password: Password to validate
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        if not password:
            return False, "Password cannot be empty"
        
        if len(password) < 6:
            return False, "Password must be at least 6 characters"
        
        if len(password) > 50:
            return False, "Password must be at most 50 characters"
        
        # Allow letters, numbers, and common symbols
        if not re.match(r'^[A-Za-z0-9!@#$%^&*()_+\-=\[\]{};:\'",.<>/?]+$', password):
            return False, "Password contains invalid characters"
        
        return True, ""
    
    def register_user(self, username: str, password: str) -> tuple:
        """Register a new user.
        
        Args:
            username: Username
            password: Password
            
        Returns:
            Tuple of (success, message, user_id)
        """
        # Validate username
        valid, error = self.validate_username(username)
        if not valid:
            return False, error, None
        
        # Validate password
        valid, error = self.validate_password(password)
        if not valid:
            return False, error, None
        
        # Check if username already exists
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('SELECT id FROM users WHERE username = ?', (username,))
        if cursor.fetchone():
            conn.close()
            return False, "Username already exists", None
        
        # Hash password and create user
        password_hash, salt = self._hash_password(password)
        
        try:
            cursor.execute(
                'INSERT INTO users (username, password_hash, salt) VALUES (?, ?, ?)',
                (username, password_hash, salt)
            )
            user_id = cursor.lastrowid
            conn.commit()
            conn.close()
            return True, "Registration successful!", user_id
        except Exception as e:
            conn.close()
            return False, f"Registration failed: {str(e)}", None
    
    def login_user(self, username: str, password: str) -> tuple:
        """Authenticate user login.
        
        Args:
            username: Username
            password: Password
            
        Returns:
            Tuple of (success, message, user_id)
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute(
            'SELECT id, password_hash, salt FROM users WHERE username = ?',
            (username,)
        )
        result = cursor.fetchone()
        
        if not result:
            conn.close()
            return False, "Invalid username or password", None
        
        user_id, stored_hash, salt = result
        
        # Verify password
        password_hash, _ = self._hash_password(password, salt)
        
        if password_hash != stored_hash:
            conn.close()
            return False, "Invalid username or password", None
        
        # Update last login
        cursor.execute(
            'UPDATE users SET last_login = CURRENT_TIMESTAMP WHERE id = ?',
            (user_id,)
        )
        conn.commit()
        conn.close()
        
        return True, "Login successful!", user_id
    
    def delete_user(self, user_id: int) -> tuple:
        """Delete user and all associated data.
        
        Args:
            user_id: User ID to delete
            
        Returns:
            Tuple of (success, message)
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute('DELETE FROM users WHERE id = ?', (user_id,))
            conn.commit()
            conn.close()
            return True, "Account deleted successfully"
        except Exception as e:
            conn.close()
            return False, f"Failed to delete account: {str(e)}"
    
    def get_user_stats(self, user_id: int) -> Dict:
        """Get comprehensive user statistics.
        
        Args:
            user_id: User ID
            
        Returns:
            Dictionary with user statistics
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Get username
        cursor.execute('SELECT username, created_at FROM users WHERE id = ?', (user_id,))
        result = cursor.fetchone()
        if not result:
            conn.close()
            return None
        
        username, created_at = result
        
        # Total quizzes
        cursor.execute(
            'SELECT COUNT(*) FROM quiz_sessions WHERE user_id = ? AND completed_at IS NOT NULL',
            (user_id,)
        )
        total_quizzes = cursor.fetchone()[0]
        
        # Total questions answered
        cursor.execute(
            'SELECT COUNT(*) FROM question_attempts WHERE user_id = ?',
            (user_id,)
        )
        total_questions = cursor.fetchone()[0]
        
        # Correct answers
        cursor.execute(
            'SELECT COUNT(*) FROM question_attempts WHERE user_id = ? AND is_correct = 1',
            (user_id,)
        )
        correct_answers = cursor.fetchone()[0]
        
        # Incorrect answers
        incorrect_answers = total_questions - correct_answers
        
        # Total stars
        cursor.execute(
            'SELECT COALESCE(SUM(stars_earned), 0) FROM stars WHERE user_id = ?',
            (user_id,)
        )
        total_stars = cursor.fetchone()[0]
        
        # Average score
        cursor.execute(
            '''SELECT 
                COALESCE(AVG(CAST(points_awarded AS FLOAT) / points_possible * 100), 0)
                FROM question_attempts 
                WHERE user_id = ? AND points_possible > 0''',
            (user_id,)
        )
        avg_score = cursor.fetchone()[0]
        
        # Favorite course
        cursor.execute(
            '''SELECT course, COUNT(*) as count 
                FROM quiz_sessions 
                WHERE user_id = ? 
                GROUP BY course 
                ORDER BY count DESC 
                LIMIT 1''',
            (user_id,)
        )
        fav_result = cursor.fetchone()
        favorite_course = fav_result[0] if fav_result else "None"
        
        conn.close()
        
        return {
            'username': username,
            'member_since': created_at,
            'total_quizzes': total_quizzes,
            'total_questions': total_questions,
            'correct_answers': correct_answers,
            'incorrect_answers': incorrect_answers,
            'accuracy': (correct_answers / total_questions * 100) if total_questions > 0 else 0,
            'total_stars': total_stars,
            'average_score': round(avg_score, 1),
            'favorite_course': favorite_course
        }
    
    def record_quiz_session(self, user_id: int, course: str, difficulty: str, num_questions: int) -> int:
        """Start a new quiz session.
        
        Args:
            user_id: User ID
            course: Course name
            difficulty: Difficulty level
            num_questions: Number of questions
            
        Returns:
            Session ID
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute(
            '''INSERT INTO quiz_sessions (user_id, course, difficulty, num_questions)
               VALUES (?, ?, ?, ?)''',
            (user_id, course, difficulty, num_questions)
        )
        session_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        return session_id
    
    def complete_quiz_session(self, session_id: int, stars_earned: int):
        """Mark quiz session as complete and record stars.
        
        Args:
            session_id: Session ID
            stars_earned: Number of stars earned
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Update session
        cursor.execute(
            'UPDATE quiz_sessions SET completed_at = CURRENT_TIMESTAMP WHERE id = ?',
            (session_id,)
        )
        
        # Get user_id
        cursor.execute('SELECT user_id FROM quiz_sessions WHERE id = ?', (session_id,))
        user_id = cursor.fetchone()[0]
        
        # Record stars
        cursor.execute(
            'INSERT INTO stars (user_id, session_id, stars_earned) VALUES (?, ?, ?)',
            (user_id, session_id, stars_earned)
        )
        
        conn.commit()
        conn.close()
    
    def record_question_attempt(self, session_id: int, user_id: int, question_type: str,
                                points_awarded: int, points_possible: int, is_correct: bool):
        """Record a question attempt.
        
        Args:
            session_id: Quiz session ID
            user_id: User ID
            question_type: Type of question
            points_awarded: Points awarded
            points_possible: Maximum points possible
            is_correct: Whether answer was correct
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute(
            '''INSERT INTO question_attempts 
               (session_id, user_id, question_type, points_awarded, points_possible, is_correct)
               VALUES (?, ?, ?, ?, ?, ?)''',
            (session_id, user_id, question_type, points_awarded, points_possible, is_correct)
        )
        
        conn.commit()
        conn.close()


def main():
    """Test user manager."""
    print("🧪 Testing User Manager\n")
    
    manager = UserManager("user_data/test_users.db")
    
    # Test registration
    print("1. Testing registration...")
    success, msg, user_id = manager.register_user("TestUser123", "MyPass123!")
    print(f"   {msg} (User ID: {user_id})")
    
    # Test duplicate registration
    print("\n2. Testing duplicate registration...")
    success, msg, _ = manager.register_user("TestUser123", "AnotherPass!")
    print(f"   {msg}")
    
    # Test login
    print("\n3. Testing login...")
    success, msg, user_id = manager.login_user("TestUser123", "MyPass123!")
    print(f"   {msg}")
    
    # Test invalid login
    print("\n4. Testing invalid login...")
    success, msg, _ = manager.login_user("TestUser123", "WrongPass")
    print(f"   {msg}")
    
    # Test stats
    print("\n5. Testing user stats...")
    stats = manager.get_user_stats(user_id)
    print(f"   Username: {stats['username']}")
    print(f"   Total quizzes: {stats['total_quizzes']}")
    print(f"   Total questions: {stats['total_questions']}")
    
    print("\n✅ User manager tests complete!")


if __name__ == "__main__":
    main()
