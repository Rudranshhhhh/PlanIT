"""User Profile - Preferences and Personalization.

Stores user preferences like:
- Budget preferences
- Travel style
- Dietary restrictions
- Interests
- Past trips
"""

from typing import Dict, Any, List, Optional
from datetime import datetime
import uuid
import json


class UserProfile:
    """User profile with travel preferences."""
    
    def __init__(self, user_id: str = None):
        self.user_id = user_id or str(uuid.uuid4())
        self.created_at = datetime.now()
        self.updated_at = datetime.now()
        
        # Preferences
        self.budget_preference: str = "moderate"  # budget, moderate, luxury
        self.travel_style: str = "balanced"  # adventure, relaxation, cultural, balanced
        self.pace: str = "moderate"  # slow, moderate, fast
        
        # Dietary & restrictions
        self.dietary: List[str] = []  # vegetarian, vegan, halal, kosher, allergies
        self.accessibility: List[str] = []
        
        # Interests
        self.interests: List[str] = []  # food, history, art, nature, nightlife, shopping
        
        # Travel history
        self.past_trips: List[Dict] = []
        self.favorite_destinations: List[str] = []
        
        # Other preferences
        self.preferred_accommodation: str = "hotel"  # hotel, hostel, airbnb, luxury
        self.preferred_transport: str = "public"  # public, car, walking, taxi
    
    def update(self, **kwargs):
        """Update profile fields."""
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)
        self.updated_at = datetime.now()
    
    def add_interest(self, interest: str):
        """Add an interest."""
        if interest not in self.interests:
            self.interests.append(interest)
            self.updated_at = datetime.now()
    
    def add_past_trip(self, destination: str, date: str = None, rating: int = None):
        """Record a past trip."""
        self.past_trips.append({
            "destination": destination,
            "date": date or datetime.now().strftime("%Y-%m"),
            "rating": rating
        })
        self.updated_at = datetime.now()
    
    def get_preferences_summary(self) -> str:
        """Get a text summary of preferences for prompts."""
        parts = [
            f"Budget: {self.budget_preference}",
            f"Travel style: {self.travel_style}",
            f"Pace: {self.pace}",
        ]
        
        if self.interests:
            parts.append(f"Interests: {', '.join(self.interests)}")
        
        if self.dietary:
            parts.append(f"Dietary: {', '.join(self.dietary)}")
        
        if self.favorite_destinations:
            parts.append(f"Favorite places: {', '.join(self.favorite_destinations)}")
        
        return "\n".join(parts)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert profile to dictionary."""
        return {
            "user_id": self.user_id,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "budget_preference": self.budget_preference,
            "travel_style": self.travel_style,
            "pace": self.pace,
            "dietary": self.dietary,
            "accessibility": self.accessibility,
            "interests": self.interests,
            "past_trips": self.past_trips,
            "favorite_destinations": self.favorite_destinations,
            "preferred_accommodation": self.preferred_accommodation,
            "preferred_transport": self.preferred_transport
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> "UserProfile":
        """Create profile from dictionary."""
        profile = cls(user_id=data.get("user_id"))
        
        for key in ["budget_preference", "travel_style", "pace", 
                    "preferred_accommodation", "preferred_transport"]:
            if key in data:
                setattr(profile, key, data[key])
        
        for key in ["dietary", "accessibility", "interests", 
                    "past_trips", "favorite_destinations"]:
            if key in data:
                setattr(profile, key, data[key])
        
        return profile


class UserProfileStore:
    """In-memory user profile store."""
    
    def __init__(self):
        self._profiles: Dict[str, UserProfile] = {}
    
    def create_profile(self, user_id: str = None) -> UserProfile:
        """Create a new user profile."""
        profile = UserProfile(user_id=user_id)
        self._profiles[profile.user_id] = profile
        return profile
    
    def get_profile(self, user_id: str) -> Optional[UserProfile]:
        """Get a user profile."""
        return self._profiles.get(user_id)
    
    def get_or_create_profile(self, user_id: str = None) -> UserProfile:
        """Get existing profile or create new one."""
        if user_id and user_id in self._profiles:
            return self._profiles[user_id]
        return self.create_profile(user_id=user_id)
    
    def update_profile(self, user_id: str, **kwargs) -> Optional[UserProfile]:
        """Update a user profile."""
        profile = self.get_profile(user_id)
        if profile:
            profile.update(**kwargs)
        return profile
    
    def delete_profile(self, user_id: str) -> bool:
        """Delete a user profile."""
        if user_id in self._profiles:
            del self._profiles[user_id]
            return True
        return False


# Global profile store instance
_profile_store: Optional[UserProfileStore] = None


def get_profile_store() -> UserProfileStore:
    """Get or create the global profile store."""
    global _profile_store
    if _profile_store is None:
        _profile_store = UserProfileStore()
    return _profile_store
