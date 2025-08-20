from src.core.game_state import GameState
from src.services.version import get_display_version

print(f'Testing P(Doom) {get_display_version()}')
gs = GameState('test-seed')
print('✓ Game state initializes correctly')
# Add more checks as needed