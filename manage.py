#!/usr/bin/env python3
"""
Management script for Skhokho database operations
"""
import click
from app import create_app
from app.extensions import db
from app.models import User, Transaction, Service, Job, NetworkContact, Goal, CivicTicket


@click.group()
def cli():
    """Skhokho Database Management CLI"""
    pass


@cli.command()
def reset_db():
    """Drop all tables and recreate them fresh (DESTRUCTIVE!)"""
    app = create_app()
    
    with app.app_context():
        click.echo("⚠️  WARNING: This will DELETE ALL DATA!")
        if click.confirm('Are you sure you want to reset the database?'):
            click.echo("Dropping all tables...")
            db.drop_all()
            click.echo("✅ All tables dropped")
            
            click.echo("Creating fresh tables...")
            db.create_all()
            click.echo("✅ All tables created")
            
            click.echo("🎉 Database reset complete!")
        else:
            click.echo("❌ Operation cancelled")


@cli.command()
def init_db():
    """Initialize the database (create tables if they don't exist)"""
    app = create_app()
    
    with app.app_context():
        click.echo("Creating database tables...")
        db.create_all()
        click.echo("✅ Database initialized successfully!")


@cli.command()
def seed_demo():
    """Seed the database with demo data for hackathon"""
    app = create_app()
    
    with app.app_context():
        click.echo("Seeding demo data...")
        
        # Create demo users
        demo_user = User(username="demo", email="demo@skhokho.co.za")
        demo_user.set_password("demo123")
        demo_user.wallet_balance = 500.0
        demo_user.reputation_points = 150
        
        provider = User(username="provider", email="provider@skhokho.co.za")
        provider.set_password("provider123")
        provider.wallet_balance = 1000.0
        provider.reputation_points = 250
        
        db.session.add(demo_user)
        db.session.add(provider)
        db.session.commit()
        
        # Create demo service
        service = Service(
            user_id=provider.id,
            name="Plumbing Services",
            category="Home Repair",
            description="Professional plumbing services in Soweto",
            cost=200,
            latitude=-26.2485,
            longitude=27.8546
        )
        db.session.add(service)
        
        # Create demo goal
        goal = Goal(
            user_id=demo_user.id,
            title="Save R5000 for Business",
            description="Save money to start a small business"
        )
        db.session.add(goal)
        
        # Create demo transaction
        transaction = Transaction(
            user_id=demo_user.id,
            amount=500.0,
            transaction_type="Deposit",
            description="Initial demo deposit"
        )
        db.session.add(transaction)
        
        db.session.commit()
        
        click.echo("✅ Demo data seeded successfully!")
        click.echo(f"   Demo User: demo / demo123 (Balance: R500, Points: 150)")
        click.echo(f"   Provider: provider / provider123 (Balance: R1000, Points: 250)")


@cli.command()
def show_stats():
    """Show database statistics"""
    app = create_app()
    
    with app.app_context():
        user_count = User.query.count()
        transaction_count = Transaction.query.count()
        service_count = Service.query.count()
        job_count = Job.query.count()
        
        click.echo("📊 Database Statistics:")
        click.echo(f"   Users: {user_count}")
        click.echo(f"   Transactions: {transaction_count}")
        click.echo(f"   Services: {service_count}")
        click.echo(f"   Jobs: {job_count}")
        
        if user_count > 0:
            total_balance = db.session.query(db.func.sum(User.wallet_balance)).scalar() or 0
            total_reputation = db.session.query(db.func.sum(User.reputation_points)).scalar() or 0
            click.echo(f"   Total Wallet Balance: R{total_balance:.2f}")
            click.echo(f"   Total Reputation Points: {total_reputation}")


if __name__ == '__main__':
    cli()
