from pathlib import Path
class Gamestats:
    
    def __init__(self,ai_game):
        self.settings = ai_game.settings
        self.reset_stats()
        self.high_score = int(Path("score.txt").read_text())
        
    def reset_stats(self):
        self.ship_left = self.settings.ship_limit
        self.score = 0
        self.level = 1


