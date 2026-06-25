"""
app.py — CricketZone Entry Point
Usage: python app.py
"""

from cricketzone import create_app

app = create_app()

if __name__ == "__main__":
    app.run()