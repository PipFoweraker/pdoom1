# P(Doom) Privacy Policy & Technical Documentation

## Our Privacy Commitment

P(Doom) is designed with **privacy-first principles**. We believe that your gameplay data, choices, and strategies should remain under your control. This document outlines how we protect your privacy and what data practices we follow.

## Core Privacy Principles

### 1. **Minimal Data Collection**
- We collect only what is necessary for game functionality
- No personal information is required to play the game
- All data collection is transparent and documented

### 2. **User Control**
- **Opt-in only**: All data sharing features require explicit consent
- **Granular control**: Choose exactly what to share and when
- **Reversible**: Disable data sharing at any time without penalty

### 3. **Data Transparency**
- Open-source logging system - you can inspect all code
- Local-first storage - your data stays on your device by default
- Clear documentation of what data is collected and why

## Data Collection & Usage

### Game Data (Local Only by Default)
**What we collect locally:**
- Game state and progress
- Action choices and outcomes
- Performance metrics (turns taken, resources managed)
- Settings and preferences

**How it's used:**
- Save/load game functionality
- Performance tracking and improvement suggestions
- Local high score tracking
- Game balance and debugging (with explicit consent only)

**Your control:**
- All local data can be deleted through game settings
- Local logs can be disabled in privacy settings
- No local data is transmitted without your explicit consent

### Optional Leaderboard System
**When you opt-in to leaderboards:**
- **Pseudonymous identity**: You choose a display name (no real names required)
- **Game outcomes only**: Final scores, victory types, turn counts
- **Verification data**: Gameplay logs for competitive integrity (optional)
- **No personal data**: No emails, real names, or identifying information

**Leaderboard privacy features:**
- Pseudonymous participation only
- You control your display name
- Opt-out at any time
- Local-first with optional cloud sync

### Verbose Logging (Opt-in Only)
**Purpose:** Advanced players can enable detailed logging for:
- Strategy analysis and improvement
- Bug reporting and game balance feedback
- Competitive play verification
- Personal gameplay analytics

**What's logged when enabled:**
- Detailed action sequences and outcomes
- Random number generation events (for reproducibility)
- Resource changes and calculations
- Turn-by-turn game state progression

**Privacy protections:**
- **Disabled by default** - must be explicitly enabled
- **Local storage only** unless you choose to share
- **Full control** - enable/disable specific logging categories
- **Data ownership** - you own all logs generated

## Technical Privacy Implementation

### Deterministic Gaming System
Our deterministic RNG system enhances privacy by:
- **Reproducible gameplay**: Same seed = same game outcomes
- **Local verification**: Prove your achievements without sharing personal data
- **Anti-cheat without surveillance**: Verify game integrity through mathematical proofs
- **Competitive fairness**: Level playing field without data collection

### Privacy-Respecting Leaderboards
**Pseudonymous Design:**
```
Real Identity → [Local Only] 
Pseudonym → Leaderboard Entry
Game Data → Verification Hash
```

**Technical Safeguards:**
- No correlation between pseudonyms and real identities
- Local pseudonym generation and management
- Cryptographic verification without revealing strategies
- Minimal data transmission (scores only, not full game states)

### Local-First Architecture
- **Primary storage**: Your device
- **Cloud sync**: Optional and user-controlled
- **Offline play**: Full functionality without internet
- **Data portability**: Export your data anytime

## Your Privacy Rights

### Data Access
- **View all data**: Inspect any data we collect about you
- **Export data**: Get copies of your data in standard formats
- **Understand processing**: Clear explanations of how data is used

### Data Control
- **Opt-out anytime**: Disable any data collection feature
- **Selective sharing**: Choose exactly what to share
- **Delete data**: Remove any or all collected data
- **Modify settings**: Change privacy preferences without restriction

### Transparency
- **Open source**: All privacy-related code is auditable
- **Change notifications**: Clear notice of any policy updates
- **Contact us**: Direct access to privacy-related questions

## Privacy Settings Guide

### Essential Privacy Controls
```
Settings → Privacy → Data Collection
├── Local Logging: [Enabled/Disabled]
├── Verbose Logging: [Disabled/Standard/Full]
├── Leaderboard Participation: [Disabled/Enabled]
└── Anonymous Analytics: [Disabled/Enabled]
```

### Leaderboard Privacy Setup
```
Settings → Privacy → Leaderboards
├── Participation: [Opt-in Required]
├── Pseudonym: [User-chosen display name]
├── Data Sharing: [Scores only/Include verification data]
└── Visibility: [Public/Friends only/Private]
```

### Logging Controls
```
Settings → Privacy → Verbose Logging
├── Enable Logging: [Yes/No]
├── Log Level: [Minimal/Standard/Verbose/Debug]
├── Include RNG Data: [Yes/No]
├── Local Storage Only: [Yes/No]
└── Auto-cleanup: [Keep for X days]
```

## Data Security

### Local Data Protection
- **Encryption**: Sensitive data encrypted at rest
- **Access control**: Game data isolated from other applications
- **Backup privacy**: Encrypted backups maintain privacy
- **Secure deletion**: Complete removal of deleted data

### Network Communications (When Enabled)
- **TLS encryption**: All data transmission encrypted
- **Minimal payloads**: Only necessary data transmitted
- **Authentication without identification**: Prove legitimacy without revealing identity
- **No persistent tracking**: No cross-session correlation

## Developer Principles

### Privacy by Design
- Privacy considerations in every feature
- Default to most private settings
- Clear consent for any data sharing
- Regular privacy impact assessments

### Transparency Commitment
- **Open source approach**: Core privacy code is auditable
- **Documentation**: Clear explanations of all data practices
- **Communication**: Plain-language privacy information
- **Responsiveness**: Quick response to privacy concerns

### Data Minimization
- Collect only what's necessary for functionality
- Regular review and deletion of unnecessary data
- Purpose limitation - data used only as stated
- Storage limitation - automatic cleanup of old data

## Contact & Questions

### Privacy Concerns
- **Technical questions**: Review our open-source implementation
- **Policy questions**: Contact the development team
- **Data requests**: Use in-game privacy tools or contact support
- **Violation reports**: Direct channel for privacy issue reporting

### Staying Informed
- Privacy policy updates announced in-game
- Major changes require explicit re-consent
- Regular privacy reviews and improvements
- Community input welcomed on privacy features

## Implementation Timeline

### Current Status (v0.2.5)
✅ **Local-first data storage**
✅ **Pseudonymous leaderboard system**
✅ **Opt-in verbose logging**
✅ **Deterministic gameplay for verification**
✅ **Privacy controls in settings**

### Planned Enhancements
🔄 **Enhanced encryption for local data**
🔄 **Additional leaderboard privacy options**
🔄 **Automated data cleanup tools**
🔄 **Privacy dashboard for data overview**

---

*This document reflects our current privacy implementation and commitment. As an open-source project, you can verify these practices by reviewing our code. Privacy is fundamental to P(Doom)'s design, not an afterthought.*

**Last Updated:** September 4, 2025  
**Version:** 1.0  
**Effective:** Immediately
