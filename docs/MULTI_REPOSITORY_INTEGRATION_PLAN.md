# Multi-Repository Integration Plan: P(Doom) Ecosystem

## Executive Summary

This document outlines the comprehensive integration plan for coordinating P(Doom)'s three-repository ecosystem: **game** (pdoom1), **website** (pdoom1-website), and **data** (pdoom-data) repositories, along with the required database infrastructure. The goal is to create a secure, scalable, and privacy-respecting ecosystem that enables seamless data flow, competitive features, and community engagement while maintaining the highest standards of security and user privacy.

## Current State Assessment

### ✅ Existing Infrastructure (Ready)
- **Website Pipeline**: Automated game→website content sync (dev-blog, releases)
- **Local Leaderboards**: Comprehensive seed-based competition system
- **Remote API Stubs**: Placeholder endpoints at `api.pdoom1.com/scores`
- **Privacy Framework**: GDPR-compliant pseudonymous data handling
- **GitHub Actions**: Cross-repo workflows with secure token management

### ❌ Missing Components (Implementation Required)
- **Data Repository**: `pdoom1-data` repository needs to be created
- **Database Schema**: User data, leaderboards, analytics, and content storage
- **API Gateway**: Secure REST API for cross-service communication
- **Authentication System**: User identity and authorization management
- **Data Synchronization**: Real-time sync between local and remote systems

### 📋 **Repository Status (Verified September 15, 2025)**
- **`PipFoweraker/pdoom1`** ✅ **ACTIVE** - Main game repository (current workspace)
- **`PipFoweraker/pdoom1-website`** ✅ **ACTIVE** - Website repository (20 open issues, actively maintained)
- **`PipFoweraker/pdoom-data`** ✅ **ACTIVE** - Data service repository (serves entire P(Doom) ecosystem)

## Repository Architecture Overview

```
P(Doom) Ecosystem Architecture

┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│     pdoom1      │    │  pdoom1-website │    │   pdoom-data    │
│   (Game Repo)   │    │ (Website Repo)  │    │ (Data Service)  │
├─────────────────┤    ├─────────────────┤    ├─────────────────┤
│ • Game Logic    │───▶│ • Static Site   │    │ • Database      │
│ • Local Data    │    │ • Blog System   │    │ • API Gateway   │
│ • Dev Tools     │    │ • Community     │◀───│ • Analytics     │
│ • CI/CD         │    │   Features      │    │ • Data Models   │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                        │                        │
         │                        │                        │
         └────────────────────────┼────────────────────────┘
                                  │
                    ┌─────────────────┐
                    │   PostgreSQL    │
                    │   Database      │
                    │  (Managed PaaS) │
                    └─────────────────┘
```

## Database Design

### Core Tables Schema

```sql
-- User Management
CREATE TABLE users (
    user_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    pseudonym VARCHAR(50) UNIQUE NOT NULL,
    email_hash VARCHAR(64), -- Hashed for privacy
    privacy_settings JSONB NOT NULL DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    last_active TIMESTAMP WITH TIME ZONE,
    opt_in_leaderboard BOOLEAN DEFAULT FALSE,
    opt_in_analytics BOOLEAN DEFAULT FALSE
);

-- Game Sessions
CREATE TABLE game_sessions (
    session_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(user_id) ON DELETE CASCADE,
    seed VARCHAR(100) NOT NULL,
    config_hash VARCHAR(64) NOT NULL,
    game_version VARCHAR(20) NOT NULL,
    started_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    completed_at TIMESTAMP WITH TIME ZONE,
    final_score INTEGER,
    final_turn INTEGER,
    victory_type VARCHAR(50),
    game_metadata JSONB,
    checksum VARCHAR(64), -- Anti-cheat verification
    duration_seconds FLOAT
);

-- Leaderboards
CREATE TABLE leaderboard_entries (
    entry_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    session_id UUID REFERENCES game_sessions(session_id) ON DELETE CASCADE,
    user_id UUID REFERENCES users(user_id) ON DELETE CASCADE,
    seed VARCHAR(100) NOT NULL,
    config_hash VARCHAR(64) NOT NULL,
    score INTEGER NOT NULL,
    rank INTEGER, -- Calculated field, updated by triggers
    submitted_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    verified BOOLEAN DEFAULT FALSE,
    metadata JSONB
);

-- Weekly Challenges
CREATE TABLE weekly_challenges (
    challenge_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    week_starting DATE NOT NULL,
    seed VARCHAR(100) NOT NULL,
    config_hash VARCHAR(64) NOT NULL,
    title VARCHAR(200) NOT NULL,
    description TEXT,
    reward_data JSONB,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Community Content
CREATE TABLE blog_entries (
    entry_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    title VARCHAR(200) NOT NULL,
    slug VARCHAR(200) UNIQUE NOT NULL,
    content TEXT NOT NULL,
    metadata JSONB,
    published_at TIMESTAMP WITH TIME ZONE,
    source_repo VARCHAR(50) DEFAULT 'pdoom1',
    sync_status VARCHAR(20) DEFAULT 'pending'
);

-- Analytics (Privacy-Respecting)
CREATE TABLE analytics_events (
    event_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(user_id) ON DELETE CASCADE,
    event_type VARCHAR(50) NOT NULL,
    event_data JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    -- Automatic deletion after 90 days for privacy
    expires_at TIMESTAMP WITH TIME ZONE DEFAULT (NOW() + INTERVAL '90 days')
);
```

### Indexes and Performance

```sql
-- Performance indexes
CREATE INDEX idx_leaderboard_seed_score ON leaderboard_entries(seed, score DESC);
CREATE INDEX idx_game_sessions_user_completed ON game_sessions(user_id, completed_at DESC);
CREATE INDEX idx_users_pseudonym ON users(pseudonym);
CREATE INDEX idx_analytics_user_type ON analytics_events(user_id, event_type);

-- Privacy cleanup job (automated)
CREATE OR REPLACE FUNCTION cleanup_expired_analytics() RETURNS void AS $$
BEGIN
    DELETE FROM analytics_events WHERE expires_at < NOW();
END;
$$ LANGUAGE plpgsql;
```

## API Architecture

### RESTful API Endpoints

```
pdoom1-data API Specification

Base URL: https://api.pdoom1.com/v1/

Authentication: Bearer token (JWT) or API key

Endpoints:

┌─────────────────────────────────────────────────────────────┐
│ Authentication & User Management                            │
├─────────────────────────────────────────────────────────────┤
│ POST   /auth/register          Create user account          │
│ POST   /auth/login            Authenticate user             │
│ POST   /auth/refresh          Refresh access token          │
│ GET    /users/profile         Get user profile              │
│ PATCH  /users/profile         Update privacy settings       │
│ DELETE /users/profile         Delete user account           │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│ Leaderboards & Scoring                                      │
├─────────────────────────────────────────────────────────────┤
│ POST   /leaderboards/submit   Submit game score             │
│ GET    /leaderboards/global   Get global leaderboard        │
│ GET    /leaderboards/seed/{seed} Get seed-specific board    │
│ GET    /leaderboards/user     Get user's scores             │
│ GET    /leaderboards/ranks    Get ranking statistics        │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│ Weekly Challenges                                           │
├─────────────────────────────────────────────────────────────┤
│ GET    /challenges/current    Get current weekly challenge  │
│ GET    /challenges/history    Get past challenges           │
│ POST   /challenges/submit     Submit challenge score        │
│ GET    /challenges/{id}/leaderboard Challenge rankings      │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│ Content Management                                          │
├─────────────────────────────────────────────────────────────┤
│ GET    /content/blog          Get blog entries              │
│ POST   /content/sync          Sync content from game repo   │
│ GET    /content/releases      Get release information       │
│ POST   /webhooks/github       GitHub webhook endpoint       │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│ Analytics (Privacy-Respecting)                             │
├─────────────────────────────────────────────────────────────┤
│ POST   /analytics/event       Record analytics event        │
│ GET    /analytics/aggregated  Get anonymized statistics     │
│ DELETE /analytics/user        Delete user analytics data    │
└─────────────────────────────────────────────────────────────┘
```

### Authentication & Security

```javascript
// JWT Token Structure
{
  "sub": "user_uuid",
  "pseudonym": "user_pseudonym",
  "permissions": ["leaderboard_submit", "analytics_opt_in"],
  "iat": 1234567890,
  "exp": 1234567890
}

// API Request Headers
{
  "Authorization": "Bearer {jwt_token}",
  "Content-Type": "application/json",
  "X-Game-Version": "v0.4.1",
  "X-Client-ID": "pdoom1-client"
}
```

## Security Architecture

### Privacy-First Design Principles

1. **Data Minimization**: Collect only essential data for functionality
2. **Pseudonymization**: No real names or identifiable information stored
3. **Opt-in Systems**: All data collection requires explicit user consent
4. **Retention Limits**: Automatic deletion of analytics data after 90 days
5. **Encryption**: All data encrypted in transit and at rest
6. **Access Control**: Granular permissions and audit logging

### Security Implementation

```yaml
# Security Configuration
security:
  encryption:
    database: AES-256-GCM
    transit: TLS 1.3
    api_keys: bcrypt with salt
  
  authentication:
    method: JWT + refresh tokens
    expiry: 24 hours (access), 7 days (refresh)
    rotation: Automatic key rotation every 90 days
  
  api_protection:
    rate_limiting: 100 req/min per user
    ddos_protection: Cloudflare
    input_validation: JSON schema validation
    sql_injection: Parameterized queries only
  
  audit:
    all_api_calls: Logged with IP, user, timestamp
    admin_actions: Full audit trail
    retention: 1 year for security logs
```

### GDPR & Privacy Compliance

```
Privacy Compliance Checklist:

✅ Right to Access: Users can export all their data
✅ Right to Rectification: Users can update their information
✅ Right to Erasure: Complete account deletion available
✅ Right to Portability: JSON export of user data
✅ Privacy by Design: Default settings protect privacy
✅ Consent Management: Granular opt-in/opt-out controls
✅ Data Processing Lawfulness: Clear legal basis for processing
✅ Data Protection Impact Assessment: Regular privacy audits
```

## Implementation Roadmap

### Phase 1: Foundation (Weeks 1-3)
**Objective**: Set up core infrastructure and database

**Tasks**:
- [ ] Create `pdoom1-data` repository
- [ ] Set up PostgreSQL database (managed service)
- [ ] Implement basic API gateway with authentication
- [ ] Create database schema and migrations
- [ ] Set up CI/CD pipeline for data repository
- [ ] Implement basic security middleware

**Deliverables**:
- Working API with user registration/authentication
- Database with core tables operational
- Basic security and monitoring in place

### Phase 2: Leaderboard Integration (Weeks 4-6)
**Objective**: Replace local-only leaderboards with hybrid local/remote system

**Tasks**:
- [ ] Implement leaderboard API endpoints
- [ ] Update game client to sync with remote API
- [ ] Create privacy-respecting submission system
- [ ] Implement anti-cheat verification
- [ ] Add rank calculation and caching
- [ ] Create leaderboard sync workers

**Deliverables**:
- Players can submit scores to global leaderboards
- Seed-specific competitions work remotely
- Privacy controls fully functional

### Phase 3: Website Integration (Weeks 7-9)
**Objective**: Connect website to data repository for dynamic content

**Tasks**:
- [ ] Implement content management API
- [ ] Update website to fetch dynamic leaderboards
- [ ] Create blog content sync endpoints
- [ ] Add community features (challenges, rankings)
- [ ] Implement real-time updates
- [ ] Add social features (sharing, achievements)

**Deliverables**:
- Website displays live leaderboards
- Community challenges automated
- Blog content flows through all repositories

### Phase 4: Analytics & Optimization (Weeks 10-12)
**Objective**: Add privacy-respecting analytics and performance optimization

**Tasks**:
- [ ] Implement analytics collection system
- [ ] Create privacy dashboard for users
- [ ] Add performance monitoring
- [ ] Implement data retention policies
- [ ] Create admin dashboard
- [ ] Add automated backups and disaster recovery

**Deliverables**:
- Complete ecosystem with analytics
- Admin tools for system management
- Full compliance with privacy regulations

## Repository Structure: pdoom1-data

```
pdoom1-data/
├── api/                      # API Gateway & Endpoints
│   ├── auth/                # Authentication handlers
│   ├── leaderboards/        # Leaderboard API
│   ├── content/             # Content management API
│   ├── analytics/           # Analytics API
│   └── middleware/          # Security & validation middleware
├── database/
│   ├── migrations/          # Database schema migrations
│   ├── seeds/              # Test data and fixtures
│   └── models/             # Database models and ORM
├── services/
│   ├── sync/               # Data synchronization services
│   ├── cache/              # Redis caching layer
│   ├── queue/              # Background job processing
│   └── notifications/      # Email/webhook notifications
├── workers/
│   ├── leaderboard_calc/   # Rank calculation worker
│   ├── content_sync/       # Cross-repo sync worker
│   └── cleanup/            # Privacy compliance cleanup
├── config/
│   ├── database.yml        # Database configuration
│   ├── security.yml        # Security settings
│   └── privacy.yml         # Privacy policy settings
├── tests/
│   ├── api/                # API endpoint tests
│   ├── integration/        # Cross-service integration tests
│   └── security/           # Security & privacy tests
├── docs/
│   ├── API.md              # API documentation
│   ├── DEPLOYMENT.md       # Deployment guide
│   └── PRIVACY.md          # Privacy policy documentation
├── scripts/
│   ├── setup.sh           # Environment setup
│   ├── migrate.sh         # Database migration runner
│   └── backup.sh          # Backup procedures
├── .github/
│   └── workflows/         # CI/CD workflows
├── docker-compose.yml     # Local development setup
├── Dockerfile            # Production container
└── README.md             # Repository documentation
```

## Deployment Architecture

### Production Environment

```yaml
# Production Infrastructure (Docker + Cloud)
services:
  api_gateway:
    image: pdoom1-data:latest
    replicas: 3
    environment:
      - DATABASE_URL=${DATABASE_URL}
      - REDIS_URL=${REDIS_URL}
      - JWT_SECRET=${JWT_SECRET}
    
  database:
    provider: PostgreSQL (managed service)
    version: 15
    size: Standard tier with automated backups
    
  cache:
    provider: Redis (managed service)
    memory: 1GB
    persistence: enabled
    
  monitoring:
    provider: Application monitoring service
    metrics: API response times, error rates, user activity
    alerts: Email + Discord webhooks
```

### Security Considerations

1. **Network Security**:
   - API Gateway behind CDN/Load Balancer
   - Database in private network
   - VPC with security groups

2. **Application Security**:
   - Input validation on all endpoints
   - SQL injection prevention
   - Rate limiting per user/IP
   - CORS configuration

3. **Data Security**:
   - Encryption at rest and in transit
   - Regular security audits
   - Automated vulnerability scanning
   - Backup encryption

## Cross-Repository Coordination

### Workflow Integration

```yaml
# Enhanced GitHub Actions for Multi-Repo Coordination
name: Multi-Repo Sync
on:
  push:
    branches: [main]
  schedule:
    - cron: '0 */6 * * *'  # Every 6 hours

jobs:
  sync_game_to_data:
    runs-on: ubuntu-latest
    steps:
      - name: Sync leaderboard updates
        uses: ./.github/actions/sync-leaderboards
        with:
          api_endpoint: ${{ secrets.DATA_API_ENDPOINT }}
          api_key: ${{ secrets.DATA_API_KEY }}
          
  sync_data_to_website:
    runs-on: ubuntu-latest
    needs: sync_game_to_data
    steps:
      - name: Update website leaderboards
        uses: ./.github/actions/sync-website-content
        with:
          website_repo: PipFoweraker/pdoom1-website
          data_api: ${{ secrets.DATA_API_ENDPOINT }}
```

### Communication Patterns

1. **Game → Data**: Real-time score submission, privacy settings sync
2. **Data → Website**: Periodic leaderboard updates, new blog content
3. **Website → Data**: User registration, privacy setting changes
4. **Data → Game**: Weekly challenge notifications, version updates

## Risk Mitigation & Monitoring

### Operational Risks

| Risk | Impact | Mitigation | Monitoring |
|------|--------|------------|------------|
| Database downtime | High | Automated failover, read replicas | 99.9% uptime SLA |
| API overload | Medium | Rate limiting, horizontal scaling | Response time alerts |
| Data breach | Critical | Encryption, access controls, auditing | Security monitoring |
| Privacy violation | Critical | GDPR compliance, data minimization | Privacy audit trail |
| Cross-repo sync failure | Medium | Retry logic, manual override | Sync status dashboard |

### Compliance Monitoring

```
Automated Compliance Checks:
- Daily: GDPR compliance verification
- Weekly: Security vulnerability scan
- Monthly: Privacy policy compliance audit
- Quarterly: Full penetration testing
```

## Success Metrics

### Technical Metrics
- **API Performance**: <200ms average response time
- **Uptime**: 99.9% availability
- **Security**: Zero data breaches, regular security audits passed
- **Privacy**: 100% GDPR compliance score

### User Engagement Metrics
- **Leaderboard Participation**: >50% of active players opt-in
- **Community Challenges**: Weekly participation growth
- **Website Engagement**: Increased blog views and community interaction
- **Privacy Satisfaction**: High user satisfaction with privacy controls

## Next Steps

### Immediate Actions (This Week)
1. **Repository Setup**: Create `pdoom1-data` repository with basic structure
2. **Database Design**: Finalize schema and create migration scripts
3. **Security Planning**: Define authentication system architecture
4. **Team Coordination**: Establish development workflow for multi-repo work

### Implementation Priority
1. **High Priority**: User authentication, basic leaderboard API
2. **Medium Priority**: Website integration, weekly challenges
3. **Low Priority**: Advanced analytics, admin dashboard

---

## Conclusion

This comprehensive integration plan provides a secure, scalable foundation for the P(Doom) ecosystem. By implementing this architecture, you'll achieve:

- **Seamless Coordination**: All three repositories working in harmony
- **Privacy Excellence**: GDPR-compliant, user-respecting data handling
- **Community Growth**: Competitive features that drive engagement
- **Technical Excellence**: Modern, maintainable, and secure infrastructure
- **Future-Proof Design**: Architecture that scales with community growth

The phased approach ensures manageable implementation while building toward a world-class gaming ecosystem that respects privacy and fosters community.

**Ready to begin implementation? Start with Phase 1: Foundation setup.**
