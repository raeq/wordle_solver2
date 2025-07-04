from src.events.observer import GameEventBus
from src.modules.backend.game_engine import GameEngine
from src.modules.backend.stats_manager import StatsManager

# Create a shared event bus
bus = GameEventBus()

# Create StatsManager and GameEngine with the shared bus
stats = StatsManager(event_bus=bus)
engine = GameEngine(event_bus=bus)

# Start a new game
engine.start_new_game()

# Simulate guesses until the game ends
# For testing, just guess the target word to win immediately
result, is_solved = engine.make_guess(engine.target_word)

print("Game finished. Is solved?", is_solved)
print("StatsManager history:")
for game in stats.get_history():
    print(game)
