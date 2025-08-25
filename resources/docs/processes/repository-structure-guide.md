# Focus Flow - Repository Structure Guide

**Purpose**: This document provides comprehensive guidance for organizing the Focus Flow productivity game codebase, establishing clear file placement standards and architectural boundaries for enterprise-grade development patterns.

_Version: 1.0_  
_Created: January 25, 2025_  
_Status: Initial Setup Phase_

---

## 📋 Quick Reference - File Placement Guide

| **Action**                     | **Location**                              | **Purpose**                  |
| ------------------------------ | ----------------------------------------- | ---------------------------- |
| **Add focus session model**    | `services/focus_engine/models/`           | Database and API models      |
| **Add React component**        | `ui/focus_app/src/components/{category}/` | UI components by feature     |
| **Add API endpoint**           | `services/focus_engine/routers/`          | REST API routes              |
| **Add shared utility**         | `shared/focus_shared/`                    | Cross-service utilities      |
| **Add AI insight logic**       | `services/ai_insights/`                   | AI coaching and analysis     |
| **Add music integration**      | `services/music_control/`                 | YouTube Music API client     |
| **Add custom hook**            | `ui/focus_app/src/hooks/`                 | React state management       |
| **Add database migration**     | `database/migrations/`                    | Schema changes               |
| **Add animation component**    | `ui/focus_app/src/components/animations/` | Visual feedback              |
| **Add productivity analytics** | `services/analytics/`                     | Session data analysis        |
| **Add gamification logic**     | `services/game_engine/`                   | Achievements and progress    |
| **Add configuration**          | `config/`                                 | Environment and app settings |
| **Add documentation**          | `docs/{category}/`                        | Technical and user guides    |
| **Add tests**                  | `tests/{category}/`                       | Testing suites               |

---

## 🏗️ Complete Repository Structure

### **Root Level Organization**

```
focus-flow/
├── 📁 services/                        # Microservices architecture
├── 📁 ui/                             # Frontend applications
├── 📁 shared/                         # Shared libraries and utilities
├── 📁 database/                       # Database management
├── 📁 config/                         # Configuration management
├── 📁 infrastructure/                 # Deployment and DevOps
├── 📁 docs/                          # Documentation
├── 📁 tests/                         # Testing infrastructure
├── 📁 scripts/                       # Development and deployment scripts
├── 📁 assets/                        # Static assets and media
├── 📁 examples/                      # Usage examples and demos
├── 📁 logs/                          # Application logs
├── 📁 build/                         # Build artifacts
├── 📁 dist/                          # Distribution packages
├── 📄 docker-compose.yml             # Local development orchestration
├── 📄 docker-compose.prod.yml        # Production orchestration
├── 📄 .env.example                   # Environment template
├── 📄 .gitignore                     # Git ignore patterns
├── 📄 README.md                      # Project overview
├── 📄 CONTRIBUTING.md                # Development guidelines
├── 📄 LICENSE                        # Project license
└── 📄 package.json                   # Project metadata
```

---

## 🎯 **Core Services Architecture**

### **`/services/` - Microservices Implementation**

#### **Focus Engine Service** - Core timer and session management

```
services/focus_engine/
├── 📄 main.py                        # FastAPI application entry point
├── 📄 Dockerfile                     # Service containerization
├── 📄 requirements.txt               # Python dependencies
├── 📄 .env.example                   # Service environment template
├── 📁 models/                        # Pydantic and SQLModel data models
│   ├── 📄 __init__.py
│   ├── 📄 session_models.py          # Focus session data structures
│   ├── 📄 user_models.py             # User profile and preferences
│   ├── 📄 base_models.py             # Shared base model classes
│   └── 📄 response_models.py         # API response schemas
├── 📁 routers/                       # FastAPI route handlers
│   ├── 📄 __init__.py
│   ├── 📄 sessions.py                # Session CRUD operations
│   ├── 📄 health.py                  # Service health checks
│   └── 📄 websockets.py              # Real-time session updates
├── 📁 services/                      # Business logic layer
│   ├── 📄 __init__.py
│   ├── 📄 session_service.py         # Session management logic
│   ├── 📄 timer_service.py           # Timer calculation and control
│   └── 📄 notification_service.py    # Break and completion notifications
├── 📁 database/                      # Database operations
│   ├── 📄 __init__.py
│   ├── 📄 connection.py              # Database connection management
│   ├── 📄 repositories.py            # Data access layer
│   └── 📄 session_repository.py      # Session-specific queries
├── 📁 config/                        # Service configuration
│   ├── 📄 __init__.py
│   ├── 📄 settings.py                # Environment-driven configuration
│   └── 📄 logging_config.py          # Centralized logging setup
└── 📁 utils/                         # Service utilities
    ├── 📄 __init__.py
    ├── 📄 time_calculations.py       # Time formatting and calculations
    └── 📄 validators.py               # Input validation helpers
```

#### **AI Insights Service** - Productivity coaching and analysis

```
services/ai_insights/
├── 📄 main.py                        # AI insights API entry point
├── 📄 Dockerfile                     # Service containerization
├── 📄 requirements.txt               # AI/ML dependencies
├── 📁 models/                        # AI data models
│   ├── 📄 insights_models.py         # AI coaching data structures
│   ├── 📄 analysis_models.py         # Statistical analysis models
│   └── 📄 pattern_models.py          # Productivity pattern definitions
├── 📁 routers/                       # AI insights endpoints
│   ├── 📄 insights.py                # Session analysis endpoints
│   ├── 📄 patterns.py                # Productivity pattern discovery
│   └── 📄 coaching.py                # AI coaching recommendations
├── 📁 clients/                       # AI service integrations
│   ├── 📄 openai_client.py           # OpenAI API integration
│   ├── 📄 ollama_client.py           # Local LLM integration
│   └── 📄 analysis_client.py         # Statistical analysis client
├── 📁 services/                      # AI business logic
│   ├── 📄 session_analyzer.py        # Individual session analysis
│   ├── 📄 pattern_discoverer.py      # Multi-session pattern recognition
│   ├── 📄 coaching_generator.py      # Personalized coaching insights
│   └── 📄 correlation_engine.py      # Statistical correlation analysis
├── 📁 prompts/                       # LLM prompt templates
│   ├── 📄 session_analysis.txt       # Session insight prompts
│   ├── 📄 productivity_coaching.txt  # Coaching recommendation prompts
│   └── 📄 pattern_interpretation.txt # Pattern analysis prompts
└── 📁 config/                        # AI service configuration
    ├── 📄 ai_settings.py             # AI model configuration
    └── 📄 prompt_config.py           # Prompt template management
```

#### **Music Control Service** - YouTube Music integration

```
services/music_control/
├── 📄 main.py                        # Music control API entry point
├── 📄 Dockerfile                     # Service containerization
├── 📄 requirements.txt               # Music API dependencies
├── 📁 models/                        # Music data models
│   ├── 📄 playlist_models.py         # Playlist data structures
│   ├── 📄 track_models.py            # Track information models
│   └── 📄 session_music_models.py    # Music session correlation
├── 📁 routers/                       # Music control endpoints
│   ├── 📄 playlists.py               # Playlist management endpoints
│   ├── 📄 playback.py                # Playback control endpoints
│   └── 📄 discovery.py               # Focus playlist discovery
├── 📁 clients/                       # External music service clients
│   ├── 📄 youtube_music_client.py    # YouTube Music API client
│   ├── 📄 spotify_client.py          # Alternative Spotify integration
│   └── 📄 browser_control_client.py  # Browser-based playback control
├── 📁 services/                      # Music business logic
│   ├── 📄 playlist_service.py        # Playlist management logic
│   ├── 📄 focus_detection.py         # Focus-suitable playlist detection
│   └── 📄 effectiveness_tracker.py   # Music effectiveness analysis
└── 📁 utils/                         # Music utilities
    ├── 📄 playlist_analyzer.py       # Playlist content analysis
    └── 📄 genre_classifier.py        # Music genre classification
```

#### **Analytics Service** - Productivity data analysis

```
services/analytics/
├── 📄 main.py                        # Analytics API entry point
├── 📄 Dockerfile                     # Service containerization
├── 📄 requirements.txt               # Analytics dependencies
├── 📁 models/                        # Analytics data models
│   ├── 📄 metrics_models.py          # Productivity metrics definitions
│   ├── 📄 trend_models.py            # Trend analysis structures
│   └── 📄 comparison_models.py       # Comparative analysis models
├── 📁 routers/                       # Analytics endpoints
│   ├── 📄 metrics.py                 # Productivity metrics endpoints
│   ├── 📄 trends.py                  # Trend analysis endpoints
│   ├── 📄 comparisons.py             # Comparative analytics endpoints
│   └── 📄 export.py                  # Data export functionality
├── 📁 services/                      # Analytics business logic
│   ├── 📄 metrics_calculator.py      # Productivity metrics calculation
│   ├── 📄 trend_analyzer.py          # Trend analysis and forecasting
│   ├── 📄 comparative_analyzer.py    # Comparative performance analysis
│   └── 📄 export_service.py          # Data export service
└── 📁 processors/                    # Data processing engines
    ├── 📄 session_aggregator.py      # Session data aggregation
    ├── 📄 time_series_processor.py   # Time series data processing
    └── 📄 correlation_processor.py   # Cross-metric correlation analysis
```

#### **Game Engine Service** - Gamification and achievements

```
services/game_engine/
├── 📄 main.py                        # Game engine API entry point
├── 📄 Dockerfile                     # Service containerization
├── 📄 requirements.txt               # Gamification dependencies
├── 📁 models/                        # Game data models
│   ├── 📄 achievement_models.py      # Achievement definitions and progress
│   ├── 📄 streak_models.py           # Streak tracking structures
│   ├── 📄 level_models.py            # Level progression models
│   └── 📄 reward_models.py           # Reward and experience models
├── 📁 routers/                       # Gamification endpoints
│   ├── 📄 achievements.py            # Achievement tracking endpoints
│   ├── 📄 streaks.py                 # Streak management endpoints
│   ├── 📄 levels.py                  # Level progression endpoints
│   └── 📄 leaderboards.py            # Future social features
├── 📁 services/                      # Game logic services
│   ├── 📄 achievement_service.py     # Achievement logic and unlocking
│   ├── 📄 streak_service.py          # Streak calculation and maintenance
│   ├── 📄 level_service.py           # Level progression calculation
│   └── 📄 experience_service.py      # Experience point calculation
├── 📁 achievements/                  # Achievement definitions
│   ├── 📄 base_achievements.py       # Core achievement templates
│   ├── 📄 focus_achievements.py      # Focus-related achievements
│   ├── 📄 streak_achievements.py     # Streak-based achievements
│   └── 📄 milestone_achievements.py  # Major milestone achievements
└── 📁 calculators/                   # Game calculation engines
    ├── 📄 experience_calculator.py   # Experience point calculations
    ├── 📄 streak_calculator.py       # Streak maintenance calculations
    └── 📄 difficulty_calculator.py   # Adaptive difficulty adjustment
```

---

## 🎨 **Frontend Application Architecture**

### **`/ui/focus_app/` - React Frontend Application**

#### **Core Application Structure**

```
ui/focus_app/
├── 📄 package.json                   # Frontend dependencies and scripts
├── 📄 tsconfig.json                  # TypeScript configuration
├── 📄 tailwind.config.js             # Tailwind CSS configuration
├── 📄 vite.config.ts                 # Vite build configuration
├── 📄 Dockerfile                     # Frontend containerization
├── 📄 .env.example                   # Frontend environment template
├── 📁 public/                        # Static assets
│   ├── 📄 index.html                 # Application entry point
│   ├── 📄 favicon.ico                # Application favicon
│   ├── 📁 sounds/                    # Notification sounds
│   │   ├── 📄 session_complete.mp3
│   │   ├── 📄 break_start.mp3
│   │   └── 📄 gentle_reminder.mp3
│   └── 📁 images/                    # Static images and icons
├── 📁 src/                           # Source code
│   ├── 📄 main.tsx                   # React application entry point
│   ├── 📄 App.tsx                    # Main application component
│   ├── 📄 index.css                  # Global styles and Tailwind imports
│   └── 📁 components/                # React components (detailed below)
└── 📁 dist/                          # Build output directory
```

#### **Component Architecture**

```
ui/focus_app/src/components/
├── 📁 focus/                         # Focus session components
│   ├── 📄 FocusTimer.tsx             # Main timer display component
│   ├── 📄 SessionControls.tsx        # Start/pause/stop controls
│   ├── 📄 ProgressRing.tsx           # Animated circular progress
│   ├── 📄 TimeDisplay.tsx            # Time formatting display
│   ├── 📄 SessionStatus.tsx          # Current session status
│   └── 📄 InterruptionTracker.tsx    # Interruption logging component
├── 📁 music/                         # Music integration components
│   ├── 📄 PlaylistSelector.tsx       # YouTube Music playlist picker
│   ├── 📄 MusicControls.tsx          # Play/pause/skip controls
│   ├── 📄 PlaylistBrowser.tsx        # Browse available playlists
│   ├── 📄 NowPlaying.tsx             # Current track display
│   └── 📄 MusicSettingsPanel.tsx     # Music preferences
├── 📁 insights/                      # AI insights and analytics
│   ├── 📄 SessionSummary.tsx         # Post-session AI insights
│   ├── 📄 ProductivityChart.tsx      # Focus analytics visualization
│   ├── 📄 AICoachingPanel.tsx        # AI-powered productivity tips
│   ├── 📄 PatternAnalysis.tsx        # Productivity pattern display
│   ├── 📄 TrendVisualization.tsx     # Long-term trend charts
│   └── 📄 InsightsLoading.tsx        # Loading states for AI analysis
├── 📁 animations/                    # Visual feedback and animations
│   ├── 📄 FocusVisualizer.tsx        # Focus session background animation
│   ├── 📄 BreakModeVisualizer.tsx    # Break period animations
│   ├── 📄 ProgressAnimations.tsx     # Animated progress indicators
│   ├── 📄 AchievementPopup.tsx       # Achievement unlock animations
│   └── 📄 TransitionEffects.tsx      # Screen transition animations
├── 📁 game/                          # Gamification components
│   ├── 📄 AchievementBadge.tsx       # Individual achievement display
│   ├── 📄 AchievementGallery.tsx     # All achievements overview
│   ├── 📄 StreakTracker.tsx          # Streak display and progress
│   ├── 📄 LevelProgress.tsx          # Level progression display
│   ├── 📄 ExperienceBar.tsx          # Experience points visualization
│   └── 📄 RewardNotification.tsx     # Reward unlock notifications
├── 📁 analytics/                     # Analytics and dashboard components
│   ├── 📄 DashboardOverview.tsx      # Main analytics dashboard
│   ├── 📄 FocusMetrics.tsx           # Focus effectiveness metrics
│   ├── 📄 TimeAnalysis.tsx           # Time-based analysis charts
│   ├── 📄 ProductivityHeatmap.tsx    # Time-of-day effectiveness heatmap
│   ├── 📄 SessionHistory.tsx         # Historical session data
│   └── 📄 ExportControls.tsx         # Data export functionality
├── 📁 settings/                      # Application settings
│   ├── 📄 UserPreferences.tsx        # General user preferences
│   ├── 📄 SessionSettings.tsx        # Focus session configuration
│   ├── 📄 NotificationSettings.tsx   # Notification preferences
│   ├── 📄 MusicPreferences.tsx       # Music integration settings
│   └── 📄 PrivacySettings.tsx        # Data and privacy controls
├── 📁 layout/                        # Layout and navigation components
│   ├── 📄 AppHeader.tsx              # Application header navigation
│   ├── 📄 Sidebar.tsx                # Main navigation sidebar
│   ├── 📄 MainContent.tsx            # Content area wrapper
│   ├── 📄 Footer.tsx                 # Application footer
│   └── 📄 NavigationTabs.tsx         # Tab-based navigation
├── 📁 common/                        # Shared UI components
│   ├── 📄 Button.tsx                 # Standardized button component
│   ├── 📄 Modal.tsx                  # Modal dialog component
│   ├── 📄 LoadingSpinner.tsx         # Loading indicator
│   ├── 📄 ErrorBoundary.tsx          # Error handling component
│   ├── 📄 Tooltip.tsx                # Tooltip component
│   └── 📄 ConfirmationDialog.tsx     # Confirmation modal
└── 📁 forms/                         # Form components
    ├── 📄 SessionStartForm.tsx       # Session configuration form
    ├── 📄 InterruptionLogForm.tsx    # Interruption logging form
    ├── 📄 FeedbackForm.tsx           # Session feedback form
    └── 📄 FormControls.tsx           # Reusable form controls
```

#### **Services and State Management**

```
ui/focus_app/src/
├── 📁 services/                      # API client services
│   ├── 📄 apiClient.ts               # Base API client configuration
│   ├── 📄 focusSessionService.ts     # Focus session API operations
│   ├── 📄 musicService.ts            # Music control API operations
│   ├── 📄 insightsService.ts         # AI insights API operations
│   ├── 📄 analyticsService.ts        # Analytics API operations
│   ├── 📄 gameService.ts             # Gamification API operations
│   └── 📄 websocketService.ts        # Real-time updates service
├── 📁 hooks/                         # Custom React hooks
│   ├── 📄 useFocusSession.ts         # Focus session state management
│   ├── 📄 useMusicControl.ts         # Music playback control
│   ├── 📄 useProductivityInsights.ts # AI insights integration
│   ├── 📄 useGameProgress.ts         # Achievement and level tracking
│   ├── 📄 useAnalytics.ts            # Productivity analytics
│   ├── 📄 useNotifications.ts        # Browser notification management
│   ├── 📄 useLocalStorage.ts         # Local storage management
│   └── 📄 useWebSocket.ts            # WebSocket connection management
├── 📁 context/                       # React context providers
│   ├── 📄 AppContext.tsx             # Global application state
│   ├── 📄 AuthContext.tsx            # User authentication state
│   ├── 📄 ThemeContext.tsx           # UI theme management
│   └── 📄 NotificationContext.tsx    # Notification system state
├── 📁 types/                         # TypeScript type definitions
│   ├── 📄 focus.ts                   # Focus session interfaces
│   ├── 📄 music.ts                   # Music integration types
│   ├── 📄 insights.ts                # AI insights interfaces
│   ├── 📄 analytics.ts               # Analytics data types
│   ├── 📄 game.ts                    # Gamification interfaces
│   ├── 📄 api.ts                     # API response types
│   └── 📄 common.ts                  # Shared type definitions
├── 📁 utils/                         # Utility functions
│   ├── 📄 timeFormatters.ts          # Time display formatting
│   ├── 📄 sessionCalculations.ts     # Focus session calculations
│   ├── 📄 animationHelpers.ts        # Animation control utilities
│   ├── 📄 chartHelpers.ts            # Data visualization utilities
│   ├── 📄 validationHelpers.ts       # Form validation utilities
│   └── 📄 constants.ts               # Application constants
└── 📁 styles/                        # Styling resources
    ├── 📄 animations.css             # Custom animation definitions
    ├── 📄 components.css             # Component-specific styles
    ├── 📄 themes.css                 # Theme definitions
    └── 📄 utilities.css              # Custom utility classes
```

---

## 📚 **Shared Libraries Architecture**

### **`/shared/focus_shared/` - Cross-Service Utilities**

```
shared/focus_shared/
├── 📄 setup.py                       # Package installation configuration
├── 📄 __init__.py                    # Package initialization
├── 📄 requirements.txt               # Shared library dependencies
├── 📁 models/                        # Shared data models
│   ├── 📄 __init__.py
│   ├── 📄 base_models.py             # Base model classes
│   ├── 📄 session_models.py          # Shared session models
│   ├── 📄 user_models.py             # User-related models
│   └── 📄 response_models.py         # Standard API response models
├── 📁 utils/                         # Cross-service utilities
│   ├── 📄 __init__.py
│   ├── 📄 time_utils.py              # Time calculation utilities
│   ├── 📄 validation_utils.py        # Data validation helpers
│   ├── 📄 logging_utils.py           # Centralized logging utilities
│   └── 📄 config_utils.py            # Configuration management
├── 📁 constants/                     # Application constants
│   ├── 📄 __init__.py
│   ├── 📄 session_constants.py       # Focus session constants
│   ├── 📄 achievement_constants.py   # Gamification constants
│   └── 📄 api_constants.py           # API-related constants
├── 📁 exceptions/                    # Custom exception classes
│   ├── 📄 __init__.py
│   ├── 📄 session_exceptions.py      # Session-related exceptions
│   ├── 📄 music_exceptions.py        # Music integration exceptions
│   └── 📄 api_exceptions.py          # API-related exceptions
└── 📁 types/                         # Shared type definitions
    ├── 📄 __init__.py
    ├── 📄 session_types.py           # Session-related types
    ├── 📄 music_types.py             # Music integration types
    └── 📄 api_types.py               # API-related types
```

---

## 🗄️ **Database Management**

### **`/database/` - Database Schema and Management**

```
database/
├── 📄 init.sql                       # Initial database setup
├── 📄 schema.sql                     # Complete database schema
├── 📄 seed_data.sql                  # Development seed data
├── 📁 migrations/                    # Database schema migrations
│   ├── 📄 001_initial_schema.sql     # Initial tables creation
│   ├── 📄 002_add_music_integration.sql # Music-related tables
│   ├── 📄 003_add_ai_insights.sql    # AI insights storage
│   ├── 📄 004_add_gamification.sql   # Achievement and streak tables
│   └── 📄 005_add_analytics_views.sql # Analytics views and indexes
├── 📁 seeds/                         # Development and demo data
│   ├── 📄 demo_users.sql             # Demo user accounts
│   ├── 📄 sample_sessions.sql        # Sample focus sessions
│   ├── 📄 sample_playlists.sql       # Sample music playlists
│   └── 📄 achievement_definitions.sql # Achievement definitions
├── 📁 views/                         # Database views for analytics
│   ├── 📄 productivity_metrics.sql   # Productivity calculation views
│   ├── 📄 session_analytics.sql      # Session analysis views
│   └── 📄 user_progress.sql          # User progress tracking views
├── 📁 functions/                     # Database stored procedures
│   ├── 📄 session_calculations.sql   # Session metric calculations
│   ├── 📄 streak_maintenance.sql     # Streak calculation functions
│   └── 📄 achievement_checks.sql     # Achievement unlock logic
└── 📁 backups/                       # Database backup configurations
    ├── 📄 backup_script.sh           # Automated backup script
    └── 📄 restore_script.sh          # Database restore script
```

---

## ⚙️ **Configuration and Infrastructure**

### **`/config/` - Application Configuration**

```
config/
├── 📄 app.yml                        # Main application configuration
├── 📄 database.yml                   # Database configuration
├── 📄 redis.yml                      # Redis cache configuration
├── 📁 environments/                  # Environment-specific configs
│   ├── 📄 development.yml            # Development environment
│   ├── 📄 staging.yml                # Staging environment
│   ├── 📄 production.yml             # Production environment
│   └── 📄 testing.yml                # Testing environment
├── 📁 services/                      # Service-specific configurations
│   ├── 📄 focus_engine.yml           # Focus engine service config
│   ├── 📄 ai_insights.yml            # AI insights service config
│   ├── 📄 music_control.yml          # Music control service config
│   ├── 📄 analytics.yml              # Analytics service config
│   └── 📄 game_engine.yml            # Game engine service config
└── 📁 logging/                       # Logging configurations
    ├── 📄 development.yml             # Development logging
    ├── 📄 production.yml              # Production logging
    └── 📄 structured_logging.yml      # Structured logging format
```

### **`/infrastructure/` - Deployment and DevOps**

```
infrastructure/
├── 📁 docker/                        # Docker configurations
│   ├── 📄 docker-compose.yml         # Development orchestration
│   ├── 📄 docker-compose.prod.yml    # Production orchestration
│   ├── 📄 docker-compose.test.yml    # Testing orchestration
│   └── 📁 dockerfiles/               # Service-specific Dockerfiles
├── 📁 kubernetes/                    # Kubernetes manifests
│   ├── 📄 namespace.yaml             # Application namespace
│   ├── 📄 configmaps.yaml            # Configuration management
│   ├── 📄 secrets.yaml               # Secret management
│   ├── 📁 services/                  # Service deployments
│   └── 📁 ingress/                   # Ingress configurations
├── 📁 monitoring/                    # Monitoring and observability
│   ├── 📄 prometheus.yml             # Prometheus configuration
│   ├── 📄 grafana-dashboards.json    # Grafana dashboard definitions
│   ├── 📄 alertmanager.yml           # Alert management configuration
│   └── 📁 healthchecks/              # Service health check definitions
├── 📁 ci_cd/                         # CI/CD pipeline configurations
│   ├── 📄 .github_workflows.yml      # GitHub Actions workflows
│   ├── 📄 .gitlab-ci.yml             # GitLab CI configuration
│   └── 📄 jenkins_pipeline.groovy    # Jenkins pipeline definition
└── 📁 security/                      # Security configurations
    ├── 📄 network_policies.yaml      # Kubernetes network policies
    ├── 📄 rbac.yaml                  # Role-based access control
    └── 📄 security_policies.yaml     # Security policy definitions
```

---

## 📖 **Documentation Architecture**

### **`/docs/` - Comprehensive Documentation**

```
docs/
├── 📁 api/                           # API documentation
│   ├── 📄 focus_engine_api.md        # Focus engine API reference
│   ├── 📄 ai_insights_api.md         # AI insights API reference
│   ├── 📄 music_control_api.md       # Music control API reference
│   ├── 📄 analytics_api.md           # Analytics API reference
│   ├── 📄 game_engine_api.md         # Game engine API reference
│   └── 📄 websocket_api.md           # WebSocket API reference
├── 📁 architecture/                  # Architecture documentation
│   ├── 📄 system_overview.md         # High-level system architecture
│   ├── 📄 database_design.md         # Database schema documentation
│   ├── 📄 service_architecture.md    # Microservices architecture
│   ├── 📄 security_architecture.md   # Security design patterns
│   └── 📄 deployment_architecture.md # Deployment architecture
├── 📁 development/                   # Development guides
│   ├── 📄 getting_started.md         # Development environment setup
│   ├── 📄 coding_standards.md        # Code quality and style guidelines
│   ├── 📄 testing_guidelines.md      # Testing practices and standards
│   ├── 📄 debugging_guide.md         # Debugging and troubleshooting
│   └── 📄 contributing.md            # Contribution guidelines
├── 📁 user_guides/                   # End-user documentation
│   ├── 📄 user_manual.md             # Complete user manual
│   ├── 📄 getting_started_guide.md   # New user onboarding
│   ├── 📄 advanced_features.md       # Advanced feature usage
│   └── 📄 troubleshooting.md         # User troubleshooting guide
├── 📁 deployment/                    # Deployment documentation
│   ├── 📄 local_development.md       # Local development setup
│   ├── 📄 docker_deployment.md       # Docker deployment guide
│   ├── 📄 kubernetes_deployment.md   # Kubernetes deployment guide
│   └── 📄 production_deployment.md   # Production deployment checklist
└── 📁 design/                        # Design documentation
    ├── 📄 ui_design_system.md        # UI design system documentation
    ├── 📄 user_experience_guide.md   # UX design principles
    └── 📄 accessibility_guide.md     # Accessibility implementation
```

---

## 🧪 **Testing Infrastructure**

### **`/tests/` - Comprehensive Testing Suite**

```
tests/
├── 📁 unit/                          # Unit tests
│   ├── 📁 services/                  # Service unit tests
│   │   ├── 📄 test_focus_engine.py
│   │   ├── 📄 test_ai_insights.py
│   │   ├── 📄 test_music_control.py
│   │   ├── 📄 test_analytics.py
│   │   └── 📄 test_game_engine.py
│   ├── 📁 shared/                    # Shared library unit tests
│   │   ├── 📄 test_time_utils.py
│   │   ├── 📄 test_validation_utils.py
│   │   └── 📄 test_config_utils.py
│   └── 📁 frontend/                  # Frontend unit tests
│       ├── 📄 test_focus_timer.test.tsx
│       ├── 📄 test_music_controls.test.tsx
│       ├── 📄 test_insights_panel.test.tsx
│       └── 📄 test_game_components.test.tsx
├── 📁 integration/                   # Integration tests
│   ├── 📄 test_session_workflow.py   # End-to-end session testing
│   ├── 📄 test_music_integration.py  # Music service integration
│   ├── 📄 test_ai_integration.py     # AI insights integration
│   ├── 📄 test_database_operations.py # Database integration testing
│   └── 📄 test_api_integration.py    # API integration testing
├── 📁 e2e/                           # End-to-end tests
│   ├── 📄 test_complete_session.py   # Complete session workflow
│   ├── 📄 test_user_journey.py       # Full user journey testing
│   ├── 📄 test_gamification.py       # Achievement unlock testing
│   └── 📄 test_analytics_flow.py     # Analytics generation testing
├── 📁 performance/                   # Performance tests
│   ├── 📄 test_api_performance.py    # API response time testing
│   ├── 📄 test_database_performance.py # Database query performance
│   └── 📄 test_frontend_performance.py # Frontend performance testing
├── 📁 fixtures/                      # Test fixtures and data
│   ├── 📄 sample_sessions.json       # Sample session data
│   ├── 📄 sample_playlists.json      # Sample playlist data
│   ├── 📄 sample_users.json          # Sample user data
│   └── 📄 mock_responses.json        # Mock API responses
├── 📁 utils/                         # Testing utilities
│   ├── 📄 test_helpers.py            # Common test helper functions
│   ├── 📄 mock_services.py           # Service mocking utilities
│   └── 📄 data_generators.py         # Test data generation utilities
└── 📄 conftest.py                    # Pytest configuration and fixtures
```

---

## 🔧 **Development Tools and Scripts**

### **`/scripts/` - Development and Deployment Scripts**

```
scripts/
├── 📁 setup/                         # Environment setup scripts
│   ├── 📄 install_dependencies.sh    # Install all project dependencies
│   ├── 📄 setup_database.sh          # Database initialization
│   ├── 📄 setup_environment.sh       # Environment configuration
│   └── 📄 install_pre_commit.sh      # Pre-commit hooks setup
├── 📁 development/                   # Development workflow scripts
│   ├── 📄 start_dev_services.sh      # Start development services
│   ├── 📄 run_migrations.sh          # Database migration runner
│   ├── 📄 seed_test_data.sh          # Load test data into database
│   ├── 📄 lint_and_format.sh         # Code linting and formatting
│   └── 📄 run_tests.sh               # Test execution script
├── 📁 deployment/                    # Deployment scripts
│   ├── 📄 build_images.sh            # Docker image building
│   ├── 📄 deploy_staging.sh          # Staging deployment
│   ├── 📄 deploy_production.sh       # Production deployment
│   └── 📄 rollback_deployment.sh     # Deployment rollback
├── 📁 monitoring/                    # Monitoring and maintenance scripts
│   ├── 📄 health_check.sh            # Service health monitoring
│   ├── 📄 log_analysis.sh            # Log analysis and reporting
│   ├── 📄 performance_monitoring.sh  # Performance metric collection
│   └── 📄 backup_database.sh         # Database backup automation
└── 📁 utilities/                     # General utility scripts
    ├── 📄 generate_api_docs.sh       # API documentation generation
    ├── 📄 update_dependencies.sh     # Dependency update automation
    └── 📄 clean_build_artifacts.sh   # Build artifact cleanup
```

---

## 🎨 **Assets and Media**

### **`/assets/` - Static Assets and Media Resources**

```
assets/
├── 📁 images/                        # Image assets
│   ├── 📁 icons/                     # Application icons
│   │   ├── 📄 app_icon.svg
│   │   ├── 📄 timer_icon.svg
│   │   ├── 📄 music_icon.svg
│   │   └── 📄 achievement_icons/     # Achievement badge icons
│   ├── 📁 backgrounds/               # Background images and patterns
│   │   ├── 📄 focus_gradient.svg
│   │   ├── 📄 break_pattern.svg
│   │   └── 📄 dashboard_background.svg
│   └── 📁 branding/                  # Brand assets
│       ├── 📄 logo.svg
│       ├── 📄 logo_variations.svg
│       └── 📄 brand_guidelines.pdf
├── 📁 sounds/                        # Audio assets
│   ├── 📄 session_start.mp3          # Session start notification
│   ├── 📄 session_complete.mp3       # Session completion sound
│   ├── 📄 break_start.mp3            # Break period start sound
│   ├── 📄 achievement_unlock.mp3     # Achievement unlock sound
│   └── 📄 gentle_reminder.mp3        # Gentle notification sound
├── 📁 animations/                    # Animation assets
│   ├── 📄 focus_particles.json       # Lottie animation files
│   ├── 📄 break_animation.json
│   └── 📄 achievement_animation.json
└── 📁 fonts/                         # Custom font files
    ├── 📄 focus_display_font.woff2
    └── 📄 ui_font.woff2
```

---

## 📊 **Implementation Status & Architecture Highlights**

### 🚀 **Current Implementation Status**

**✅ Planning Phase Completed**:

- ✅ **Repository structure design** with enterprise patterns
- ✅ **Microservices architecture** with clear service boundaries
- ✅ **Database schema planning** with analytics optimization
- ✅ **Frontend component architecture** with React enterprise patterns
- ✅ **AI integration planning** with multiple LLM provider support
- ✅ **DevOps pipeline design** with comprehensive testing strategy

**🔄 Ready for Implementation**:

- 🔄 **Core focus engine service** implementation
- 🔄 **React frontend application** development
- 🔄 **YouTube Music integration** service
- 🔄 **AI insights generation** service
- 🔄 **Analytics and visualization** components
- 🔄 **Gamification engine** implementation

### 🏗️ **Architecture Highlights**

**Enterprise-Grade Features**:

- ✅ **Microservices architecture** with clear separation of concerns
- ✅ **Container-native deployment** with Docker and Kubernetes support
- ✅ **Comprehensive testing strategy** with unit, integration, and E2E tests
- ✅ **Real-time updates** with WebSocket integration
- ✅ **AI-powered insights** with multiple LLM provider support
- ✅ **External API integration** with YouTube Music
- ✅ **Performance monitoring** with metrics and observability
- ✅ **Scalable database design** optimized for analytics and time-series data

**Development Experience Features**:

- ✅ **Type-safe development** with TypeScript across frontend and backend
- ✅ **Automated code quality** with linting, formatting, and pre-commit hooks
- ✅ **Comprehensive documentation** with API references and user guides
- ✅ **Development workflow automation** with scripts and tooling
- ✅ **Environment management** with configuration as code
- ✅ **Shared libraries** for consistent patterns across services

**User Experience Features**:

- ✅ **Responsive design** optimized for desktop and mobile devices
- ✅ **Accessibility compliance** with WCAG guidelines
- ✅ **Progressive web app** capabilities for offline functionality
- ✅ **Gamification elements** to encourage consistent usage
- ✅ **Personalized AI coaching** based on individual usage patterns
- ✅ **Music integration** for enhanced focus experience

---

## 📚 **Essential Documentation References**

### **Architecture Documentation**

- **[Focus Flow LLM Project Knowledge Base](../docs/ai/focus_flow_llm_project_knowledgebase.md)** - Complete project context and technical specifications
- **[System Architecture Overview](../docs/architecture/system_overview.md)** - High-level system design and component interaction
- **[Database Design Documentation](../docs/architecture/database_design.md)** - Database schema and optimization strategies

### **Development Guidelines**

- **[Getting Started Guide](../docs/development/getting_started.md)** - Development environment setup and first steps
- **[Coding Standards](../docs/development/coding_standards.md)** - Code quality guidelines and best practices
- **[Testing Guidelines](../docs/development/testing_guidelines.md)** - Testing strategies and implementation patterns

### **API References**

- **[Focus Engine API](../docs/api/focus_engine_api.md)** - Focus session management endpoints
- **[AI Insights API](../docs/api/ai_insights_api.md)** - AI coaching and analysis endpoints
- **[Music Control API](../docs/api/music_control_api.md)** - YouTube Music integration endpoints

### **Deployment Documentation**

- **[Local Development Setup](../docs/deployment/local_development.md)** - Local environment configuration
- **[Docker Deployment Guide](../docs/deployment/docker_deployment.md)** - Containerized deployment instructions
- **[Production Deployment](../docs/deployment/production_deployment.md)** - Production deployment checklist and procedures

---

**This repository structure supports**:

- ✅ **Rapid MVP development** with two-week implementation timeline
- ✅ **Enterprise scalability** with microservices and container architecture
- ✅ **AI-powered insights** with multiple LLM integration patterns
- ✅ **External service integration** with YouTube Music API
- ✅ **Comprehensive testing** with unit, integration, and E2E coverage
- ✅ **Production-ready deployment** with monitoring and observability
- ✅ **Developer experience optimization** with tooling and automation
- ✅ **User experience excellence** with responsive design and accessibility

For questions about file placement, architectural decisions, or implementation patterns, refer to this guide and the comprehensive documentation in the `/docs/` directory.
