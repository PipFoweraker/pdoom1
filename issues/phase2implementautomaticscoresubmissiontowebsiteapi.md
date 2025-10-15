# Phase 2: Implement Automatic Score Submission to Website API\n\n## Overview
Complete the weekly league system by implementing automatic score submission from game to website API.

## Background
The pdoom1-website v1.0.0 weekly league infrastructure is now complete and deployed:
- 8 API endpoints operational with CORS support
- Weekly league management system active (2025_W41)
- Real leaderboard data syncing (15 seeds, 64 entries)
- Professional-grade API server ready for score submission

## Implementation Required

### 1. Score Submission Module
Create `src/web_integration/score_submitter.py`:

```python
class ScoreSubmitter:
    def __init__(self, api_endpoint="https://pdoom1.com/api"):
        self.api_endpoint = api_endpoint
        self.player_uuid = self.get_or_create_player_id()
    
    def submit_score(self, game_session):
        """Submit completed game session to website API"""
        score_data = {
            "player_uuid": self.player_uuid,
            "player_name": game_session.lab_name,
            "seed": game_session.seed,
            "score": game_session.turns_survived,
            "final_metrics": {
                "doom_risk": game_session.final_doom,
                "money": game_session.final_money,
                "staff": game_session.final_staff,
                "reputation": game_session.final_reputation,
                "compute": game_session.final_compute,
                "papers": game_session.research_papers_published,
                "tech_debt": game_session.technical_debt
            },
            "game_version": "v0.4.1",
            "timestamp": datetime.now().isoformat(),
            "verification_hash": self.calculate_verification_hash(game_session)
        }
        
        return self.post_score(score_data)
```

### 2. Player Identity System
- Generate persistent player UUID
- Privacy-respecting pseudonymous system
- Optional player name customization

### 3. Game Integration Points
- Hook into game end events
- Submit scores on successful game completion
- Handle network failures gracefully
- Add player opt-in settings

### 4. API Communication
- HTTP client for POST to `/api/scores/submit`
- Proper error handling and retry logic
- Network connectivity checks
- Rate limiting respect

### 5. Privacy Controls
Add to game settings:
```python
LEADERBOARD_SETTINGS = {
    "submit_scores": True,      # Player opt-in
    "public_name": True,        # Show lab name publicly  
    "share_metrics": True,      # Share detailed game metrics
    "weekly_leagues": True      # Participate in weekly competitions
}
```

## Website API Endpoints Ready
- POST `/api/scores/submit` - Score submission endpoint
- GET `/api/league/current` - Current weekly league
- GET `/api/league/status` - League system status
- All endpoints have CORS support and proper validation

## Expected Outcome
- Players automatically submit scores upon game completion
- Real-time leaderboard updates
- Active weekly league participation
- Complete competitive ecosystem operational

## Testing Strategy
1. Local API server testing
2. Score submission validation
3. Leaderboard update verification
4. Error handling testing
5. Privacy settings validation

## Priority: HIGH
This completes the live competition workflow and enables real weekly league competitions.

## Related
- pdoom1-website v1.0.0 weekly league system: COMPLETE
- API infrastructure: OPERATIONAL
- Weekly league management: ACTIVE\n\n<!-- GitHub Issue #379 -->