from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, ForeignKey, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime

Base = declarative_base()

class WaitlistEntry(Base):
    __tablename__ = "waitlist"
    
    id = Column(Integer, primary_key=True, index=True)
    contact_type = Column(String, nullable=False)  # "email" or "phone"
    contact_value = Column(String, unique=True, nullable=False, index=True)
    source = Column(String, default="website")
    referral_code = Column(String, unique=True, nullable=True, index=True)  # User's unique referral code
    referred_by = Column(String, nullable=True)  # Referral code of who referred them
    referral_count = Column(Integer, default=0)  # How many people they referred
    created_at = Column(DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f"<WaitlistEntry {self.contact_type}: {self.contact_value}>"

class ChatSession(Base):
    __tablename__ = "chat_sessions"
    
    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String, unique=True, nullable=False, index=True)
    product_name = Column(String, nullable=False)
    starting_price = Column(Float, nullable=False)
    current_price = Column(Float, nullable=False)
    minimum_price = Column(Float, nullable=False)  # Random minimum for this session
    final_price = Column(Float, nullable=True)
    deal_closed = Column(Boolean, default=False)
    discount_percentage = Column(Float, nullable=True)  # Track best discount
    referral_code = Column(String, unique=True, nullable=True, index=True)  # User's share code for challenge
    referred_by = Column(String, nullable=True)  # Who referred them to play
    created_at = Column(DateTime, default=datetime.utcnow)
    ended_at = Column(DateTime, nullable=True)
    
    # Relationship to messages
    messages = relationship("ConversationMessage", back_populates="session", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<ChatSession {self.session_id}: {self.product_name}>"

class ConversationMessage(Base):
    __tablename__ = "conversation_messages"
    
    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(Integer, ForeignKey("chat_sessions.id"), nullable=False)
    role = Column(String, nullable=False)  # "user" or "assistant"
    content = Column(Text, nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow)
    
    # Relationship to session
    session = relationship("ChatSession", back_populates="messages")
    
    def __repr__(self):
        return f"<Message {self.role}: {self.content[:50]}...>"

