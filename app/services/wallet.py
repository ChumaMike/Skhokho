"""
Universal Wallet Service
Handles all money movement across the Skhokho platform
"""
from app.extensions import db
from app.models import User, Transaction
from datetime import datetime
from sqlalchemy.exc import SQLAlchemyError


class WalletService:
    """Service for managing user wallets and transactions"""
    
    @staticmethod
    def deposit(user_id: int, amount: float, description: str = "Deposit") -> dict:
        """
        Add money to a user's wallet
        
        Args:
            user_id: The user's ID
            amount: Amount to deposit (must be positive)
            description: Optional description of the deposit
            
        Returns:
            dict with success status and message
        """
        if amount <= 0:
            return {"success": False, "message": "Amount must be positive"}
        
        try:
            user = db.session.get(User, user_id)
            if not user:
                return {"success": False, "message": "User not found"}
            
            # Update balance
            user.wallet_balance += amount
            
            # Create transaction record
            transaction = Transaction(
                user_id=user_id,
                amount=amount,
                transaction_type="Deposit",
                description=description
            )
            db.session.add(transaction)
            db.session.commit()
            
            return {
                "success": True,
                "message": f"Deposited R{amount:.2f}",
                "new_balance": user.wallet_balance
            }
        except SQLAlchemyError as e:
            db.session.rollback()
            return {"success": False, "message": f"Database error: {str(e)}"}
    
    @staticmethod
    def withdraw(user_id: int, amount: float, description: str = "Withdrawal") -> dict:
        """
        Withdraw money from a user's wallet
        
        Args:
            user_id: The user's ID
            amount: Amount to withdraw (must be positive)
            description: Optional description of the withdrawal
            
        Returns:
            dict with success status and message
        """
        if amount <= 0:
            return {"success": False, "message": "Amount must be positive"}
        
        try:
            user = db.session.get(User, user_id)
            if not user:
                return {"success": False, "message": "User not found"}
            
            # Check sufficient balance
            if user.wallet_balance < amount:
                return {
                    "success": False,
                    "message": f"Insufficient funds. Balance: R{user.wallet_balance:.2f}"
                }
            
            # Update balance
            user.wallet_balance -= amount
            
            # Create transaction record
            transaction = Transaction(
                user_id=user_id,
                amount=-amount,  # Negative for withdrawal
                transaction_type="Withdrawal",
                description=description
            )
            db.session.add(transaction)
            db.session.commit()
            
            return {
                "success": True,
                "message": f"Withdrew R{amount:.2f}",
                "new_balance": user.wallet_balance
            }
        except SQLAlchemyError as e:
            db.session.rollback()
            return {"success": False, "message": f"Database error: {str(e)}"}
    
    @staticmethod
    def transfer(from_id: int, to_id: int, amount: float, description: str = "Transfer") -> dict:
        """
        Transfer money between two users
        
        Args:
            from_id: Sender's user ID
            to_id: Recipient's user ID
            amount: Amount to transfer (must be positive)
            description: Optional description of the transfer
            
        Returns:
            dict with success status and message
        """
        if amount <= 0:
            return {"success": False, "message": "Amount must be positive"}
        
        if from_id == to_id:
            return {"success": False, "message": "Cannot transfer to yourself"}
        
        try:
            sender = db.session.get(User, from_id)
            recipient = db.session.get(User, to_id)
            
            if not sender:
                return {"success": False, "message": "Sender not found"}
            if not recipient:
                return {"success": False, "message": "Recipient not found"}
            
            # Check sufficient balance
            if sender.wallet_balance < amount:
                return {
                    "success": False,
                    "message": f"Insufficient funds. Balance: R{sender.wallet_balance:.2f}"
                }
            
            # Perform transfer
            sender.wallet_balance -= amount
            recipient.wallet_balance += amount
            
            # Create transaction records for both users
            sender_transaction = Transaction(
                user_id=from_id,
                amount=-amount,
                transaction_type="Payment",
                description=f"{description} to {recipient.username}",
                related_user_id=to_id
            )
            
            recipient_transaction = Transaction(
                user_id=to_id,
                amount=amount,
                transaction_type="Earning",
                description=f"{description} from {sender.username}",
                related_user_id=from_id
            )
            
            db.session.add(sender_transaction)
            db.session.add(recipient_transaction)
            db.session.commit()
            
            return {
                "success": True,
                "message": f"Transferred R{amount:.2f} to {recipient.username}",
                "sender_balance": sender.wallet_balance,
                "recipient_balance": recipient.wallet_balance
            }
        except SQLAlchemyError as e:
            db.session.rollback()
            return {"success": False, "message": f"Database error: {str(e)}"}
    
    @staticmethod
    def get_balance(user_id: int) -> dict:
        """Get user's current wallet balance"""
        try:
            user = db.session.get(User, user_id)
            if not user:
                return {"success": False, "message": "User not found"}
            
            return {
                "success": True,
                "balance": user.wallet_balance,
                "reputation_points": user.reputation_points
            }
        except SQLAlchemyError as e:
            return {"success": False, "message": f"Database error: {str(e)}"}
    
    @staticmethod
    def get_transaction_history(user_id: int, limit: int = 10) -> dict:
        """Get user's recent transaction history"""
        try:
            transactions = Transaction.query.filter_by(user_id=user_id)\
                .order_by(Transaction.timestamp.desc())\
                .limit(limit)\
                .all()
            
            return {
                "success": True,
                "transactions": [
                    {
                        "id": t.id,
                        "amount": t.amount,
                        "type": t.transaction_type,
                        "description": t.description,
                        "timestamp": t.timestamp.isoformat()
                    }
                    for t in transactions
                ]
            }
        except SQLAlchemyError as e:
            return {"success": False, "message": f"Database error: {str(e)}"}
    
    @staticmethod
    def add_reputation_points(user_id: int, points: int, reason: str = "Activity") -> dict:
        """
        Add reputation points to a user (global across all pillars)
        
        Args:
            user_id: The user's ID
            points: Points to add (can be negative for penalties)
            reason: Reason for the points
            
        Returns:
            dict with success status and message
        """
        try:
            user = db.session.get(User, user_id)
            if not user:
                return {"success": False, "message": "User not found"}
            
            user.reputation_points += points
            
            # Ensure reputation doesn't go negative
            if user.reputation_points < 0:
                user.reputation_points = 0
            
            db.session.commit()
            
            return {
                "success": True,
                "message": f"Added {points} reputation points for {reason}",
                "total_reputation": user.reputation_points
            }
        except SQLAlchemyError as e:
            db.session.rollback()
            return {"success": False, "message": f"Database error: {str(e)}"}
