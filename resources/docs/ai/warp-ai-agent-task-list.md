# Focus Flow Productivity Game - Warp Agent Task List

**Project**: Focus Flow Interactive Productivity Timer  
**Phase**: Initial Development & Core Component Setup  
**Target**: Functional MVP with Focus Timer, Music Integration, and AI Insights  
**Date**: January 2025

## Project Overview: Focus Flow

The **Focus Flow** project is an interactive, gamified Pomodoro timer that combines enterprise-grade React patterns with AI-powered productivity insights, featuring YouTube Music integration for focus playlists and animated visual feedback to help users maintain optimal focus cycles.

### Project Goals

- **Technology Showcase**: Demonstrate React/FastAPI enterprise patterns from SSLLC Structure
- **AI Integration**: Apply AI insights and analytics patterns from Data Centralization Platform
- **Rapid MVP Development**: Complete functional application in 2-week development cycle
- **External API Integration**: YouTube Music API for enhanced user experience

### Naming Convention Standards

- **Project Name**: "focus-flow" (lowercase with hyphen)
- **Repository Name**: `focus-flow_DEMO`
- **Container Names**: `focus-flow-[service]` (e.g., `focus-flow-api`, `focus-flow-frontend`)
- **Package Names**: `focus_shared`, `focus_analytics`
- **Database Names**: `focus_flow_db`, `focus_analytics_db`
- **Environment Variables**: `FOCUS_FLOW_*` prefix
- **API Endpoints**: `/api/v1/[resource]`

---

## 🚀 Repository Setup Tasks

### Task Group A: Initial Repository Creation

#### **Task A1: Create Local Repository Structure**

**Overview**: Establish the complete repository structure following the enterprise patterns defined in the Focus Flow Repository Structure Guide.

**Detailed Breakdown**:

##### **A1.1: Initialize Git Repository and Base Structure**

**Command Sequence**:

```bash
# Create the root project directory
mkdir focus-flow
cd focus-flow

# Initialize git repository
git init
echo "# Focus Flow - Interactive Productivity Timer" > README.md

# Create base directory structure
mkdir -p {services,ui,shared,database,config,infrastructure,docs,tests,scripts,assets,examples,logs,build,dist}

# Create .gitignore for the project
cat > .gitignore << 'EOF'
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
share/python-wheels/
*.egg-info/
.installed.cfg
*.egg
MANIFEST

# Virtual environments
venv/
env/
ENV/
env.bak/
venv.bak/

# Node.js
node_modules/
npm-debug.log*
yarn-debug.log*
yarn-error.log*
.pnpm-debug.log*
.npm
.eslintcache
.node_repl_history
.yarn-integrity

# React build outputs
build/
dist/
*.tsbuildinfo

# Environment variables
.env
.env.local
.env.development.local
.env.test.local
.env.production.local

# Logs
logs/
*.log
npm-debug.log*
yarn-debug.log*
yarn-error.log*
lerna-debug.log*
.pnpm-debug.log*

# Runtime data
pids/
*.pid
*.seed
*.pid.lock

# Database files
*.db
*.sqlite
*.sqlite3

# IDE files
.vscode/
.idea/
*.swp
*.swo
*~

# OS files
.DS_Store
.DS_Store?
._*
.Spotlight-V100
.Trashes
ehthumbs.db
Thumbs.db

# Docker
.docker/

# Coverage reports
htmlcov/
.coverage
.coverage.*
coverage.xml
*.cover
*.py,cover
.hypothesis/
.pytest_cache/

# Jupyter Notebook
.ipynb_checkpoints

# Audio files for testing
*.mp3
*.wav
*.flac

# Temporary files
*.tmp
*.temp
EOF

# Create environment template
cat > .env.example << 'EOF'
# Focus Flow Environment Configuration

# === Application Settings ===
FOCUS_FLOW_ENVIRONMENT=development
FOCUS_FLOW_DEBUG_MODE=true
FOCUS_FLOW_LOG_LEVEL=INFO
FOCUS_FLOW_API_VERSION=v1
FOCUS_FLOW_API_PREFIX=/api

# === Database Configuration ===
FOCUS_FLOW_DATABASE_URL=postgresql://focus_user:focus_password@localhost:5432/focus_flow_db
FOCUS_FLOW_REDIS_URL=redis://localhost:6379/0

# === External API Keys ===
# FOCUS_FLOW_OPENAI_API_KEY=your-openai-api-key-here
# FOCUS_FLOW_YOUTUBE_MUSIC_AUTH_FILE=auth.json

# === Security Settings ===
FOCUS_FLOW_SECRET_KEY=your-secret-key-change-in-production
FOCUS_FLOW_JWT_SECRET=your-jwt-secret-change-in-production

# === Performance Settings ===
FOCUS_FLOW_MAX_SESSIONS_PER_USER=1000
FOCUS_FLOW_SESSION_TIMEOUT_MINUTES=60
FOCUS_FLOW_AI_PROCESSING_TIMEOUT_SECONDS=30
EOF

echo "✅ Base repository structure created successfully"
```

**Deliverable**: Complete base repository with .gitignore and environment template  
**Time Estimate**: 5 minutes  
**Dependencies**: None

##### **A1.2: Create Services Directory Structure**

**Command Sequence**:

```bash
# Create Focus Engine service structure
mkdir -p services/focus_engine/{models,routers,services,database,config,utils}
touch services/focus_engine/{main.py,Dockerfile,requirements.txt,.env.example}
touch services/focus_engine/models/{__init__.py,session_models.py,user_models.py,base_models.py,response_models.py}
touch services/focus_engine/routers/{__init__.py,sessions.py,health.py,websockets.py}
touch services/focus_engine/services/{__init__.py,session_service.py,timer_service.py,notification_service.py}
touch services/focus_engine/database/{__init__.py,connection.py,repositories.py,session_repository.py}
touch services/focus_engine/config/{__init__.py,settings.py,logging_config.py}
touch services/focus_engine/utils/{__init__.py,time_calculations.py,validators.py}

# Create AI Insights service structure
mkdir -p services/ai_insights/{models,routers,clients,services,prompts,config}
touch services/ai_insights/{main.py,Dockerfile,requirements.txt}
touch services/ai_insights/models/{__init__.py,insights_models.py,analysis_models.py,pattern_models.py}
touch services/ai_insights/routers/{__init__.py,insights.py,patterns.py,coaching.py}
touch services/ai_insights/clients/{__init__.py,openai_client.py,ollama_client.py,analysis_client.py}
touch services/ai_insights/services/{__init__.py,session_analyzer.py,pattern_discoverer.py,coaching_generator.py,correlation_engine.py}
touch services/ai_insights/prompts/{session_analysis.txt,productivity_coaching.txt,pattern_interpretation.txt}
touch services/ai_insights/config/{__init__.py,ai_settings.py,prompt_config.py}

# Create Music Control service structure
mkdir -p services/music_control/{models,routers,clients,services,utils}
touch services/music_control/{main.py,Dockerfile,requirements.txt}
touch services/music_control/models/{__init__.py,playlist_models.py,track_models.py,session_music_models.py}
touch services/music_control/routers/{__init__.py,playlists.py,playback.py,discovery.py}
touch services/music_control/clients/{__init__.py,youtube_music_client.py,spotify_client.py,browser_control_client.py}
touch services/music_control/services/{__init__.py,playlist_service.py,focus_detection.py,effectiveness_tracker.py}
touch services/music_control/utils/{__init__.py,playlist_analyzer.py,genre_classifier.py}

# Create Analytics service structure
mkdir -p services/analytics/{models,routers,services,processors}
touch services/analytics/{main.py,Dockerfile,requirements.txt}
touch services/analytics/models/{__init__.py,metrics_models.py,trend_models.py,comparison_models.py}
touch services/analytics/routers/{__init__.py,metrics.py,trends.py,comparisons.py,export.py}
touch services/analytics/services/{__init__.py,metrics_calculator.py,trend_analyzer.py,comparative_analyzer.py,export_service.py}
touch services/analytics/processors/{__init__.py,session_aggregator.py,time_series_processor.py,correlation_processor.py}

# Create Game Engine service structure
mkdir -p services/game_engine/{models,routers,services,achievements,calculators}
touch services/game_engine/{main.py,Dockerfile,requirements.txt}
touch services/game_engine/models/{__init__.py,achievement_models.py,streak_models.py,level_models.py,reward_models.py}
touch services/game_engine/routers/{__init__.py,achievements.py,streaks.py,levels.py,leaderboards.py}
touch services/game_engine/services/{__init__.py,achievement_service.py,streak_service.py,level_service.py,experience_service.py}
touch services/game_engine/achievements/{__init__.py,base_achievements.py,focus_achievements.py,streak_achievements.py,milestone_achievements.py}
touch services/game_engine/calculators/{__init__.py,experience_calculator.py,streak_calculator.py,difficulty_calculator.py}

echo "✅ Microservices directory structure created successfully"
```

**Deliverable**: Complete microservices directory structure  
**Time Estimate**: 8 minutes  
**Dependencies**: Task A1.1 complete

##### **A1.3: Create Frontend Application Structure**

**Command Sequence**:

```bash
# Create React frontend structure
mkdir -p ui/focus_app/{public,src}
touch ui/focus_app/{package.json,tsconfig.json,tailwind.config.js,vite.config.ts,Dockerfile,.env.example}

# Create public assets
mkdir -p ui/focus_app/public/{sounds,images}
touch ui/focus_app/public/{index.html,favicon.ico}
touch ui/focus_app/public/sounds/{session_complete.mp3,break_start.mp3,gentle_reminder.mp3}

# Create source directory structure
mkdir -p ui/focus_app/src/components/{focus,music,insights,animations,game,analytics,settings,layout,common,forms}
mkdir -p ui/focus_app/src/{services,hooks,context,types,utils,styles}

# Create main application files
touch ui/focus_app/src/{main.tsx,App.tsx,index.css}

# Focus components
touch ui/focus_app/src/components/focus/{FocusTimer.tsx,SessionControls.tsx,ProgressRing.tsx,TimeDisplay.tsx,SessionStatus.tsx,InterruptionTracker.tsx}

# Music components
touch ui/focus_app/src/components/music/{PlaylistSelector.tsx,MusicControls.tsx,PlaylistBrowser.tsx,NowPlaying.tsx,MusicSettingsPanel.tsx}

# Insights components
touch ui/focus_app/src/components/insights/{SessionSummary.tsx,ProductivityChart.tsx,AICoachingPanel.tsx,PatternAnalysis.tsx,TrendVisualization.tsx,InsightsLoading.tsx}

# Animation components
touch ui/focus_app/src/components/animations/{FocusVisualizer.tsx,BreakModeVisualizer.tsx,ProgressAnimations.tsx,AchievementPopup.tsx,TransitionEffects.tsx}

# Game components
touch ui/focus_app/src/components/game/{AchievementBadge.tsx,AchievementGallery.tsx,StreakTracker.tsx,LevelProgress.tsx,ExperienceBar.tsx,RewardNotification.tsx}

# Analytics components
touch ui/focus_app/src/components/analytics/{DashboardOverview.tsx,FocusMetrics.tsx,TimeAnalysis.tsx,ProductivityHeatmap.tsx,SessionHistory.tsx,ExportControls.tsx}

# Settings components
touch ui/focus_app/src/components/settings/{UserPreferences.tsx,SessionSettings.tsx,NotificationSettings.tsx,MusicPreferences.tsx,PrivacySettings.tsx}

# Layout components
touch ui/focus_app/src/components/layout/{AppHeader.tsx,Sidebar.tsx,MainContent.tsx,Footer.tsx,NavigationTabs.tsx}

# Common components
touch ui/focus_app/src/components/common/{Button.tsx,Modal.tsx,LoadingSpinner.tsx,ErrorBoundary.tsx,Tooltip.tsx,ConfirmationDialog.tsx}

# Form components
touch ui/focus_app/src/components/forms/{SessionStartForm.tsx,InterruptionLogForm.tsx,FeedbackForm.tsx,FormControls.tsx}

# Services
touch ui/focus_app/src/services/{apiClient.ts,focusSessionService.ts,musicService.ts,insightsService.ts,analyticsService.ts,gameService.ts,websocketService.ts}

# Hooks
touch ui/focus_app/src/hooks/{useFocusSession.ts,useMusicControl.ts,useProductivityInsights.ts,useGameProgress.ts,useAnalytics.ts,useNotifications.ts,useLocalStorage.ts,useWebSocket.ts}

# Context providers
touch ui/focus_app/src/context/{AppContext.tsx,AuthContext.tsx,ThemeContext.tsx,NotificationContext.tsx}

# Types
touch ui/focus_app/src/types/{focus.ts,music.ts,insights.ts,analytics.ts,game.ts,api.ts,common.ts}

# Utils
touch ui/focus_app/src/utils/{timeFormatters.ts,sessionCalculations.ts,animationHelpers.ts,chartHelpers.ts,validationHelpers.ts,constants.ts}

# Styles
touch ui/focus_app/src/styles/{animations.css,components.css,themes.css,utilities.css}

echo "✅ React frontend structure created successfully"
```

**Deliverable**: Complete React application directory structure  
**Time Estimate**: 10 minutes  
**Dependencies**: Task A1.1 complete

##### **A1.4: Create Shared Libraries and Database Structure**

**Command Sequence**:

```bash
# Create shared library structure
mkdir -p shared/focus_shared/{models,utils,constants,exceptions,types}
touch shared/focus_shared/{setup.py,__init__.py,requirements.txt}
touch shared/focus_shared/models/{__init__.py,base_models.py,session_models.py,user_models.py,response_models.py}
touch shared/focus_shared/utils/{__init__.py,time_utils.py,validation_utils.py,logging_utils.py,config_utils.py}
touch shared/focus_shared/constants/{__init__.py,session_constants.py,achievement_constants.py,api_constants.py}
touch shared/focus_shared/exceptions/{__init__.py,session_exceptions.py,music_exceptions.py,api_exceptions.py}
touch shared/focus_shared/types/{__init__.py,session_types.py,music_types.py,api_types.py}

# Create database structure
mkdir -p database/{migrations,seeds,views,functions,backups}
touch database/{init.sql,schema.sql,seed_data.sql}
touch database/migrations/{001_initial_schema.sql,002_add_music_integration.sql,003_add_ai_insights.sql,004_add_gamification.sql,005_add_analytics_views.sql}
touch database/seeds/{demo_users.sql,sample_sessions.sql,sample_playlists.sql,achievement_definitions.sql}
touch database/views/{productivity_metrics.sql,session_analytics.sql,user_progress.sql}
touch database/functions/{session_calculations.sql,streak_maintenance.sql,achievement_checks.sql}
touch database/backups/{backup_script.sh,restore_script.sh}

# Create configuration structure
mkdir -p config/{environments,services,logging}
touch config/{app.yml,database.yml,redis.yml}
touch config/environments/{development.yml,staging.yml,production.yml,testing.yml}
touch config/services/{focus_engine.yml,ai_insights.yml,music_control.yml,analytics.yml,game_engine.yml}
touch config/logging/{development.yml,production.yml,structured_logging.yml}

echo "✅ Shared libraries and database structure created successfully"
```

**Deliverable**: Shared libraries and database management structure  
**Time Estimate**: 7 minutes  
**Dependencies**: Task A1.1 complete

##### **A1.5: Create Infrastructure, Documentation, and Support Files**

**Command Sequence**:

```bash
# Create infrastructure structure
mkdir -p infrastructure/{docker,kubernetes,monitoring,ci_cd,security}
touch infrastructure/docker/{docker-compose.yml,docker-compose.prod.yml,docker-compose.test.yml}
mkdir -p infrastructure/docker/dockerfiles
touch infrastructure/docker/dockerfiles/{focus-engine.Dockerfile,ai-insights.Dockerfile,music-control.Dockerfile,analytics.Dockerfile,game-engine.Dockerfile,frontend.Dockerfile}
touch infrastructure/kubernetes/{namespace.yaml,configmaps.yaml,secrets.yaml}
mkdir -p infrastructure/kubernetes/{services,ingress}
touch infrastructure/monitoring/{prometheus.yml,grafana-dashboards.json,alertmanager.yml}
mkdir -p infrastructure/monitoring/healthchecks
touch infrastructure/ci_cd/{.github_workflows.yml,.gitlab-ci.yml,jenkins_pipeline.groovy}
touch infrastructure/security/{network_policies.yaml,rbac.yaml,security_policies.yaml}

# Create documentation structure
mkdir -p docs/{api,architecture,development,user_guides,deployment,design}
touch docs/api/{focus_engine_api.md,ai_insights_api.md,music_control_api.md,analytics_api.md,game_engine_api.md,websocket_api.md}
touch docs/architecture/{system_overview.md,database_design.md,service_architecture.md,security_architecture.md,deployment_architecture.md}
touch docs/development/{getting_started.md,coding_standards.md,testing_guidelines.md,debugging_guide.md,contributing.md}
touch docs/user_guides/{user_manual.md,getting_started_guide.md,advanced_features.md,troubleshooting.md}
touch docs/deployment/{local_development.md,docker_deployment.md,kubernetes_deployment.md,production_deployment.md}
touch docs/design/{ui_design_system.md,user_experience_guide.md,accessibility_guide.md}

# Create testing structure
mkdir -p tests/{unit,integration,e2e,performance,fixtures,utils}
mkdir -p tests/unit/{services,shared,frontend}
touch tests/unit/services/{test_focus_engine.py,test_ai_insights.py,test_music_control.py,test_analytics.py,test_game_engine.py}
touch tests/unit/shared/{test_time_utils.py,test_validation_utils.py,test_config_utils.py}
touch tests/unit/frontend/{test_focus_timer.test.tsx,test_music_controls.test.tsx,test_insights_panel.test.tsx,test_game_components.test.tsx}
touch tests/integration/{test_session_workflow.py,test_music_integration.py,test_ai_integration.py,test_database_operations.py,test_api_integration.py}
touch tests/e2e/{test_complete_session.py,test_user_journey.py,test_gamification.py,test_analytics_flow.py}
touch tests/performance/{test_api_performance.py,test_database_performance.py,test_frontend_performance.py}
touch tests/fixtures/{sample_sessions.json,sample_playlists.json,sample_users.json,mock_responses.json}
touch tests/utils/{test_helpers.py,mock_services.py,data_generators.py}
touch tests/conftest.py

# Create scripts structure
mkdir -p scripts/{setup,development,deployment,monitoring,utilities}
touch scripts/setup/{install_dependencies.sh,setup_database.sh,setup_environment.sh,install_pre_commit.sh}
touch scripts/development/{start_dev_services.sh,run_migrations.sh,seed_test_data.sh,lint_and_format.sh,run_tests.sh}
touch scripts/deployment/{build_images.sh,deploy_staging.sh,deploy_production.sh,rollback_deployment.sh}
touch scripts/monitoring/{health_check.sh,log_analysis.sh,performance_monitoring.sh,backup_database.sh}
touch scripts/utilities/{generate_api_docs.sh,update_dependencies.sh,clean_build_artifacts.sh}

# Create assets structure
mkdir -p assets/{images,sounds,animations,fonts}
mkdir -p assets/images/{icons,backgrounds,branding}
mkdir -p assets/images/icons/achievement_icons
touch assets/images/icons/{app_icon.svg,timer_icon.svg,music_icon.svg}
touch assets/images/backgrounds/{focus_gradient.svg,break_pattern.svg,dashboard_background.svg}
touch assets/images/branding/{logo.svg,logo_variations.svg,brand_guidelines.pdf}
touch assets/sounds/{session_start.mp3,session_complete.mp3,break_start.mp3,achievement_unlock.mp3,gentle_reminder.mp3}
touch assets/animations/{focus_particles.json,break_animation.json,achievement_animation.json}
touch assets/fonts/{focus_display_font.woff2,ui_font.woff2}

# Create examples and logs directories
mkdir -p examples/{demo_data,usage_examples,api_examples}
touch examples/demo_data/{sample_focus_sessions.json,sample_playlists.json,demo_achievements.json}
touch examples/usage_examples/{basic_session.py,ai_insights_demo.py,music_integration_demo.py}
touch examples/api_examples/{session_api_usage.py,insights_api_usage.py,music_api_usage.py}

mkdir -p logs/{services,access,error,debug}

echo "✅ Infrastructure, documentation, and support files created successfully"
```

**Deliverable**: Complete project infrastructure and documentation structure  
**Time Estimate**: 12 minutes  
**Dependencies**: Task A1.1 complete

##### **A1.6: Create Core Project Files**

**Command Sequence**:

````bash
# Create comprehensive README
cat > README.md << 'EOF'
# Focus Flow - Interactive Productivity Timer

A gamified Pomodoro timer that combines enterprise-grade React patterns with AI-powered productivity insights, featuring YouTube Music integration and animated visual feedback.

## 🎯 Project Overview

Focus Flow is designed to showcase:
- **Enterprise React Patterns**: Component architecture from SSLLC Structure
- **AI Integration**: Analytics and insights from Data Centralization Platform
- **External API Integration**: YouTube Music for enhanced user experience
- **Rapid MVP Development**: Complete functional application in 2-week cycle

## 🏗️ Architecture

### Microservices
- **Focus Engine**: Core timer and session management
- **AI Insights**: Productivity coaching and pattern analysis
- **Music Control**: YouTube Music playlist integration
- **Analytics**: Session data analysis and visualization
- **Game Engine**: Achievement system and gamification

### Frontend
- **React + TypeScript**: Modern frontend with enterprise patterns
- **Tailwind CSS**: Responsive design system
- **Vite**: Fast build tooling and development server

## 🚀 Quick Start

### Prerequisites
- Node.js 18+
- Python 3.11+
- PostgreSQL 14+
- Redis 6+

### Development Setup

1. **Clone and Setup**
   ```bash
   git clone https://github.com/soundstate/focus-flow_DEMO.git
   cd focus-flow_DEMO
   cp .env.example .env
````

2. **Start Services**

   ```bash
   # Start backend services
   docker-compose up -d

   # Start frontend development server
   cd ui/focus_app
   npm install
   npm run dev
   ```

3. **Access Application**
   - Frontend: http://localhost:3000
   - API Documentation: http://localhost:8000/docs

## 📊 Features

### Core Timer

- ✅ 50-minute focus sessions with 10-minute breaks
- ✅ Animated progress indicators
- ✅ Interruption tracking
- ✅ Session pause/resume functionality

### Music Integration

- 🔄 YouTube Music playlist discovery
- 🔄 Automatic focus playlist management
- 🔄 Music effectiveness analysis

### AI Insights

- 🔄 Post-session productivity analysis
- 🔄 Pattern recognition and coaching
- 🔄 Personalized recommendations

### Gamification

- 🔄 Achievement system
- 🔄 Focus streak tracking
- 🔄 Level progression

### Analytics

- 🔄 Productivity trend visualization
- 🔄 Time effectiveness heatmaps
- 🔄 Comparative performance analysis

## 🧪 Testing

```bash
# Run backend tests
pytest tests/

# Run frontend tests
cd ui/focus_app
npm run test
```

## 📦 Deployment

### Docker Development

```bash
docker-compose up --build
```

### Production

```bash
docker-compose -f docker-compose.prod.yml up --build
```

## 🤝 Contributing

1. Fork the repository
2. Create feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- SSLLC Structure patterns for enterprise architecture
- Data Centralization Platform for AI integration patterns
- YouTube Music API for music integration capabilities
  EOF

# Create contributing guide

cat > CONTRIBUTING.md << 'EOF'

# Contributing to Focus Flow

## Development Setup

1. Clone the repository
2. Install dependencies (see README.md)
3. Create feature branch
4. Make changes
5. Run tests
6. Submit pull request

## Code Standards

- Follow TypeScript best practices
- Use Tailwind CSS for styling
- Write comprehensive tests
- Document API changes
- Follow conventional commits

## Testing Requirements

- Unit tests for all business logic
- Integration tests for API endpoints
- E2E tests for critical user flows
- Performance tests for scalability

## Pull Request Process

1. Update documentation
2. Add tests for new features
3. Ensure all tests pass
4. Update changelog
5. Request review
   EOF

# Create license file

cat > LICENSE << 'EOF'
MIT License

Copyright (c) 2025 Sound State

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, so forth.

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
EOF

# Create Docker Compose for development

cat > docker-compose.yml << 'EOF'
version: '3.8'

services:
postgres:
image: postgres:15
container_name: focus-flow-postgres
environment:
POSTGRES_DB: focus_flow_db
POSTGRES_USER: focus_user
POSTGRES_PASSWORD: focus_password
ports: - "5432:5432"
volumes: - postgres_data:/var/lib/postgresql/data - ./database/init.sql:/docker-entrypoint-initdb.d/init.sql

redis:
image: redis:7-alpine
container_name: focus-flow-redis
ports: - "6379:6379"
command: redis-server --requirepass focus_redis_password

focus-engine:
build:
context: ./services/focus_engine
dockerfile: Dockerfile
container_name: focus-flow-engine
environment: - FOCUS_FLOW_DATABASE_URL=postgresql://focus_user:focus_password@postgres:5432/focus_flow_db - FOCUS_FLOW_REDIS_URL=redis://:focus_redis_password@redis:6379/0
ports: - "8001:8000"
depends_on: - postgres - redis
volumes: - ./services/focus_engine:/app
command: uvicorn main:app --host 0.0.0.0 --port 8000 --reload

ai-insights:
build:
context: ./services/ai_insights
dockerfile: Dockerfile
container_name: focus-flow-ai-insights
environment: - FOCUS_FLOW_DATABASE_URL=postgresql://focus_user:focus_password@postgres:5432/focus_flow_db - FOCUS_FLOW_REDIS_URL=redis://:focus_redis_password@redis:6379/0
ports: - "8002:8000"
depends_on: - postgres - redis
volumes: - ./services/ai_insights:/app

volumes:
postgres_data:
EOF

echo "✅ Core project files created successfully"

````

**Deliverable**: Complete project documentation and Docker setup
**Time Estimate**: 15 minutes
**Dependencies**: All previous A1 tasks complete

#### **Task A2: Create GitHub Repository and Initial Commit**

**Overview**: Initialize GitHub repository, commit the complete structure, and push to the soundstate GitHub account.

##### **A2.1: GitHub Repository Creation and Initial Commit**

**Command Sequence**:
```bash
# Add all files to git
git add .

# Create initial commit
git commit -m "feat: initial Focus Flow repository structure

- Complete microservices architecture (5 services)
- React frontend with enterprise component patterns
- Shared libraries for cross-service utilities
- Database schema and migration framework
- Infrastructure setup with Docker Compose
- Comprehensive testing structure
- Documentation and development guides
- Assets and static resource organization

Implements enterprise patterns from SSLLC Structure and AI integration
patterns from Data Centralization Platform for rapid MVP development."

# Create GitHub repository using gh CLI (if available)
gh repo create soundstate/focus-flow_DEMO --public --description "Interactive productivity timer with AI insights and music integration - Technology showcase combining SSLLC Structure and Data Centralization Platform patterns"

# Add GitHub remote
git remote add origin https://github.com/soundstate/focus-flow_DEMO.git

# Push to GitHub
git push -u origin main

echo "✅ Repository created and pushed to GitHub successfully"
echo "Repository URL: https://github.com/soundstate/focus-flow_DEMO"
````

**Alternative Manual GitHub Creation** (if gh CLI not available):

```bash
echo "🔍 If GitHub CLI is not available, please:"
echo "1. Go to https://github.com/soundstate"
echo "2. Click 'New repository'"
echo "3. Repository name: focus-flow_DEMO"
echo "4. Description: Interactive productivity timer with AI insights and music integration"
echo "5. Public repository"
echo "6. Do not initialize with README (we already have one)"
echo "7. Create repository"
echo "8. Copy the repository URL and run:"
echo "   git remote add origin https://github.com/soundstate/focus-flow_DEMO.git"
echo "   git push -u origin main"
```

**Deliverable**: GitHub repository created with complete codebase  
**Time Estimate**: 10 minutes  
**Dependencies**: Task A1 complete

---

## 🏗️ Core Component Development Tasks

### Task Group B: Focus Engine Service Development

#### **Task B1: Focus Engine Service Foundation**

**Overview**: Create the core Focus Engine service with FastAPI, database models, and basic session management functionality.

##### **B1.1: Focus Engine FastAPI Application Setup**

**Command Sequence**:

```bash
cd services/focus_engine

# Create requirements.txt
cat > requirements.txt << 'EOF'
fastapi==0.104.1
uvicorn[standard]==0.24.0
sqlalchemy==2.0.23
psycopg2-binary==2.9.9
alembic==1.12.1
pydantic==2.5.0
pydantic-settings==2.1.0
redis==5.0.1
python-jose[cryptography]==3.3.0
passlib[bcrypt]==1.7.4
python-multipart==0.0.6
websockets==12.0
pytest==7.4.3
pytest-asyncio==0.21.1
httpx==0.25.2
EOF

# Create main FastAPI application
cat > main.py << 'EOF'
"""
Focus Flow - Focus Engine Service
Main FastAPI application for focus session management
"""

from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import uvicorn
from config.settings import get_settings
from config.logging_config import setup_logging
from routers import sessions, health, websockets
from database.connection import engine
from sqlalchemy.orm import Session

# Initialize settings and logging
settings = get_settings()
logger = setup_logging()

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan management"""
    logger.info("🚀 Focus Engine service starting up...")
    yield
    logger.info("📴 Focus Engine service shutting down...")

# Create FastAPI application
app = FastAPI(
    title="Focus Flow - Focus Engine",
    description="Core focus session management and timer functionality",
    version="1.0.0",
    docs_url="/docs" if settings.debug_mode else None,
    redoc_url="/redoc" if settings.debug_mode else None,
    lifespan=lifespan
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(health.router, prefix="/health", tags=["health"])
app.include_router(sessions.router, prefix="/api/v1/sessions", tags=["sessions"])
app.include_router(websockets.router, prefix="/ws", tags=["websockets"])

@app.get("/")
async def root():
    """Root endpoint with service information"""
    return {
        "service": "Focus Flow - Focus Engine",
        "version": "1.0.0",
        "status": "operational",
        "description": "Core focus session management and timer functionality"
    }

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.debug_mode,
        log_level=settings.log_level.lower()
    )
EOF

echo "✅ Focus Engine FastAPI application created"
```

**Deliverable**: Complete FastAPI application foundation  
**Time Estimate**: 20 minutes  
**Dependencies**: Task A2 complete

##### **B1.2: Database Models and Configuration**

**Command Sequence**:

```bash
# Create settings configuration
cat > config/settings.py << 'EOF'
"""
Focus Engine Service Configuration
Environment-driven settings using Pydantic
"""

from pydantic_settings import BaseSettings
from typing import List, Optional
import os

class Settings(BaseSettings):
    """Application settings"""

    # Application settings
    debug_mode: bool = True
    log_level: str = "INFO"
    environment: str = "development"

    # Database settings
    database_url: str = "postgresql://focus_user:focus_password@localhost:5432/focus_flow_db"

    # Redis settings
    redis_url: str = "redis://localhost:6379/0"

    # Security settings
    secret_key: str = "focus-flow-secret-key-change-in-production"
    jwt_secret: str = "focus-flow-jwt-secret-change-in-production"

    # API settings
    api_prefix: str = "/api/v1"
    cors_origins: List[str] = ["http://localhost:3000", "http://localhost:3001"]

    # Session settings
    max_sessions_per_user: int = 1000
    session_timeout_minutes: int = 60
    default_session_duration: int = 50  # minutes
    default_break_duration: int = 10    # minutes

    class Config:
        env_prefix = "FOCUS_FLOW_"
        env_file = ".env"

def get_settings() -> Settings:
    """Get application settings"""
    return Settings()
EOF

# Create logging configuration
cat > config/logging_config.py << 'EOF'
"""
Focus Engine Logging Configuration
Centralized logging setup following enterprise patterns
"""

import logging
import sys
from typing import Dict, Any
import json
from datetime import datetime

class JSONFormatter(logging.Formatter):
    """JSON log formatter for structured logging"""

    def format(self, record: logging.LogRecord) -> str:
        log_entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "level": record.levelname,
            "service": "focus-engine",
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno
        }

        # Add exception info if present
        if record.exc_info:
            log_entry["exception"] = self.formatException(record.exc_info)

        return json.dumps(log_entry)

def setup_logging() -> logging.Logger:
    """Setup structured logging for the service"""

    logger = logging.getLogger("focus_engine")
    logger.setLevel(logging.INFO)

    # Remove existing handlers
    for handler in logger.handlers[:]:
        logger.removeHandler(handler)

    # Create console handler with JSON formatting
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(JSONFormatter())
    logger.addHandler(console_handler)

    return logger
EOF

# Create database connection
cat > database/connection.py << 'EOF'
"""
Focus Engine Database Connection
SQLAlchemy setup with connection pooling
"""

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from config.settings import get_settings
import logging

logger = logging.getLogger("focus_engine.database")
settings = get_settings()

# Create SQLAlchemy engine
engine = create_engine(
    settings.database_url,
    pool_size=20,
    max_overflow=10,
    pool_timeout=30,
    pool_recycle=3600,
    echo=settings.debug_mode
)

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create declarative base
Base = declarative_base()

def get_database() -> Session:
    """Get database session dependency"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
EOF

echo "✅ Database configuration created"
```

**Deliverable**: Complete database and configuration setup  
**Time Estimate**: 15 minutes  
**Dependencies**: Task B1.1 complete

##### **B1.3: Session Models and Basic API Endpoints**

**Command Sequence**:

```bash
# Create session models
cat > models/session_models.py << 'EOF'
"""
Focus Session Data Models
SQLAlchemy models for focus sessions and related data
"""

from sqlalchemy import Column, Integer, String, DateTime, Float, Boolean, JSON, Text
from sqlalchemy.dialects.postgresql import UUID, ARRAY
from database.connection import Base
from datetime import datetime
from typing import Optional, List, Dict, Any
import uuid
from pydantic import BaseModel, Field

class FocusSession(Base):
    """Focus session database model"""
    __tablename__ = "focus_sessions"

    id = Column(Integer, primary_key=True, index=True)
    session_uuid = Column(UUID(as_uuid=True), default=uuid.uuid4, unique=True, index=True)
    user_id = Column(String(255), index=True)  # Future multi-user support

    # Session timing
    start_time = Column(DateTime, nullable=False, index=True)
    end_time = Column(DateTime, nullable=True)
    planned_duration = Column(Integer, default=50)  # minutes
    actual_duration = Column(Integer, nullable=True)
    break_duration = Column(Integer, default=10)

    # Session quality metrics
    completion_rate = Column(Float, nullable=True)  # 0.0 to 1.0
    productivity_score = Column(Float, nullable=True)  # 0.0 to 10.0
    interruptions = Column(Integer, default=0)
    interruption_types = Column(JSON, nullable=True)
    focus_quality = Column(String(50), nullable=True)  # "high", "medium", "low"

    # Session context
    session_type = Column(String(50), default="work")  # "work", "break", "deep_work"
    time_of_day_category = Column(String(50), nullable=True)  # "morning", "afternoon", "evening"

    # Music integration
    playlist_id = Column(String(255), nullable=True)
    playlist_name = Column(String(500), nullable=True)

    # AI-generated insights
    ai_insights = Column(Text, nullable=True)
    optimal_time_suggestions = Column(Text, nullable=True)
    improvement_recommendations = Column(JSON, nullable=True)

    # Gamification
    experience_points = Column(Integer, default=0)
    achievements_unlocked = Column(JSON, nullable=True)

    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class User(Base):
    """User model for future multi-user support"""
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    user_uuid = Column(UUID(as_uuid=True), default=uuid.uuid4, unique=True, index=True)
    username = Column(String(255), unique=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=True)

    # User preferences
    default_session_duration = Column(Integer, default=50)
    default_break_duration = Column(Integer, default=10)
    notification_preferences = Column(JSON, nullable=True)

    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    is_active = Column(Boolean, default=True)

# Pydantic models for API
class SessionStartRequest(BaseModel):
    """Request model for starting a focus session"""
    duration: int = Field(default=50, ge=1, le=180, description="Session duration in minutes")
    session_type: str = Field(default="work", description="Type of session")
    playlist_id: Optional[str] = Field(None, description="Music playlist ID")
    user_id: str = Field(default="demo_user", description="User identifier")

class SessionCompletionRequest(BaseModel):
    """Request model for completing a focus session"""
    completion_rate: float = Field(ge=0.0, le=1.0, description="Session completion percentage")
    productivity_score: float = Field(ge=0.0, le=10.0, description="Self-assessed productivity score")
    interruptions: int = Field(ge=0, description="Number of interruptions")
    interruption_types: Optional[List[str]] = Field(None, description="Types of interruptions")

class SessionResponse(BaseModel):
    """Response model for focus session data"""
    id: int
    session_uuid: str
    user_id: str
    start_time: datetime
    end_time: Optional[datetime]
    planned_duration: int
    actual_duration: Optional[int]
    completion_rate: Optional[float]
    productivity_score: Optional[float]
    interruptions: int
    session_type: str
    playlist_id: Optional[str]
    playlist_name: Optional[str]
    ai_insights: Optional[str]
    experience_points: int
    created_at: datetime

    class Config:
        from_attributes = True
EOF

# Create health check router
cat > routers/health.py << 'EOF'
"""
Health Check Router
Service health monitoring endpoints
"""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from database.connection import get_database
from config.settings import get_settings
import redis
import logging

logger = logging.getLogger("focus_engine.health")
router = APIRouter()
settings = get_settings()

@router.get("/")
async def health_check():
    """Basic health check"""
    return {
        "service": "focus-engine",
        "status": "healthy",
        "version": "1.0.0"
    }

@router.get("/detailed")
async def detailed_health_check(db: Session = Depends(get_database)):
    """Detailed health check with dependency validation"""
    health_status = {
        "service": "focus-engine",
        "status": "healthy",
        "version": "1.0.0",
        "checks": {}
    }

    # Database connection check
    try:
        db.execute("SELECT 1")
        health_status["checks"]["database"] = "healthy"
    except Exception as e:
        logger.error(f"Database health check failed: {e}")
        health_status["checks"]["database"] = "unhealthy"
        health_status["status"] = "degraded"

    # Redis connection check
    try:
        r = redis.from_url(settings.redis_url)
        r.ping()
        health_status["checks"]["redis"] = "healthy"
    except Exception as e:
        logger.error(f"Redis health check failed: {e}")
        health_status["checks"]["redis"] = "unhealthy"
        health_status["status"] = "degraded"

    return health_status
EOF

# Create session router with basic endpoints
cat > routers/sessions.py << 'EOF'
"""
Focus Session Router
API endpoints for focus session management
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from database.connection import get_database
from models.session_models import FocusSession, SessionStartRequest, SessionCompletionRequest, SessionResponse
from datetime import datetime, timedelta
from typing import List
import logging

logger = logging.getLogger("focus_engine.sessions")
router = APIRouter()

@router.post("/start", response_model=SessionResponse)
async def start_session(
    session_request: SessionStartRequest,
    db: Session = Depends(get_database)
):
    """Start a new focus session"""

    logger.info(f"Starting new session for user {session_request.user_id}, duration: {session_request.duration} minutes")

    # Create new session
    session = FocusSession(
        user_id=session_request.user_id,
        start_time=datetime.utcnow(),
        planned_duration=session_request.duration,
        session_type=session_request.session_type,
        playlist_id=session_request.playlist_id,
        break_duration=10  # Default break duration
    )

    db.add(session)
    db.commit()
    db.refresh(session)

    logger.info(f"Session created successfully with ID: {session.id}")

    return session

@router.put("/{session_id}/complete", response_model=SessionResponse)
async def complete_session(
    session_id: int,
    completion_data: SessionCompletionRequest,
    db: Session = Depends(get_database)
):
    """Complete a focus session"""

    # Get session
    session = db.query(FocusSession).filter(FocusSession.id == session_id).first()
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Session not found"
        )

    # Update session data
    session.end_time = datetime.utcnow()
    session.actual_duration = int((session.end_time - session.start_time).total_seconds() / 60)
    session.completion_rate = completion_data.completion_rate
    session.productivity_score = completion_data.productivity_score
    session.interruptions = completion_data.interruptions
    session.interruption_types = completion_data.interruption_types

    # Calculate experience points based on completion
    session.experience_points = int(completion_data.completion_rate * 100 + completion_data.productivity_score * 10)

    # Determine focus quality
    if completion_data.completion_rate >= 0.9 and completion_data.productivity_score >= 8:
        session.focus_quality = "high"
    elif completion_data.completion_rate >= 0.7 and completion_data.productivity_score >= 6:
        session.focus_quality = "medium"
    else:
        session.focus_quality = "low"

    db.commit()
    db.refresh(session)

    logger.info(f"Session {session_id} completed: {completion_data.completion_rate:.1%} completion, {completion_data.productivity_score}/10 productivity")

    return session

@router.get("/{session_id}", response_model=SessionResponse)
async def get_session(session_id: int, db: Session = Depends(get_database)):
    """Get a specific session by ID"""

    session = db.query(FocusSession).filter(FocusSession.id == session_id).first()
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Session not found"
        )

    return session

@router.get("/user/{user_id}", response_model=List[SessionResponse])
async def get_user_sessions(
    user_id: str,
    limit: int = 50,
    db: Session = Depends(get_database)
):
    """Get sessions for a specific user"""

    sessions = (db.query(FocusSession)
               .filter(FocusSession.user_id == user_id)
               .order_by(FocusSession.start_time.desc())
               .limit(limit)
               .all())

    return sessions

@router.delete("/{session_id}")
async def delete_session(session_id: int, db: Session = Depends(get_database)):
    """Delete a session"""

    session = db.query(FocusSession).filter(FocusSession.id == session_id).first()
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Session not found"
        )

    db.delete(session)
    db.commit()

    return {"message": "Session deleted successfully"}
EOF

# Create basic websocket router
cat > routers/websockets.py << 'EOF'
"""
WebSocket Router
Real-time session updates and timer synchronization
"""

from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from typing import Dict, Set
import json
import asyncio
import logging

logger = logging.getLogger("focus_engine.websockets")
router = APIRouter()

# Active WebSocket connections
active_connections: Dict[str, Set[WebSocket]] = {}

@router.websocket("/session/{session_id}")
async def websocket_session_updates(websocket: WebSocket, session_id: str):
    """WebSocket endpoint for real-time session updates"""

    await websocket.accept()

    # Add connection to active connections
    if session_id not in active_connections:
        active_connections[session_id] = set()
    active_connections[session_id].add(websocket)

    logger.info(f"WebSocket connected for session {session_id}")

    try:
        while True:
            # Listen for messages from client
            data = await websocket.receive_text()
            message = json.loads(data)

            # Echo message back to all connections for this session
            if session_id in active_connections:
                for connection in active_connections[session_id].copy():
                    try:
                        await connection.send_text(data)
                    except:
                        active_connections[session_id].discard(connection)

    except WebSocketDisconnect:
        # Remove connection
        if session_id in active_connections:
            active_connections[session_id].discard(websocket)
            if not active_connections[session_id]:
                del active_connections[session_id]

        logger.info(f"WebSocket disconnected for session {session_id}")

async def broadcast_session_update(session_id: str, update_data: dict):
    """Broadcast update to all connections for a session"""

    if session_id in active_connections:
        message = json.dumps(update_data)
        for connection in active_connections[session_id].copy():
            try:
                await connection.send_text(message)
            except:
                active_connections[session_id].discard(connection)
EOF

# Create Dockerfile
cat > Dockerfile << 'EOF'
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Expose port
EXPOSE 8000

# Run the application
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
EOF

echo "✅ Focus Engine service core components created"
```

**Deliverable**: Complete Focus Engine service with API endpoints  
**Time Estimate**: 35 minutes  
**Dependencies**: Task B1.2 complete

---

### Task Group C: Database Setup and Initial Frontend

#### **Task C1: Database Schema and Initialization**

**Overview**: Create the complete database schema, migrations, and seed data for the Focus Flow application.

##### **C1.1: Database Schema Creation**

**Command Sequence**:

```bash
cd ../../database

# Create comprehensive database schema
cat > schema.sql << 'EOF'
-- Focus Flow Database Schema
-- Complete database structure for focus sessions, users, analytics, and gamification

-- Create extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_trgm";

-- Users table for future multi-user support
CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    user_uuid UUID DEFAULT uuid_generate_v4() UNIQUE NOT NULL,
    username VARCHAR(255) UNIQUE NOT NULL,
    email VARCHAR(255) UNIQUE,
    password_hash VARCHAR(255),

    -- User preferences
    default_session_duration INTEGER DEFAULT 50,
    default_break_duration INTEGER DEFAULT 10,
    notification_preferences JSONB DEFAULT '{}',

    -- Metadata
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    is_active BOOLEAN DEFAULT TRUE
);

-- Focus sessions table
CREATE TABLE IF NOT EXISTS focus_sessions (
    id SERIAL PRIMARY KEY,
    session_uuid UUID DEFAULT uuid_generate_v4() UNIQUE NOT NULL,
    user_id VARCHAR(255) NOT NULL DEFAULT 'demo_user',

    -- Session timing
    start_time TIMESTAMP WITH TIME ZONE NOT NULL,
    end_time TIMESTAMP WITH TIME ZONE,
    planned_duration INTEGER DEFAULT 50, -- minutes
    actual_duration INTEGER,
    break_duration INTEGER DEFAULT 10,

    -- Session quality metrics
    completion_rate FLOAT CHECK (completion_rate >= 0.0 AND completion_rate <= 1.0),
    productivity_score FLOAT CHECK (productivity_score >= 0.0 AND productivity_score <= 10.0),
    interruptions INTEGER DEFAULT 0,
    interruption_types JSONB,
    focus_quality VARCHAR(50) CHECK (focus_quality IN ('high', 'medium', 'low')),

    -- Session context
    session_type VARCHAR(50) DEFAULT 'work' CHECK (session_type IN ('work', 'break', 'deep_work')),
    time_of_day_category VARCHAR(50) CHECK (time_of_day_category IN ('morning', 'afternoon', 'evening')),

    -- Music integration
    playlist_id VARCHAR(255),
    playlist_name VARCHAR(500),

    -- AI-generated insights
    ai_insights TEXT,
    optimal_time_suggestions TEXT,
    improvement_recommendations JSONB,

    -- Gamification
    experience_points INTEGER DEFAULT 0,
    achievements_unlocked JSONB DEFAULT '[]',

    -- Metadata
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Music playlists table
CREATE TABLE IF NOT EXISTS music_playlists (
    id SERIAL PRIMARY KEY,
    playlist_uuid UUID DEFAULT uuid_generate_v4() UNIQUE NOT NULL,
    user_id VARCHAR(255) NOT NULL DEFAULT 'demo_user',

    -- Playlist information
    external_id VARCHAR(255) NOT NULL, -- YouTube Music playlist ID
    title VARCHAR(500) NOT NULL,
    description TEXT,
    thumbnail_url VARCHAR(1000),
    track_count INTEGER DEFAULT 0,

    -- Focus suitability
    is_focus_suitable BOOLEAN DEFAULT FALSE,
    focus_effectiveness_score FLOAT DEFAULT 0.0,
    avg_session_completion_rate FLOAT,
    avg_productivity_score FLOAT,

    -- Usage statistics
    usage_count INTEGER DEFAULT 0,
    last_used TIMESTAMP WITH TIME ZONE,

    -- Metadata
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Achievements definition table
CREATE TABLE IF NOT EXISTS achievement_definitions (
    id SERIAL PRIMARY KEY,
    achievement_uuid UUID DEFAULT uuid_generate_v4() UNIQUE NOT NULL,

    -- Achievement details
    achievement_key VARCHAR(255) UNIQUE NOT NULL,
    title VARCHAR(255) NOT NULL,
    description TEXT NOT NULL,
    category VARCHAR(100) NOT NULL, -- 'focus', 'streak', 'milestone', 'improvement'

    -- Requirements
    requirement_type VARCHAR(100) NOT NULL, -- 'session_count', 'streak_days', 'focus_time', 'productivity_score'
    requirement_value FLOAT NOT NULL,
    requirement_timeframe VARCHAR(50), -- 'daily', 'weekly', 'monthly', 'all_time'

    -- Rewards
    experience_points INTEGER DEFAULT 0,
    badge_icon VARCHAR(255),
    badge_color VARCHAR(50),

    -- Metadata
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- User achievements table
CREATE TABLE IF NOT EXISTS user_achievements (
    id SERIAL PRIMARY KEY,
    user_id VARCHAR(255) NOT NULL DEFAULT 'demo_user',
    achievement_id INTEGER REFERENCES achievement_definitions(id),

    -- Achievement progress
    current_progress FLOAT DEFAULT 0.0,
    is_unlocked BOOLEAN DEFAULT FALSE,
    unlocked_at TIMESTAMP WITH TIME ZONE,

    -- Context
    unlock_session_id INTEGER REFERENCES focus_sessions(id),

    -- Metadata
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,

    UNIQUE(user_id, achievement_id)
);

-- User streaks table
CREATE TABLE IF NOT EXISTS user_streaks (
    id SERIAL PRIMARY KEY,
    user_id VARCHAR(255) NOT NULL DEFAULT 'demo_user',

    -- Streak information
    streak_type VARCHAR(50) NOT NULL, -- 'daily_sessions', 'weekly_goals', 'consistency'
    current_streak INTEGER DEFAULT 0,
    longest_streak INTEGER DEFAULT 0,
    last_activity_date DATE,

    -- Metadata
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,

    UNIQUE(user_id, streak_type)
);

-- Create indexes for performance
CREATE INDEX IF NOT EXISTS idx_focus_sessions_user_id ON focus_sessions(user_id);
CREATE INDEX IF NOT EXISTS idx_focus_sessions_start_time ON focus_sessions(start_time);
CREATE INDEX IF NOT EXISTS idx_focus_sessions_session_type ON focus_sessions(session_type);
CREATE INDEX IF NOT EXISTS idx_focus_sessions_focus_quality ON focus_sessions(focus_quality);
CREATE INDEX IF NOT EXISTS idx_music_playlists_user_id ON music_playlists(user_id);
CREATE INDEX IF NOT EXISTS idx_music_playlists_focus_suitable ON music_playlists(is_focus_suitable);
CREATE INDEX IF NOT EXISTS idx_user_achievements_user_id ON user_achievements(user_id);
CREATE INDEX IF NOT EXISTS idx_user_achievements_unlocked ON user_achievements(is_unlocked);
CREATE INDEX IF NOT EXISTS idx_user_streaks_user_id ON user_streaks(user_id);

-- Create updated_at triggers
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER update_users_updated_at
    BEFORE UPDATE ON users
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_focus_sessions_updated_at
    BEFORE UPDATE ON focus_sessions
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_music_playlists_updated_at
    BEFORE UPDATE ON music_playlists
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_user_achievements_updated_at
    BEFORE UPDATE ON user_achievements
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_user_streaks_updated_at
    BEFORE UPDATE ON user_streaks
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
EOF

# Create database initialization script
cat > init.sql << 'EOF'
-- Focus Flow Database Initialization
-- Run this script to set up the database for the first time

\echo 'Creating Focus Flow database schema...'

-- Include the main schema
\i schema.sql

\echo 'Database schema created successfully!'

-- Create demo user
INSERT INTO users (username, email, default_session_duration, default_break_duration)
VALUES ('demo_user', 'demo@focusflow.app', 50, 10)
ON CONFLICT (username) DO NOTHING;

\echo 'Demo user created!'

-- Insert default achievement definitions
\i seed_data.sql

\echo 'Focus Flow database initialization completed!'
EOF

echo "✅ Database schema created"
```

**Deliverable**: Complete database schema with tables, indexes, and triggers  
**Time Estimate**: 25 minutes  
**Dependencies**: Task B1 complete

##### **C1.2: Seed Data and Achievement Definitions**

**Command Sequence**:

```bash
# Create seed data with achievements and sample data
cat > seed_data.sql << 'EOF'
-- Focus Flow Seed Data
-- Default achievement definitions and sample data

-- Insert achievement definitions
INSERT INTO achievement_definitions (achievement_key, title, description, category, requirement_type, requirement_value, experience_points, badge_icon, badge_color) VALUES
-- First Steps Achievements
('first_session', 'Getting Started', 'Complete your first focus session', 'milestone', 'session_count', 1, 100, 'play-circle', 'green'),
('first_week', 'Week One', 'Complete 7 focus sessions', 'milestone', 'session_count', 7, 300, 'calendar', 'blue'),
('first_month', 'Monthly Momentum', 'Complete 30 focus sessions', 'milestone', 'session_count', 30, 1000, 'trophy', 'gold'),

-- Focus Quality Achievements
('high_focus_master', 'Focus Master', 'Achieve high focus quality 10 times', 'focus', 'high_quality_sessions', 10, 500, 'target', 'purple'),
('perfectionist', 'Perfectionist', 'Complete a session with 100% completion rate and 10/10 productivity', 'focus', 'perfect_session', 1, 250, 'star', 'gold'),
('flow_state', 'Flow State', 'Complete 5 consecutive sessions with high focus quality', 'focus', 'consecutive_high_quality', 5, 750, 'zap', 'purple'),

-- Streak Achievements
('daily_habit', 'Daily Habit', 'Maintain a 7-day daily session streak', 'streak', 'daily_streak', 7, 400, 'calendar-check', 'green'),
('consistency_champion', 'Consistency Champion', 'Maintain a 30-day daily session streak', 'streak', 'daily_streak', 30, 2000, 'award', 'gold'),
('unstoppable', 'Unstoppable', 'Maintain a 100-day daily session streak', 'streak', 'daily_streak', 100, 10000, 'fire', 'red'),

-- Time-based Achievements
('focused_hour', 'Focused Hour', 'Complete 60 minutes of focused work in a single session', 'time', 'single_session_duration', 60, 200, 'clock', 'blue'),
('marathon_focus', 'Marathon Focus', 'Complete 120 minutes of focused work in a single session', 'time', 'single_session_duration', 120, 500, 'activity', 'red'),
('century_club', 'Century Club', 'Accumulate 100 hours of total focus time', 'time', 'total_focus_time', 6000, 5000, 'layers', 'gold'), -- 100 hours in minutes

-- Productivity Achievements
('productivity_pro', 'Productivity Pro', 'Maintain an average productivity score of 8+ over 10 sessions', 'improvement', 'avg_productivity_score', 8, 600, 'trending-up', 'blue'),
('zen_master', 'Zen Master', 'Complete 20 sessions with 0 interruptions each', 'improvement', 'zero_interruption_sessions', 20, 1000, 'minimize', 'purple'),
('improvement_guru', 'Improvement Guru', 'Show consistent improvement over 4 weeks', 'improvement', 'weekly_improvement_streak', 4, 800, 'bar-chart', 'green'),

-- Special Achievements
('music_lover', 'Music Lover', 'Complete 50 sessions with music playlists', 'special', 'sessions_with_music', 50, 400, 'headphones', 'pink'),
('early_bird', 'Early Bird', 'Complete 10 sessions before 9 AM', 'special', 'morning_sessions', 10, 300, 'sunrise', 'yellow'),
('night_owl', 'Night Owl', 'Complete 10 sessions after 8 PM', 'special', 'evening_sessions', 10, 300, 'moon', 'indigo'),

-- Milestone Achievements
('focus_apprentice', 'Focus Apprentice', 'Reach level 5 in focus mastery', 'milestone', 'user_level', 5, 500, 'user-plus', 'green'),
('focus_expert', 'Focus Expert', 'Reach level 15 in focus mastery', 'milestone', 'user_level', 15, 1500, 'user-check', 'blue'),
('focus_legend', 'Focus Legend', 'Reach level 30 in focus mastery', 'milestone', 'user_level', 30, 5000, 'crown', 'gold')

ON CONFLICT (achievement_key) DO NOTHING;

-- Insert sample music playlists
INSERT INTO music_playlists (external_id, title, description, track_count, is_focus_suitable, focus_effectiveness_score) VALUES
('demo_playlist_1', 'Lo-Fi Study Beats', 'Chill lo-fi hip hop for deep focus', 45, TRUE, 8.5),
('demo_playlist_2', 'Ambient Focus', 'Atmospheric sounds for concentration', 32, TRUE, 9.2),
('demo_playlist_3', 'Classical Focus', 'Instrumental classical music for work', 28, TRUE, 8.8),
('demo_playlist_4', 'Nature Sounds', 'Rain, ocean, and forest sounds', 15, TRUE, 7.9),
('demo_playlist_5', 'Electronic Chill', 'Downtempo electronic music', 38, TRUE, 8.1)
ON CONFLICT (external_id) DO NOTHING;

-- Insert sample focus sessions for demo
INSERT INTO focus_sessions (
    user_id, start_time, end_time, planned_duration, actual_duration,
    completion_rate, productivity_score, interruptions, focus_quality,
    session_type, playlist_id, playlist_name, experience_points
) VALUES
-- Recent sessions for demo purposes
('demo_user', CURRENT_TIMESTAMP - INTERVAL '2 hours', CURRENT_TIMESTAMP - INTERVAL '1 hour 10 minutes', 50, 50, 1.0, 9.0, 0, 'high', 'work', 'demo_playlist_1', 'Lo-Fi Study Beats', 190),
('demo_user', CURRENT_TIMESTAMP - INTERVAL '1 day 3 hours', CURRENT_TIMESTAMP - INTERVAL '1 day 2 hours 15 minutes', 50, 45, 0.9, 7.5, 2, 'medium', 'work', 'demo_playlist_2', 'Ambient Focus', 165),
('demo_user', CURRENT_TIMESTAMP - INTERVAL '2 days 4 hours', CURRENT_TIMESTAMP - INTERVAL '2 days 3 hours 20 minutes', 50, 40, 0.8, 6.5, 3, 'medium', 'work', 'demo_playlist_3', 'Classical Focus', 145),
('demo_user', CURRENT_TIMESTAMP - INTERVAL '3 days 2 hours', CURRENT_TIMESTAMP - INTERVAL '3 days 1 hour 5 minutes', 50, 55, 1.0, 8.5, 1, 'high', 'work', 'demo_playlist_1', 'Lo-Fi Study Beats', 175),
('demo_user', CURRENT_TIMESTAMP - INTERVAL '4 days 5 hours', CURRENT_TIMESTAMP - INTERVAL '4 days 4 hours 30 minutes', 50, 30, 0.6, 5.0, 5, 'low', 'work', NULL, NULL, 110);

-- Initialize user streaks
INSERT INTO user_streaks (user_id, streak_type, current_streak, longest_streak, last_activity_date) VALUES
('demo_user', 'daily_sessions', 3, 7, CURRENT_DATE),
('demo_user', 'weekly_goals', 2, 4, CURRENT_DATE),
('demo_user', 'consistency', 5, 12, CURRENT_DATE)
ON CONFLICT (user_id, streak_type) DO NOTHING;

-- Grant some achievements to demo user
INSERT INTO user_achievements (user_id, achievement_id, current_progress, is_unlocked, unlocked_at)
SELECT 'demo_user', id, requirement_value, TRUE, CURRENT_TIMESTAMP - INTERVAL '1 day'
FROM achievement_definitions
WHERE achievement_key IN ('first_session', 'getting_started', 'daily_habit')
ON CONFLICT (user_id, achievement_id) DO NOTHING;
EOF

echo "✅ Seed data and achievements created"
```

**Deliverable**: Complete seed data with achievements and sample sessions  
**Time Estimate**: 20 minutes  
**Dependencies**: Task C1.1 complete

#### **Task C2: React Frontend Foundation**

**Overview**: Create the basic React application with TypeScript, core components, and API integration setup.

##### **C2.1: React Application Setup**

**Command Sequence**:

```bash
cd ../../ui/focus_app

# Create package.json
cat > package.json << 'EOF'
{
  "name": "focus-flow-app",
  "version": "1.0.0",
  "description": "Focus Flow - Interactive Productivity Timer Frontend",
  "type": "module",
  "scripts": {
    "dev": "vite",
    "build": "tsc && vite build",
    "preview": "vite preview",
    "test": "vitest",
    "test:coverage": "vitest run --coverage",
    "lint": "eslint src --ext ts,tsx --report-unused-disable-directives --max-warnings 0",
    "lint:fix": "eslint src --ext ts,tsx --fix"
  },
  "dependencies": {
    "react": "^18.2.0",
    "react-dom": "^18.2.0",
    "react-router-dom": "^6.20.0",
    "axios": "^1.6.0",
    "@tanstack/react-query": "^5.8.0",
    "zustand": "^4.4.0",
    "framer-motion": "^10.16.0",
    "lucide-react": "^0.294.0",
    "date-fns": "^2.30.0",
    "recharts": "^2.8.0",
    "@headlessui/react": "^1.7.0",
    "clsx": "^2.0.0",
    "tailwind-merge": "^2.0.0"
  },
  "devDependencies": {
    "@types/react": "^18.2.0",
    "@types/react-dom": "^18.2.0",
    "@typescript-eslint/eslint-plugin": "^6.0.0",
    "@typescript-eslint/parser": "^6.0.0",
    "@vitejs/plugin-react": "^4.1.0",
    "eslint": "^8.53.0",
    "eslint-plugin-react-hooks": "^4.6.0",
    "eslint-plugin-react-refresh": "^0.4.0",
    "typescript": "^5.2.0",
    "vite": "^4.5.0",
    "vitest": "^0.34.0",
    "tailwindcss": "^3.3.0",
    "autoprefixer": "^10.4.0",
    "postcss": "^8.4.0",
    "@testing-library/react": "^13.4.0",
    "@testing-library/jest-dom": "^6.1.0",
    "@testing-library/user-event": "^14.5.0"
  }
}
EOF

# Create TypeScript configuration
cat > tsconfig.json << 'EOF'
{
  "compilerOptions": {
    "target": "ES2020",
    "useDefineForClassFields": true,
    "lib": ["ES2020", "DOM", "DOM.Iterable"],
    "module": "ESNext",
    "skipLibCheck": true,

    /* Bundler mode */
    "moduleResolution": "bundler",
    "allowImportingTsExtensions": true,
    "resolveJsonModule": true,
    "isolatedModules": true,
    "noEmit": true,
    "jsx": "react-jsx",

    /* Linting */
    "strict": true,
    "noUnusedLocals": true,
    "noUnusedParameters": true,
    "noFallthroughCasesInSwitch": true,

    /* Path mapping */
    "baseUrl": ".",
    "paths": {
      "@/*": ["src/*"],
      "@/components/*": ["src/components/*"],
      "@/services/*": ["src/services/*"],
      "@/hooks/*": ["src/hooks/*"],
      "@/types/*": ["src/types/*"],
      "@/utils/*": ["src/utils/*"]
    }
  },
  "include": ["src"],
  "references": [{ "path": "./tsconfig.node.json" }]
}
EOF

# Create Vite configuration
cat > vite.config.ts << 'EOF'
import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import path from 'path'

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [react()],
  resolve: {
    alias: {
      "@": path.resolve(__dirname, "./src"),
    },
  },
  server: {
    port: 3000,
    host: true,
    proxy: {
      '/api': {
        target: 'http://localhost:8001',
        changeOrigin: true,
      },
      '/ws': {
        target: 'ws://localhost:8001',
        ws: true,
      }
    }
  },
  build: {
    outDir: 'dist',
    sourcemap: true,
  }
})
EOF

# Create Tailwind CSS configuration
cat > tailwind.config.js << 'EOF'
/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        primary: {
          50: '#eff6ff',
          100: '#dbeafe',
          200: '#bfdbfe',
          300: '#93c5fd',
          400: '#60a5fa',
          500: '#3b82f6',
          600: '#2563eb',
          700: '#1d4ed8',
          800: '#1e40af',
          900: '#1e3a8a',
        },
        focus: {
          50: '#f0fdf4',
          100: '#dcfce7',
          200: '#bbf7d0',
          300: '#86efac',
          400: '#4ade80',
          500: '#22c55e',
          600: '#16a34a',
          700: '#15803d',
          800: '#166534',
          900: '#14532d',
        }
      },
      animation: {
        'pulse-slow': 'pulse 3s cubic-bezier(0.4, 0, 0.6, 1) infinite',
        'bounce-gentle': 'bounce 2s infinite',
        'spin-slow': 'spin 3s linear infinite',
      }
    },
  },
  plugins: [],
}
EOF

echo "✅ React application configuration created"
```

**Deliverable**: Complete React application setup with TypeScript and Tailwind CSS  
**Time Estimate**: 15 minutes  
**Dependencies**: Task C1.2 complete

##### **C2.2: Core Application Structure and Types**

**Command Sequence**:

```bash
# Create main application entry point
cat > src/main.tsx << 'EOF'
import React from 'react'
import ReactDOM from 'react-dom/client'
import App from './App.tsx'
import './index.css'

ReactDOM.createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    <App />
  </React.StrictMode>,
)
EOF

# Create main CSS file
cat > src/index.css << 'EOF'
@tailwind base;
@tailwind components;
@tailwind utilities;

@layer base {
  html {
    font-family: 'Inter', system-ui, sans-serif;
  }

  body {
    @apply antialiased;
  }
}

@layer components {
  .btn {
    @apply px-4 py-2 rounded-lg font-medium transition-all duration-200;
  }

  .btn-primary {
    @apply bg-primary-600 hover:bg-primary-700 text-white;
  }

  .btn-secondary {
    @apply bg-gray-200 hover:bg-gray-300 text-gray-900;
  }

  .btn-success {
    @apply bg-focus-600 hover:bg-focus-700 text-white;
  }

  .card {
    @apply bg-white rounded-xl shadow-sm border border-gray-200;
  }

  .card-header {
    @apply px-6 py-4 border-b border-gray-200;
  }

  .card-body {
    @apply px-6 py-4;
  }
}

@layer utilities {
  .text-gradient {
    @apply bg-gradient-to-r from-primary-600 to-focus-600 bg-clip-text text-transparent;
  }

  .focus-ring {
    @apply focus:outline-none focus:ring-2 focus:ring-primary-500 focus:ring-offset-2;
  }
}

/* Custom animations */
@keyframes breathe {
  0%, 100% { transform: scale(1); opacity: 0.7; }
  50% { transform: scale(1.05); opacity: 1; }
}

.animate-breathe {
  animation: breathe 3s ease-in-out infinite;
}

@keyframes progress-pulse {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.5; }
}

.animate-progress-pulse {
  animation: progress-pulse 2s ease-in-out infinite;
}
EOF

# Create TypeScript types
cat > src/types/focus.ts << 'EOF'
// Focus Flow Type Definitions
// Core types for focus sessions and user interactions

export interface FocusSession {
  id: number;
  session_uuid: string;
  user_id: string;
  start_time: string;
  end_time?: string;
  planned_duration: number;
  actual_duration?: number;
  completion_rate?: number;
  productivity_score?: number;
  interruptions: number;
  interruption_types?: string[];
  focus_quality?: 'high' | 'medium' | 'low';
  session_type: 'work' | 'break' | 'deep_work';
  time_of_day_category?: 'morning' | 'afternoon' | 'evening';
  playlist_id?: string;
  playlist_name?: string;
  ai_insights?: string;
  optimal_time_suggestions?: string;
  improvement_recommendations?: string[];
  experience_points: number;
  achievements_unlocked?: string[];
  created_at: string;
  updated_at: string;
}

export interface SessionStartRequest {
  duration: number;
  session_type: string;
  playlist_id?: string;
  user_id: string;
}

export interface SessionCompletionRequest {
  completion_rate: number;
  productivity_score: number;
  interruptions: number;
  interruption_types?: string[];
}

export interface TimerState {
  sessionId: number | null;
  timeRemaining: number;
  totalTime: number;
  isActive: boolean;
  isPaused: boolean;
  progress: number;
  interruptions: number;
  startTime: Date | null;
}

export interface SessionStats {
  totalSessions: number;
  totalFocusTime: number; // in minutes
  averageCompletion: number;
  averageProductivity: number;
  currentStreak: number;
  longestStreak: number;
}
EOF

cat > src/types/api.ts << 'EOF'
// API Response Types

export interface ApiResponse<T> {
  data: T;
  message?: string;
  success: boolean;
}

export interface ApiError {
  message: string;
  detail?: string;
  status?: number;
}

export interface PaginatedResponse<T> {
  items: T[];
  total: number;
  page: number;
  size: number;
  pages: number;
}
EOF

# Create API client
cat > src/services/apiClient.ts << 'EOF'
import axios, { AxiosResponse } from 'axios';
import type { ApiResponse, ApiError } from '@/types/api';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || '/api/v1';

// Create axios instance with default configuration
const apiClient = axios.create({
  baseURL: API_BASE_URL,
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor for adding auth tokens (future use)
apiClient.interceptors.request.use(
  (config) => {
    // Add auth token when available
    const token = localStorage.getItem('focus_flow_token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor for error handling
apiClient.interceptors.response.use(
  (response: AxiosResponse) => {
    return response;
  },
  (error) => {
    const apiError: ApiError = {
      message: error.response?.data?.message || error.message || 'An error occurred',
      detail: error.response?.data?.detail,
      status: error.response?.status,
    };

    // Handle specific error codes
    if (error.response?.status === 401) {
      // Handle unauthorized access
      localStorage.removeItem('focus_flow_token');
      window.location.href = '/login';
    }

    return Promise.reject(apiError);
  }
);

export default apiClient;

// Helper function for making API calls with proper typing
export async function apiCall<T>(
  method: 'GET' | 'POST' | 'PUT' | 'DELETE',
  url: string,
  data?: any
): Promise<T> {
  const response = await apiClient.request<T>({
    method,
    url,
    data,
  });

  return response.data;
}
EOF

# Create focus session service
cat > src/services/focusSessionService.ts << 'EOF'
import apiClient, { apiCall } from './apiClient';
import type {
  FocusSession,
  SessionStartRequest,
  SessionCompletionRequest
} from '@/types/focus';

class FocusSessionService {
  private readonly basePath = '/sessions';

  /**
   * Start a new focus session
   */
  async startSession(request: SessionStartRequest): Promise<FocusSession> {
    return apiCall<FocusSession>('POST', `${this.basePath}/start`, request);
  }

  /**
   * Complete a focus session
   */
  async completeSession(sessionId: number, completion: SessionCompletionRequest): Promise<FocusSession> {
    return apiCall<FocusSession>('PUT', `${this.basePath}/${sessionId}/complete`, completion);
  }

  /**
   * Get a specific session by ID
   */
  async getSession(sessionId: number): Promise<FocusSession> {
    return apiCall<FocusSession>('GET', `${this.basePath}/${sessionId}`);
  }

  /**
   * Get sessions for a user
   */
  async getUserSessions(userId: string, limit: number = 50): Promise<FocusSession[]> {
    return apiCall<FocusSession[]>('GET', `${this.basePath}/user/${userId}?limit=${limit}`);
  }

  /**
   * Delete a session
   */
  async deleteSession(sessionId: number): Promise<void> {
    return apiCall<void>('DELETE', `${this.basePath}/${sessionId}`);
  }
}

export const focusSessionService = new FocusSessionService();
EOF

echo "✅ Core application structure and API services created"
```

**Deliverable**: Complete application foundation with types and API integration  
**Time Estimate**: 20 minutes  
**Dependencies**: Task C2.1 complete

---

## 🎯 Success Criteria & Next Steps

### **Minimum Viable Product (MVP) Completion Criteria**

✅ **Repository Structure**: Complete codebase organization following enterprise patterns  
✅ **GitHub Integration**: Repository created and pushed to soundstate/focus-flow_DEMO  
✅ **Focus Engine Service**: FastAPI service with session management endpoints  
✅ **Database Infrastructure**: PostgreSQL schema with focus sessions, achievements, and analytics  
✅ **React Frontend Foundation**: TypeScript application with API integration setup  
✅ **Development Environment**: Docker Compose setup for local development  
✅ **Documentation**: Comprehensive README and development guides

### **Total Estimated Time**: 4-5 hours for complete foundation setup

### **Recommended Execution Strategy**

Execute tasks in sequence as dependencies require:

1. **Repository Setup** (Tasks A1-A2): 60 minutes - Complete project structure and GitHub setup
2. **Backend Foundation** (Task B1): 70 minutes - Focus Engine service with API endpoints
3. **Database Setup** (Task C1): 45 minutes - Complete database schema and seed data
4. **Frontend Foundation** (Task C2): 35 minutes - React application with API integration

### **Post-Foundation Development Priorities**

#### **Phase 1: Core Functionality** (Next 2-3 hours)

1. **Frontend Timer Component**: Interactive focus timer with start/pause/complete functionality
2. **WebSocket Integration**: Real-time timer synchronization between browser and backend
3. **Session Management**: Complete session workflow from start to completion with AI insights
4. **Basic UI Components**: Progress ring, session controls, and completion summary

#### **Phase 2: Advanced Features** (Next 4-5 hours)

1. **Music Integration**: YouTube Music API client and playlist management
2. **AI Insights Service**: Session analysis and productivity coaching endpoints
3. **Analytics Dashboard**: Session history, productivity trends, and performance metrics
4. **Gamification**: Achievement system, streak tracking, and experience points

#### **Phase 3: Polish & Testing** (Next 2-3 hours)

1. **Animations**: Focus visualizer, progress animations, and achievement popups
2. **Responsive Design**: Mobile-friendly interface and touch interactions
3. **Error Handling**: Comprehensive error states and user feedback
4. **Testing**: Unit tests, integration tests, and E2E testing setup

---

## 🚀 Ready for Warp Agent Execution!

**This task list provides complete step-by-step instructions for setting up the Focus Flow productivity application following enterprise development patterns. Each task includes detailed commands, configuration files, and deliverables to ensure successful implementation.**

**Repository URL**: `https://github.com/soundstate/focus-flow_DEMO`

**Development Server**: `http://localhost:3000` (Frontend) + `http://localhost:8001` (API)

**Next Phase**: After completing these foundation tasks, the agent should be ready to implement the interactive timer component and begin core feature development.
