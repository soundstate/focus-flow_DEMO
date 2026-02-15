I have created the following plan after thorough exploration and analysis of the codebase. Follow the below plan verbatim. Trust the files and references. Do not re-verify what's written in the plan. Explore only when absolutely necessary. First implement all the proposed file changes and then I'll review all the changes together at the end.

### Observations

The project has a solid foundation with a production-ready Focus Engine service (Pomodoro timer with analytics, templates, notifications) and a React/TypeScript frontend with basic structure. However, the brainstorm document envisions a much broader **Weekly Scheduling App** with life balance features, while the current implementation is focused on Pomodoro timer functionality. Four microservices (ai_insights, analytics, game_engine, music_control) have directory structures but are empty. The gap between vision and implementation requires a phased approach that builds on existing strengths while gradually expanding toward the full vision.

### Approach

Transform the brainstorm document into an actionable development plan by: (1) Implementing the four empty microservices to complete the core Pomodoro app features, (2) Enhancing the frontend to integrate all services with real API connections, (3) Extending the data model to support scheduling features (goals, weekly schedules, onboarding), (4) Adding new features progressively from simple (onboarding, goals) to complex (AI scheduling, calendar integration), and (5) Maintaining the microservices architecture while ensuring proper service communication patterns.

### Reasoning

I explored the repository structure, read the brainstorm document, examined the PROGRESS.md to understand current implementation status, reviewed the Focus Engine service (models, services, routers), analyzed the frontend structure (components, Redux slices, API services), and checked the empty microservices to understand the architectural vision. This revealed a well-architected foundation ready for expansion.

## Proposed File Changes

### services\game_engine\main.py(MODIFY)

References: 

- services\focus_engine\main.py

Create the FastAPI application for the Game Engine service with:
- Application initialization with CORS middleware and lifespan management
- Health check endpoint at `/health`
- Include routers for achievements, levels, streaks, and leaderboards from `routers/` directory
- Configure settings from `config/settings.py` (to be created)
- Set up logging configuration
- Define root endpoint with service information
- Configure uvicorn server with host, port (8001), and reload settings

### services\game_engine\config\settings.py(NEW)

References: 

- services\focus_engine\config\settings.py

Create Pydantic settings configuration for Game Engine service:
- Define Settings class with BaseSettings inheritance
- Include debug_mode, log_level, environment settings
- Database URL for storing achievements, levels, streaks
- Redis URL for caching leaderboard data
- API prefix and CORS origins
- XP calculation settings (base_xp_per_session, completion_bonus, streak_multiplier)
- Achievement unlock thresholds
- Leaderboard configuration (refresh_interval, max_entries)
- Environment variable prefix 'GAME_ENGINE_'
- get_settings() factory function

### services\game_engine\models\achievement_models.py(MODIFY)

References: 

- services\focus_engine\models\session_models.py

Define achievement data models:
- Achievement SQLAlchemy model with fields: id, achievement_id (UUID), user_id, achievement_type (first_session, streak_3, streak_7, streak_30, total_sessions_10, total_sessions_50, total_sessions_100, deep_work_master, early_bird, night_owl), title, description, icon, unlocked_at, progress_current, progress_required, is_unlocked
- AchievementResponse Pydantic model for API responses
- AchievementProgress Pydantic model for tracking progress
- UserAchievementStats Pydantic model with total_unlocked, total_available, completion_percentage, recent_unlocks
- AchievementCategory enum (MILESTONE, STREAK, CONSISTENCY, MASTERY, TIME_BASED)

### services\game_engine\models\level_models.py(MODIFY)

References: 

- services\focus_engine\models\session_models.py

Define level and experience data models:
- UserLevel SQLAlchemy model with fields: id, user_id, current_level, current_xp, total_xp, xp_to_next_level, level_up_at (timestamp), created_at, updated_at
- LevelResponse Pydantic model for API responses
- LevelUpEvent Pydantic model with level_reached, xp_earned, rewards_unlocked, timestamp
- ExperienceGain Pydantic model with session_id, base_xp, bonus_xp, total_xp, reason
- Level progression calculation constants (XP_BASE = 100, XP_MULTIPLIER = 1.5 per level)

### services\game_engine\models\streak_models.py(MODIFY)

References: 

- services\focus_engine\models\session_models.py

Define streak tracking data models:
- UserStreak SQLAlchemy model with fields: id, user_id, current_streak, longest_streak, last_session_date, streak_start_date, total_sessions, created_at, updated_at
- StreakResponse Pydantic model for API responses
- StreakUpdate Pydantic model with previous_streak, new_streak, is_broken, is_milestone
- StreakMilestone Pydantic model with milestone_type (3_day, 7_day, 30_day, 100_day), reached_at, reward
- Streak calculation logic constants (STREAK_GRACE_PERIOD_HOURS = 36 for allowing one missed day)

### services\game_engine\services\achievement_service.py(MODIFY)

References: 

- services\focus_engine\services\session_service.py

Implement achievement service business logic:
- AchievementService class with methods:
  - check_and_unlock_achievements(user_id, session_data) - evaluates all achievement criteria after session completion
  - get_user_achievements(user_id) - retrieves all achievements with unlock status
  - get_achievement_progress(user_id, achievement_id) - returns progress toward specific achievement
  - calculate_achievement_stats(user_id) - computes overall achievement statistics
- Achievement evaluation logic for each type (first session, streaks, totals, time-based)
- Integration with Focus Engine session data via HTTP client
- Achievement unlock notification generation
- Progress tracking and persistence

### services\game_engine\services\level_service.py(MODIFY)

References: 

- services\focus_engine\services\session_service.py

Implement level and experience service:
- LevelService class with methods:
  - award_experience(user_id, session_id, session_data) - calculates and awards XP based on session completion
  - calculate_xp_for_session(session_data) - determines XP amount (base + bonuses for completion rate, duration, quality)
  - check_level_up(user_id) - evaluates if user leveled up and triggers level-up event
  - get_user_level(user_id) - retrieves current level information
  - get_level_history(user_id) - returns level progression history
- XP calculation formula: base_xp * completion_rate * quality_multiplier + streak_bonus
- Level-up threshold calculation: XP_BASE * (XP_MULTIPLIER ^ level)
- Level-up reward generation (unlock new templates, themes, features)

### services\game_engine\services\streak_service.py(MODIFY)

References: 

- services\focus_engine\services\session_service.py

Implement streak tracking service:
- StreakService class with methods:
  - update_streak(user_id, session_date) - updates streak based on new session
  - check_streak_status(user_id) - evaluates if streak is active or broken
  - get_user_streak(user_id) - retrieves current streak information
  - check_streak_milestones(user_id) - identifies milestone achievements
  - calculate_streak_bonus(streak_count) - computes XP multiplier for active streaks
- Streak logic: increment if session within 36 hours of last, break if gap exceeds grace period
- Milestone detection (3, 7, 30, 100 day streaks)
- Streak recovery suggestions when broken
- Integration with achievement service for streak-based achievements

### services\game_engine\routers\achievements.py(MODIFY)

References: 

- services\focus_engine\routers\sessions.py

Create achievements router with endpoints:
- GET `/api/v1/achievements/users/{user_id}` - list all achievements with unlock status
- GET `/api/v1/achievements/users/{user_id}/unlocked` - get only unlocked achievements
- GET `/api/v1/achievements/users/{user_id}/progress` - get progress toward all achievements
- GET `/api/v1/achievements/users/{user_id}/stats` - get achievement statistics
- POST `/api/v1/achievements/check/{user_id}` - manually trigger achievement check (for testing)
- Use AchievementService for business logic
- Return appropriate response models
- Include error handling and validation

### services\game_engine\routers\levels.py(MODIFY)

References: 

- services\focus_engine\routers\sessions.py

Create levels router with endpoints:
- GET `/api/v1/levels/users/{user_id}` - get current level and XP
- GET `/api/v1/levels/users/{user_id}/history` - get level progression history
- POST `/api/v1/levels/users/{user_id}/award-xp` - award XP for session completion (called by Focus Engine webhook)
- GET `/api/v1/levels/leaderboard` - get XP leaderboard (top users by level/XP)
- Use LevelService for business logic
- Include level-up event notifications
- Return LevelResponse and related models

### services\game_engine\routers\streaks.py(MODIFY)

References: 

- services\focus_engine\routers\sessions.py

Create streaks router with endpoints:
- GET `/api/v1/streaks/users/{user_id}` - get current streak information
- GET `/api/v1/streaks/users/{user_id}/milestones` - get achieved streak milestones
- POST `/api/v1/streaks/users/{user_id}/update` - update streak after session (called by Focus Engine)
- GET `/api/v1/streaks/leaderboard` - get streak leaderboard (longest current streaks)
- Use StreakService for business logic
- Include streak milestone notifications
- Return StreakResponse and related models

### services\game_engine\routers\leaderboards.py(MODIFY)

References: 

- services\focus_engine\routers\analytics.py

Create leaderboards router with endpoints:
- GET `/api/v1/leaderboards/xp` - get XP leaderboard with pagination
- GET `/api/v1/leaderboards/streaks` - get streak leaderboard
- GET `/api/v1/leaderboards/sessions` - get total sessions leaderboard
- GET `/api/v1/leaderboards/users/{user_id}/rank` - get user's rank across all leaderboards
- Query parameters: limit (default 50), offset, time_period (all_time, monthly, weekly)
- Use Redis caching for leaderboard data (refresh every 5 minutes)
- Return LeaderboardEntry models with rank, user_id, username, score, change_from_previous

### services\game_engine\database\connection.py(NEW)

References: 

- services\focus_engine\database\connection.py

Create database connection module:
- Import SQLAlchemy create_engine, sessionmaker, declarative_base
- Create Base = declarative_base() for ORM models
- Create engine from settings.database_url
- Create SessionLocal = sessionmaker(bind=engine)
- Define get_db() dependency function for FastAPI that yields database session
- Include connection pooling configuration
- Add create_tables() function to initialize database schema

### services\music_control\main.py(MODIFY)

References: 

- services\focus_engine\main.py

Create the FastAPI application for Music Control service:
- Application initialization with CORS middleware and lifespan management
- Health check endpoint at `/health`
- Include routers for playlists, playback, and discovery from `routers/` directory
- Configure settings from `config/settings.py` (to be created)
- Set up logging configuration
- Define root endpoint with service information
- Configure uvicorn server with host, port (8002), and reload settings
- Initialize music client connections (Spotify, YouTube Music) on startup

### services\music_control\config\settings.py(NEW)

References: 

- services\focus_engine\config\settings.py

Create Pydantic settings configuration for Music Control service:
- Define Settings class with BaseSettings inheritance
- Include debug_mode, log_level, environment settings
- Database URL for storing playlist preferences and effectiveness data
- Spotify API credentials (client_id, client_secret, redirect_uri)
- YouTube Music API credentials (api_key, oauth_client_id, oauth_client_secret)
- API prefix and CORS origins
- Music service preferences (default_service, enable_spotify, enable_youtube_music)
- Playlist recommendation settings (min_duration, max_duration, focus_genres)
- Environment variable prefix 'MUSIC_CONTROL_'
- get_settings() factory function

### services\music_control\models\playlist_models.py(MODIFY)

References: 

- services\focus_engine\models\session_models.py

Define playlist data models:
- Playlist SQLAlchemy model with fields: id, playlist_id (UUID), user_id, name, description, source (spotify, youtube_music, custom), external_id, track_count, duration_minutes, genre, mood, focus_effectiveness_score, usage_count, created_at, updated_at
- PlaylistResponse Pydantic model for API responses
- PlaylistCreate Pydantic model for creating playlists
- PlaylistRecommendation Pydantic model with playlist_id, name, reason, effectiveness_score, match_score
- PlaylistEffectiveness Pydantic model with playlist_id, avg_productivity_score, avg_completion_rate, total_sessions, last_used

### services\music_control\models\track_models.py(MODIFY)

Define track data models:
- Track Pydantic model with fields: track_id, title, artist, album, duration_seconds, external_url, preview_url, genre, tempo, energy_level
- TrackResponse Pydantic model for API responses
- NowPlaying Pydantic model with track, playlist_id, position, is_playing, progress_seconds
- PlaybackState Pydantic model with is_playing, current_track, playlist_id, volume, shuffle, repeat_mode

### services\music_control\clients\spotify_client.py(MODIFY)

Implement Spotify API client:
- SpotifyClient class with OAuth2 authentication flow
- Methods:
  - authenticate(code) - exchange authorization code for access token
  - refresh_token(refresh_token) - refresh expired access token
  - get_user_playlists(user_id) - fetch user's playlists
  - search_playlists(query, limit) - search for playlists by keyword
  - get_playlist_tracks(playlist_id) - get tracks in a playlist
  - play_playlist(playlist_id, device_id) - start playlist playback
  - pause_playback() - pause current playback
  - resume_playback() - resume playback
  - get_playback_state() - get current playback information
- Use requests library for HTTP calls to Spotify Web API
- Handle rate limiting and token expiration
- Store tokens securely in database

### services\music_control\clients\youtube_music_client.py(MODIFY)

Implement YouTube Music API client:
- YouTubeMusicClient class with OAuth2 authentication
- Methods:
  - authenticate(code) - exchange authorization code for access token
  - get_user_playlists(user_id) - fetch user's playlists
  - search_playlists(query, limit) - search for playlists
  - get_playlist_tracks(playlist_id) - get tracks in a playlist
  - create_playlist(name, description, tracks) - create new playlist
- Use ytmusicapi library or direct YouTube Data API v3 calls
- Handle API quotas and rate limiting
- Store authentication tokens in database

### services\music_control\services\playlist_service.py(MODIFY)

References: 

- services\focus_engine\services\template_service.py

Implement playlist management service:
- PlaylistService class with methods:
  - get_user_playlists(user_id, source) - retrieve playlists from specified source or all sources
  - search_playlists(query, user_id) - search across all connected music services
  - get_recommended_playlists(user_id, session_type) - recommend playlists based on session type and past effectiveness
  - save_playlist(user_id, playlist_data) - save playlist to user's library
  - track_playlist_usage(user_id, playlist_id, session_id) - record playlist usage for effectiveness tracking
  - calculate_playlist_effectiveness(playlist_id) - compute effectiveness score based on session outcomes
- Integrate with SpotifyClient and YouTubeMusicClient
- Use effectiveness data from Focus Engine sessions
- Implement recommendation algorithm based on genre, mood, past success

### services\music_control\services\effectiveness_tracker.py(MODIFY)

References: 

- services\focus_engine\services\analytics_service.py

Implement music effectiveness tracking service:
- EffectivenessTracker class with methods:
  - record_session_outcome(playlist_id, session_id, productivity_score, completion_rate) - store session results
  - calculate_effectiveness_score(playlist_id) - compute weighted average of productivity metrics
  - get_best_playlists_for_user(user_id, session_type) - identify most effective playlists
  - get_effectiveness_trends(playlist_id) - analyze effectiveness over time
  - compare_playlists(playlist_ids) - compare effectiveness across multiple playlists
- Effectiveness formula: (avg_productivity_score * 0.6) + (avg_completion_rate * 0.4)
- Weight recent sessions more heavily (exponential decay)
- Minimum session count threshold (5) before considering playlist effective

### services\music_control\routers\playlists.py(MODIFY)

References: 

- services\focus_engine\routers\templates.py

Create playlists router with endpoints:
- GET `/api/v1/playlists/users/{user_id}` - get user's playlists from all sources
- GET `/api/v1/playlists/users/{user_id}/recommendations` - get recommended playlists for session type
- GET `/api/v1/playlists/{playlist_id}` - get playlist details and tracks
- POST `/api/v1/playlists/users/{user_id}/save` - save playlist to user's library
- GET `/api/v1/playlists/{playlist_id}/effectiveness` - get effectiveness metrics
- POST `/api/v1/playlists/search` - search playlists across services
- Use PlaylistService for business logic
- Return PlaylistResponse and PlaylistRecommendation models
- Include pagination for large result sets

### services\music_control\routers\playback.py(MODIFY)

Create playback control router with endpoints:
- POST `/api/v1/playback/play` - start playing a playlist (body: playlist_id, device_id)
- POST `/api/v1/playback/pause` - pause current playback
- POST `/api/v1/playback/resume` - resume playback
- POST `/api/v1/playback/next` - skip to next track
- POST `/api/v1/playback/previous` - go to previous track
- GET `/api/v1/playback/state` - get current playback state
- POST `/api/v1/playback/volume` - set volume level (0-100)
- Use SpotifyClient or YouTubeMusicClient based on active service
- Return PlaybackState and NowPlaying models
- Handle errors when no device is active

### services\music_control\routers\discovery.py(MODIFY)

Create music discovery router with endpoints:
- GET `/api/v1/discovery/focus-playlists` - discover curated focus playlists
- GET `/api/v1/discovery/by-genre/{genre}` - find playlists by genre (lo-fi, classical, ambient, etc.)
- GET `/api/v1/discovery/by-mood/{mood}` - find playlists by mood (calm, energetic, focused)
- GET `/api/v1/discovery/trending` - get trending focus playlists
- GET `/api/v1/discovery/similar/{playlist_id}` - find similar playlists
- Use external music service APIs for discovery
- Filter results for focus-appropriate content (instrumental, low-distraction)
- Return PlaylistResponse models with discovery metadata

### services\music_control\database\connection.py(NEW)

References: 

- services\focus_engine\database\connection.py

Create database connection module:
- Import SQLAlchemy create_engine, sessionmaker, declarative_base
- Create Base = declarative_base() for ORM models
- Create engine from settings.database_url
- Create SessionLocal = sessionmaker(bind=engine)
- Define get_db() dependency function for FastAPI
- Include connection pooling configuration
- Add create_tables() function to initialize database schema

### services\ai_insights\main.py(MODIFY)

References: 

- services\focus_engine\main.py

Create the FastAPI application for AI Insights service:
- Application initialization with CORS middleware and lifespan management
- Health check endpoint at `/health`
- Include routers for patterns, insights, and coaching from `routers/` directory
- Configure settings from `config/settings.py` (to be created)
- Set up logging configuration
- Define root endpoint with service information
- Configure uvicorn server with host, port (8003), and reload settings
- Initialize AI client (OpenAI or Ollama) on startup based on configuration

### services\ai_insights\config\settings.py(NEW)

References: 

- services\focus_engine\config\settings.py

Create Pydantic settings configuration for AI Insights service:
- Define Settings class with BaseSettings inheritance
- Include debug_mode, log_level, environment settings
- Database URL for storing insights and patterns
- AI provider settings (provider: 'openai' or 'ollama', openai_api_key, ollama_base_url, model_name)
- API prefix and CORS origins
- Insight generation settings (min_sessions_for_patterns, confidence_threshold, max_recommendations)
- Prompt configuration (temperature, max_tokens, top_p)
- Environment variable prefix 'AI_INSIGHTS_'
- get_settings() factory function

### services\ai_insights\config\prompt_config.py(MODIFY)

Define AI prompt templates and configuration:
- PATTERN_ANALYSIS_PROMPT - template for analyzing user session patterns
- SESSION_INSIGHTS_PROMPT - template for generating session-specific insights
- PRODUCTIVITY_COACHING_PROMPT - template for personalized coaching recommendations
- SCHEDULE_OPTIMIZATION_PROMPT - template for suggesting schedule improvements
- GOAL_RECOMMENDATION_PROMPT - template for recommending goals based on behavior
- Prompt formatting functions: format_session_data(), format_user_stats(), format_patterns()
- System message templates for different insight types
- Response parsing utilities to extract structured data from AI responses

### services\ai_insights\models\pattern_models.py(MODIFY)

References: 

- services\focus_engine\models\session_models.py

Define pattern detection data models:
- ProductivityPattern SQLAlchemy model with fields: id, pattern_id (UUID), user_id, pattern_type (time_of_day, session_duration, break_timing, music_preference, consistency), description, confidence_score, detected_at, supporting_data (JSON), is_active
- PatternResponse Pydantic model for API responses
- PatternInsight Pydantic model with pattern_id, insight_text, actionable_recommendations, confidence
- PatternType enum (TIME_OF_DAY, DURATION_PREFERENCE, BREAK_TIMING, MUSIC_EFFECTIVENESS, CONSISTENCY, INTERRUPTION_TRIGGERS)
- TimeOfDayPattern Pydantic model with best_hours, avg_productivity_by_hour, recommendation

### services\ai_insights\models\insights_models.py(MODIFY)

Define AI-generated insights data models:
- AIInsight SQLAlchemy model with fields: id, insight_id (UUID), user_id, insight_type (pattern, recommendation, coaching, optimization), title, content, priority (high, medium, low), is_read, is_dismissed, generated_at, expires_at, metadata (JSON)
- InsightResponse Pydantic model for API responses
- InsightCreate Pydantic model for generating insights
- CoachingRecommendation Pydantic model with category, recommendation_text, expected_impact, difficulty_level, action_steps
- WeeklySummaryInsight Pydantic model with total_sessions, productivity_trend, key_achievements, areas_for_improvement, next_week_suggestions

### services\ai_insights\clients\openai_client.py(MODIFY)

Implement OpenAI API client:
- OpenAIClient class for interacting with OpenAI API
- Methods:
  - generate_completion(prompt, system_message, temperature, max_tokens) - generate text completion
  - generate_chat_completion(messages, model, temperature) - generate chat-based completion
  - analyze_patterns(session_data) - analyze patterns using GPT model
  - generate_insights(user_stats, patterns) - generate personalized insights
  - generate_coaching(user_data, goals) - generate coaching recommendations
- Use openai Python library
- Handle API errors and rate limiting
- Implement response caching to reduce API costs
- Parse structured responses from AI (JSON mode when available)

### services\ai_insights\clients\ollama_client.py(MODIFY)

Implement Ollama local LLM client:
- OllamaClient class for interacting with local Ollama instance
- Methods:
  - generate_completion(prompt, model, temperature) - generate text completion
  - generate_chat_completion(messages, model) - generate chat-based completion
  - analyze_patterns(session_data) - analyze patterns using local model
  - generate_insights(user_stats, patterns) - generate insights
  - generate_coaching(user_data, goals) - generate coaching
- Use requests library to call Ollama HTTP API
- Support models like llama2, mistral, codellama
- Handle connection errors gracefully
- Implement streaming responses for real-time feedback

### services\ai_insights\clients\analysis_client.py(MODIFY)

Implement unified analysis client:
- AnalysisClient class that abstracts OpenAI and Ollama clients
- Factory method get_client(provider) to return appropriate client based on settings
- Unified interface for all AI operations
- Methods:
  - analyze_productivity_patterns(user_id, days) - detect patterns in user behavior
  - generate_session_insights(session_id) - generate insights for specific session
  - generate_weekly_summary(user_id, week_start) - create weekly summary report
  - generate_coaching_recommendations(user_id) - provide personalized coaching
  - optimize_schedule(user_id, current_schedule) - suggest schedule improvements
- Handle provider switching transparently
- Implement fallback logic if primary provider fails

### services\ai_insights\services\pattern_discoverer.py(MODIFY)

References: 

- services\focus_engine\services\analytics_service.py

Implement pattern discovery service:
- PatternDiscoverer class with methods:
  - discover_patterns(user_id, days) - analyze session data to identify patterns
  - detect_time_of_day_patterns(sessions) - find optimal productivity times
  - detect_duration_patterns(sessions) - identify preferred session lengths
  - detect_music_patterns(sessions) - determine music effectiveness patterns
  - detect_consistency_patterns(sessions) - analyze consistency and regularity
  - calculate_pattern_confidence(pattern_data) - compute confidence score for patterns
- Statistical analysis using numpy/pandas for pattern detection
- Minimum data requirements (e.g., 10 sessions) before detecting patterns
- Pattern persistence to database
- Integration with Focus Engine session data via HTTP client

### services\ai_insights\services\session_analyzer.py(MODIFY)

References: 

- services\focus_engine\services\analytics_service.py

Implement session analysis service:
- SessionAnalyzer class with methods:
  - analyze_session(session_id) - generate insights for completed session
  - compare_to_user_average(session_id, user_id) - compare session to user's typical performance
  - identify_success_factors(session_id) - determine what made session successful
  - identify_improvement_areas(session_id) - suggest areas for improvement
  - generate_session_report(session_id) - create comprehensive session report
- Use AI client to generate natural language insights
- Incorporate pattern data for contextualized analysis
- Calculate session quality score based on multiple factors
- Store insights in database for future reference

### services\ai_insights\services\coaching_generator.py(MODIFY)

Implement AI coaching service:
- CoachingGenerator class with methods:
  - generate_weekly_coaching(user_id) - create personalized weekly coaching message
  - generate_goal_recommendations(user_id) - suggest new goals based on progress
  - generate_schedule_optimization(user_id) - recommend schedule improvements
  - generate_motivation_message(user_id, context) - create motivational content
  - generate_habit_suggestions(user_id) - suggest productivity habits to build
- Use AI client with coaching-specific prompts
- Incorporate user's goals, patterns, and recent performance
- Personalize tone and content based on user preferences
- Generate actionable, specific recommendations
- Track coaching effectiveness over time

### services\ai_insights\routers\patterns.py(MODIFY)

References: 

- services\focus_engine\routers\analytics.py

Create patterns router with endpoints:
- GET `/api/v1/patterns/users/{user_id}` - get all detected patterns for user
- GET `/api/v1/patterns/users/{user_id}/time-of-day` - get time-of-day productivity patterns
- GET `/api/v1/patterns/users/{user_id}/duration` - get session duration preferences
- GET `/api/v1/patterns/users/{user_id}/music` - get music effectiveness patterns
- POST `/api/v1/patterns/users/{user_id}/discover` - trigger pattern discovery analysis
- GET `/api/v1/patterns/{pattern_id}` - get specific pattern details
- Use PatternDiscoverer service for business logic
- Return PatternResponse and PatternInsight models
- Include confidence scores and supporting data

### services\ai_insights\routers\insights.py(MODIFY)

References: 

- services\focus_engine\routers\analytics.py

Create insights router with endpoints:
- GET `/api/v1/insights/users/{user_id}` - get all insights for user (paginated)
- GET `/api/v1/insights/users/{user_id}/unread` - get unread insights
- GET `/api/v1/insights/sessions/{session_id}` - get insights for specific session
- POST `/api/v1/insights/users/{user_id}/weekly-summary` - generate weekly summary
- POST `/api/v1/insights/{insight_id}/read` - mark insight as read
- POST `/api/v1/insights/{insight_id}/dismiss` - dismiss insight
- DELETE `/api/v1/insights/{insight_id}` - delete insight
- Use SessionAnalyzer and CoachingGenerator services
- Return InsightResponse and WeeklySummaryInsight models
- Include priority filtering

### services\ai_insights\routers\coaching.py(MODIFY)

Create coaching router with endpoints:
- GET `/api/v1/coaching/users/{user_id}/recommendations` - get personalized coaching recommendations
- POST `/api/v1/coaching/users/{user_id}/weekly` - generate weekly coaching message
- POST `/api/v1/coaching/users/{user_id}/goals` - get goal recommendations
- POST `/api/v1/coaching/users/{user_id}/schedule-optimization` - get schedule optimization suggestions
- POST `/api/v1/coaching/users/{user_id}/motivation` - generate motivational message
- GET `/api/v1/coaching/users/{user_id}/habits` - get habit-building suggestions
- Use CoachingGenerator service for business logic
- Return CoachingRecommendation models
- Include action steps and expected impact

### services\ai_insights\database\connection.py(NEW)

References: 

- services\focus_engine\database\connection.py

Create database connection module:
- Import SQLAlchemy create_engine, sessionmaker, declarative_base
- Create Base = declarative_base() for ORM models
- Create engine from settings.database_url
- Create SessionLocal = sessionmaker(bind=engine)
- Define get_db() dependency function for FastAPI
- Include connection pooling configuration
- Add create_tables() function to initialize database schema

### services\analytics\main.py(MODIFY)

References: 

- services\focus_engine\main.py

Create the FastAPI application for Analytics service:
- Application initialization with CORS middleware and lifespan management
- Health check endpoint at `/health`
- Include routers for trends, metrics, comparisons, and export from `routers/` directory
- Configure settings from `config/settings.py` (to be created)
- Set up logging configuration
- Define root endpoint with service information
- Configure uvicorn server with host, port (8004), and reload settings
- Initialize data aggregation scheduler on startup

### services\analytics\config\settings.py(NEW)

References: 

- services\focus_engine\config\settings.py

Create Pydantic settings configuration for Analytics service:
- Define Settings class with BaseSettings inheritance
- Include debug_mode, log_level, environment settings
- Database URL for storing aggregated analytics data
- Redis URL for caching analytics results
- API prefix and CORS origins
- Analytics calculation settings (aggregation_interval, retention_days, cache_ttl)
- Export settings (max_export_rows, supported_formats: csv, json, pdf)
- Comparison settings (max_comparison_periods, default_comparison_type)
- Environment variable prefix 'ANALYTICS_'
- get_settings() factory function

### services\analytics\models\trend_models.py(MODIFY)

Define trend analysis data models:
- TrendData Pydantic model with fields: date, value, change_from_previous, percentage_change, trend_direction (up, down, stable)
- ProductivityTrend Pydantic model with metric_name, time_period, data_points (List[TrendData]), overall_trend, insights
- TrendAnalysis Pydantic model with user_id, start_date, end_date, trends (List[ProductivityTrend]), summary
- TrendPeriod enum (DAILY, WEEKLY, MONTHLY, QUARTERLY, YEARLY)
- TrendMetric enum (TOTAL_SESSIONS, TOTAL_MINUTES, AVG_PRODUCTIVITY, COMPLETION_RATE, STREAK_LENGTH)

### services\analytics\models\metrics_models.py(MODIFY)

Define metrics data models:
- UserMetrics Pydantic model with fields: user_id, period_start, period_end, total_sessions, total_minutes, avg_session_duration, completion_rate, avg_productivity_score, best_time_of_day, most_productive_day, current_streak, longest_streak
- ComparisonMetrics Pydantic model with current_period, previous_period, changes (dict of metric changes), improvement_areas, decline_areas
- GoalProgress Pydantic model with goal_id, goal_name, target_value, current_value, progress_percentage, on_track, projected_completion_date
- CategoryBreakdown Pydantic model with category, total_minutes, session_count, percentage_of_total

### services\analytics\services\trend_analyzer.py(MODIFY)

References: 

- services\focus_engine\services\analytics_service.py

Implement trend analysis service:
- TrendAnalyzer class with methods:
  - analyze_productivity_trends(user_id, start_date, end_date, period) - analyze trends over time
  - calculate_trend_direction(data_points) - determine if trend is up, down, or stable
  - detect_anomalies(data_points) - identify unusual patterns or outliers
  - forecast_future_performance(user_id, days_ahead) - predict future productivity
  - generate_trend_insights(trends) - create natural language insights about trends
- Use statistical methods (moving averages, linear regression) for trend calculation
- Fetch session data from Focus Engine service
- Calculate percentage changes and growth rates
- Identify significant changes and turning points

### services\analytics\services\metrics_calculator.py(MODIFY)

References: 

- services\focus_engine\services\analytics_service.py

Implement metrics calculation service:
- MetricsCalculator class with methods:
  - calculate_user_metrics(user_id, start_date, end_date) - compute comprehensive metrics
  - calculate_comparison_metrics(user_id, current_period, previous_period) - compare two time periods
  - calculate_goal_progress(user_id, goal_id) - track progress toward specific goal
  - calculate_category_breakdown(user_id, start_date, end_date) - break down time by category
  - calculate_efficiency_score(user_id) - compute overall efficiency metric
- Aggregate data from Focus Engine sessions
- Use Redis caching for frequently accessed metrics
- Handle missing data gracefully
- Provide default values when insufficient data

### services\analytics\services\export_service.py(MODIFY)

Implement data export service:
- ExportService class with methods:
  - export_to_csv(user_id, start_date, end_date) - export session data to CSV
  - export_to_json(user_id, start_date, end_date) - export data to JSON
  - export_to_pdf(user_id, start_date, end_date) - generate PDF report
  - generate_weekly_report(user_id, week_start) - create formatted weekly report
  - generate_monthly_report(user_id, month_start) - create formatted monthly report
- Use pandas for CSV generation
- Use reportlab or weasyprint for PDF generation
- Include charts and visualizations in PDF reports
- Implement streaming for large exports
- Store generated reports temporarily with expiration

### services\analytics\routers\trends.py(MODIFY)

References: 

- services\focus_engine\routers\analytics.py

Create trends router with endpoints:
- GET `/api/v1/trends/users/{user_id}/productivity` - get productivity trends over time
- GET `/api/v1/trends/users/{user_id}/sessions` - get session count trends
- GET `/api/v1/trends/users/{user_id}/completion-rate` - get completion rate trends
- GET `/api/v1/trends/users/{user_id}/forecast` - get productivity forecast
- Query parameters: start_date, end_date, period (daily, weekly, monthly)
- Use TrendAnalyzer service for business logic
- Return TrendAnalysis and ProductivityTrend models
- Include caching headers for performance

### services\analytics\routers\metrics.py(MODIFY)

References: 

- services\focus_engine\routers\analytics.py

Create metrics router with endpoints:
- GET `/api/v1/metrics/users/{user_id}` - get comprehensive user metrics
- GET `/api/v1/metrics/users/{user_id}/summary` - get summary metrics for dashboard
- GET `/api/v1/metrics/users/{user_id}/goals` - get goal progress metrics
- GET `/api/v1/metrics/users/{user_id}/categories` - get category breakdown
- Query parameters: start_date, end_date, include_comparisons
- Use MetricsCalculator service for business logic
- Return UserMetrics and GoalProgress models
- Implement Redis caching with 5-minute TTL

### services\analytics\routers\comparisons.py(MODIFY)

Create comparisons router with endpoints:
- GET `/api/v1/comparisons/users/{user_id}/periods` - compare two time periods
- GET `/api/v1/comparisons/users/{user_id}/week-over-week` - compare current week to previous
- GET `/api/v1/comparisons/users/{user_id}/month-over-month` - compare current month to previous
- GET `/api/v1/comparisons/users/{user_id}/year-over-year` - compare current year to previous
- Query parameters: current_start, current_end, comparison_start, comparison_end
- Use MetricsCalculator service for business logic
- Return ComparisonMetrics models
- Highlight significant changes and improvements

### services\analytics\routers\export.py(MODIFY)

Create export router with endpoints:
- GET `/api/v1/export/users/{user_id}/csv` - export data to CSV
- GET `/api/v1/export/users/{user_id}/json` - export data to JSON
- GET `/api/v1/export/users/{user_id}/pdf` - generate PDF report
- POST `/api/v1/export/users/{user_id}/weekly-report` - generate weekly report
- POST `/api/v1/export/users/{user_id}/monthly-report` - generate monthly report
- Query parameters: start_date, end_date, format, include_charts
- Use ExportService for business logic
- Return file downloads with appropriate content-type headers
- Implement rate limiting to prevent abuse

### services\analytics\database\connection.py(NEW)

References: 

- services\focus_engine\database\connection.py

Create database connection module:
- Import SQLAlchemy create_engine, sessionmaker, declarative_base
- Create Base = declarative_base() for ORM models
- Create engine from settings.database_url
- Create SessionLocal = sessionmaker(bind=engine)
- Define get_db() dependency function for FastAPI
- Include connection pooling configuration
- Add create_tables() function to initialize database schema

### services\focus_engine\models\user_models.py(MODIFY)

References: 

- services\focus_engine\models\session_models.py

Extend user models to support onboarding and scheduling features:
- Add UserProfile SQLAlchemy model with fields: user_id (FK to User), chronotype (morning, evening, flexible), wants_to_change_chronotype (boolean), downtime_needs (low, medium, high), personality_data (JSON for questionnaire responses), onboarding_completed (boolean), onboarding_type (quick, full)
- Add UserGoal SQLAlchemy model with fields: id, goal_id (UUID), user_id, category (health, personal_development, relationships, chores, fun), goal_type (workout_frequency, learning_skill, date_time, etc.), target_value, current_value, time_period (weekly, monthly), priority_rank, is_active, created_at, updated_at
- Add UserPriorities SQLAlchemy model with fields: user_id, health_priority, personal_dev_priority, relationships_priority, chores_priority, fun_priority, downtime_priority (1-6 ranking)
- Add corresponding Pydantic models for API requests/responses
- These models support the brainstorm's onboarding and goal-setting features

### services\focus_engine\models\schedule_models.py(NEW)

References: 

- services\focus_engine\models\session_models.py

Create schedule management data models:
- WeeklySchedule SQLAlchemy model with fields: id, schedule_id (UUID), user_id, week_start_date, is_base_schedule (boolean), is_active, created_at, updated_at
- TimeBlock SQLAlchemy model with fields: id, block_id (UUID), schedule_id (FK), day_of_week (0-6), start_time, end_time, category (mandatory, health, personal_dev, relationships, chores, fun, downtime), activity_name, is_locked (for mandatory blocks), is_flexible, notes
- ScheduleTemplate SQLAlchemy model with fields: id, template_id (UUID), user_id, name, description, is_system_template, usage_count
- SprintMode SQLAlchemy model with fields: id, sprint_id (UUID), user_id, goal_id (FK), start_date, end_date, is_active, time_allocation_hours_per_week
- Corresponding Pydantic models: WeeklyScheduleResponse, TimeBlockCreate, TimeBlockUpdate, ScheduleGenerationRequest
- These models support the brainstorm's weekly scheduling features

### services\focus_engine\routers\onboarding.py(NEW)

References: 

- services\focus_engine\routers\sessions.py

Create onboarding router with endpoints:
- POST `/api/v1/onboarding/users/{user_id}/start` - initiate onboarding (quick or full)
- POST `/api/v1/onboarding/users/{user_id}/profile` - save user profile (chronotype, personality)
- POST `/api/v1/onboarding/users/{user_id}/priorities` - save category priorities
- POST `/api/v1/onboarding/users/{user_id}/goals` - save initial goals
- POST `/api/v1/onboarding/users/{user_id}/mandatory-blocks` - save mandatory time commitments
- POST `/api/v1/onboarding/users/{user_id}/complete` - finalize onboarding and generate initial schedule
- GET `/api/v1/onboarding/users/{user_id}/status` - get onboarding progress
- Use new UserProfile, UserGoal, UserPriorities models
- Return onboarding progress and next steps
- Implement validation for required fields based on onboarding type

### services\focus_engine\routers\goals.py(NEW)

References: 

- services\focus_engine\routers\templates.py

Create goals router with endpoints:
- GET `/api/v1/goals/users/{user_id}` - get all user goals
- POST `/api/v1/goals/users/{user_id}` - create new goal
- PUT `/api/v1/goals/{goal_id}` - update goal
- DELETE `/api/v1/goals/{goal_id}` - delete goal
- GET `/api/v1/goals/{goal_id}/progress` - get goal progress
- POST `/api/v1/goals/{goal_id}/update-progress` - manually update goal progress
- GET `/api/v1/goals/users/{user_id}/by-category/{category}` - get goals by category
- Use UserGoal model and integrate with Analytics service for progress tracking
- Return GoalResponse models with progress information
- Support goal categories from brainstorm: health, personal_development, relationships, chores, fun

### services\focus_engine\routers\schedules.py(NEW)

References: 

- services\focus_engine\routers\sessions.py

Create schedules router with endpoints:
- GET `/api/v1/schedules/users/{user_id}/current` - get current week's schedule
- GET `/api/v1/schedules/users/{user_id}/base` - get base schedule template
- POST `/api/v1/schedules/users/{user_id}/generate` - generate new schedule based on goals and priorities
- PUT `/api/v1/schedules/{schedule_id}` - update schedule
- POST `/api/v1/schedules/{schedule_id}/time-blocks` - add time block
- PUT `/api/v1/schedules/time-blocks/{block_id}` - update time block (drag-and-drop)
- DELETE `/api/v1/schedules/time-blocks/{block_id}` - delete time block
- POST `/api/v1/schedules/users/{user_id}/sprint-mode` - activate sprint mode for specific goal
- GET `/api/v1/schedules/users/{user_id}/preview-next-week` - preview next week's schedule
- Use WeeklySchedule, TimeBlock, SprintMode models
- Implement schedule generation algorithm based on priorities, goals, and mandatory blocks
- Return WeeklyScheduleResponse with all time blocks

### services\focus_engine\routers\feedback.py(NEW)

References: 

- services\focus_engine\routers\analytics.py

Create feedback router with endpoints:
- POST `/api/v1/feedback/users/{user_id}/weekly` - submit weekly feedback
- POST `/api/v1/feedback/users/{user_id}/monthly` - submit monthly review
- GET `/api/v1/feedback/users/{user_id}/history` - get feedback history
- POST `/api/v1/feedback/schedules/{schedule_id}/rating` - rate schedule satisfaction
- POST `/api/v1/feedback/schedules/{schedule_id}/adjustments` - request schedule adjustments based on feedback
- Create WeeklyFeedback model with fields: user_id, week_start, satisfaction_rating, neglected_areas, burnout_areas, notes, submitted_at
- Create MonthlyReview model with fields: user_id, month_start, overall_progress, priority_changes, goal_updates, intentions_for_next_month
- Use feedback to trigger schedule regeneration and AI coaching recommendations
- Integrate with AI Insights service for feedback analysis

### services\focus_engine\services\schedule_generator.py(NEW)

References: 

- services\focus_engine\services\template_service.py

Create schedule generation service:
- ScheduleGenerator class with methods:
  - generate_base_schedule(user_id) - create initial schedule from onboarding data
  - generate_weekly_schedule(user_id, week_start) - generate schedule for specific week
  - apply_priorities(schedule, priorities) - distribute time based on priority rankings
  - apply_goals(schedule, goals) - allocate time for goal-related activities
  - apply_mandatory_blocks(schedule, mandatory_blocks) - lock in mandatory commitments
  - optimize_for_chronotype(schedule, chronotype) - place activities at optimal times
  - balance_categories(schedule) - ensure balanced time distribution
  - validate_schedule(schedule) - check for conflicts and gaps
- Algorithm: start with mandatory blocks, allocate time for high-priority goals, fill remaining time with other categories, optimize timing based on chronotype
- Return WeeklySchedule with all TimeBlocks
- Support sprint mode by temporarily increasing allocation to sprint goal

### ui\focus-flow-app\src\store\slices\gameSlice.ts(NEW)

References: 

- ui\focus-flow-app\src\store\slices\timerSlice.ts

Create Redux slice for gamification state:
- Define GameState interface with fields: userLevel, currentXP, xpToNextLevel, achievements, currentStreak, longestStreak, totalSessions, unlockedRewards, recentLevelUp, recentAchievements
- Initial state with default values
- Reducers:
  - setUserLevel(level, xp, xpToNext) - update level information
  - addXP(amount) - add experience points
  - unlockAchievement(achievement) - add newly unlocked achievement
  - updateStreak(current, longest) - update streak information
  - setAchievements(achievements) - set all achievements
  - clearRecentNotifications() - clear recent level-up/achievement notifications
- Export actions and reducer
- Integrate with Game Engine service API calls

### ui\focus-flow-app\src\store\slices\musicSlice.ts(NEW)

References: 

- ui\focus-flow-app\src\store\slices\timerSlice.ts

Create Redux slice for music control state:
- Define MusicState interface with fields: playlists, currentPlaylist, isPlaying, currentTrack, volume, connectedService (spotify, youtube_music, none), playbackState, recommendations
- Initial state with default values
- Reducers:
  - setPlaylists(playlists) - set available playlists
  - setCurrentPlaylist(playlist) - set active playlist
  - setPlaybackState(isPlaying, track, position) - update playback state
  - setVolume(volume) - update volume level
  - setConnectedService(service) - set active music service
  - setRecommendations(recommendations) - set recommended playlists
  - clearPlayback() - reset playback state
- Export actions and reducer
- Integrate with Music Control service API calls

### ui\focus-flow-app\src\store\slices\scheduleSlice.ts(NEW)

References: 

- ui\focus-flow-app\src\store\slices\timerSlice.ts

Create Redux slice for schedule management state:
- Define ScheduleState interface with fields: currentSchedule, baseSchedule, timeBlocks, sprintMode, selectedDate, draggedBlock, scheduleView (week, day, list)
- Initial state with default values
- Reducers:
  - setCurrentSchedule(schedule) - set active schedule
  - setBaseSchedule(schedule) - set base template schedule
  - setTimeBlocks(blocks) - set all time blocks
  - addTimeBlock(block) - add new time block
  - updateTimeBlock(blockId, updates) - update existing block (for drag-and-drop)
  - deleteTimeBlock(blockId) - remove time block
  - setSprintMode(sprint) - activate/deactivate sprint mode
  - setSelectedDate(date) - change selected date
  - setDraggedBlock(block) - track block being dragged
  - setScheduleView(view) - change view mode
- Export actions and reducer
- Integrate with Focus Engine schedules API

### ui\focus-flow-app\src\store\slices\goalsSlice.ts(NEW)

References: 

- ui\focus-flow-app\src\store\slices\timerSlice.ts

Create Redux slice for goals management state:
- Define GoalsState interface with fields: goals, goalsByCategory, activeGoals, completedGoals, selectedGoal, goalProgress
- Initial state with default values
- Reducers:
  - setGoals(goals) - set all goals
  - addGoal(goal) - add new goal
  - updateGoal(goalId, updates) - update existing goal
  - deleteGoal(goalId) - remove goal
  - setGoalProgress(goalId, progress) - update goal progress
  - setSelectedGoal(goalId) - select goal for detailed view
  - filterByCategory(category) - filter goals by category
  - toggleGoalActive(goalId) - activate/deactivate goal
- Export actions and reducer
- Integrate with Focus Engine goals API

### ui\focus-flow-app\src\store\slices\insightsSlice.ts(NEW)

References: 

- ui\focus-flow-app\src\store\slices\analyticsSlice.ts

Create Redux slice for AI insights state:
- Define InsightsState interface with fields: insights, unreadInsights, patterns, coachingRecommendations, weeklySummary, loading, error
- Initial state with default values
- Reducers:
  - setInsights(insights) - set all insights
  - addInsight(insight) - add new insight
  - markInsightRead(insightId) - mark insight as read
  - dismissInsight(insightId) - dismiss insight
  - setPatterns(patterns) - set detected patterns
  - setCoachingRecommendations(recommendations) - set coaching suggestions
  - setWeeklySummary(summary) - set weekly summary data
  - setLoading(loading) - set loading state
  - setError(error) - set error state
- Export actions and reducer
- Integrate with AI Insights service API

### ui\focus-flow-app\src\services\gameApi.ts(NEW)

References: 

- ui\focus-flow-app\src\services\sessionApi.ts

Create Game Engine API client:
- Import api instance from `./api.ts`
- Define functions:
  - getUserLevel(userId) - get current level and XP
  - getUserAchievements(userId) - get all achievements
  - getUnlockedAchievements(userId) - get only unlocked achievements
  - getAchievementProgress(userId) - get progress toward achievements
  - getUserStreak(userId) - get current streak information
  - getStreakMilestones(userId) - get achieved milestones
  - getXPLeaderboard(limit, offset) - get XP leaderboard
  - getStreakLeaderboard(limit, offset) - get streak leaderboard
- All functions return typed responses using TypeScript interfaces
- Handle errors and return appropriate error messages
- Base URL: http://localhost:8001/api/v1

### ui\focus-flow-app\src\services\musicApi.ts(NEW)

References: 

- ui\focus-flow-app\src\services\sessionApi.ts

Create Music Control API client:
- Import api instance from `./api.ts`
- Define functions:
  - getUserPlaylists(userId) - get user's playlists
  - getPlaylistRecommendations(userId, sessionType) - get recommended playlists
  - getPlaylistDetails(playlistId) - get playlist details and tracks
  - searchPlaylists(query) - search for playlists
  - savePlaylist(userId, playlistData) - save playlist to library
  - playPlaylist(playlistId, deviceId) - start playlist playback
  - pausePlayback() - pause playback
  - resumePlayback() - resume playback
  - getPlaybackState() - get current playback state
  - setVolume(volume) - set volume level
- All functions return typed responses
- Base URL: http://localhost:8002/api/v1

### ui\focus-flow-app\src\services\insightsApi.ts(NEW)

References: 

- ui\focus-flow-app\src\services\sessionApi.ts

Create AI Insights API client:
- Import api instance from `./api.ts`
- Define functions:
  - getUserInsights(userId, limit, offset) - get all insights
  - getUnreadInsights(userId) - get unread insights
  - getSessionInsights(sessionId) - get insights for specific session
  - generateWeeklySummary(userId) - generate weekly summary
  - markInsightRead(insightId) - mark insight as read
  - dismissInsight(insightId) - dismiss insight
  - getUserPatterns(userId) - get detected patterns
  - getTimeOfDayPatterns(userId) - get time-of-day patterns
  - getCoachingRecommendations(userId) - get coaching recommendations
  - generateWeeklyCoaching(userId) - generate weekly coaching message
- All functions return typed responses
- Base URL: http://localhost:8003/api/v1

### ui\focus-flow-app\src\services\scheduleApi.ts(NEW)

References: 

- ui\focus-flow-app\src\services\sessionApi.ts

Create Schedule API client:
- Import api instance from `./api.ts`
- Define functions:
  - getCurrentSchedule(userId) - get current week's schedule
  - getBaseSchedule(userId) - get base schedule template
  - generateSchedule(userId, weekStart) - generate new schedule
  - updateSchedule(scheduleId, updates) - update schedule
  - addTimeBlock(scheduleId, blockData) - add time block
  - updateTimeBlock(blockId, updates) - update time block
  - deleteTimeBlock(blockId) - delete time block
  - activateSprintMode(userId, sprintData) - activate sprint mode
  - previewNextWeek(userId) - preview next week's schedule
  - submitWeeklyFeedback(userId, feedbackData) - submit weekly feedback
- All functions return typed responses
- Base URL: http://localhost:8000/api/v1 (Focus Engine)

### ui\focus-flow-app\src\services\goalsApi.ts(NEW)

References: 

- ui\focus-flow-app\src\services\sessionApi.ts

Create Goals API client:
- Import api instance from `./api.ts`
- Define functions:
  - getUserGoals(userId) - get all user goals
  - createGoal(userId, goalData) - create new goal
  - updateGoal(goalId, updates) - update goal
  - deleteGoal(goalId) - delete goal
  - getGoalProgress(goalId) - get goal progress
  - updateGoalProgress(goalId, progress) - update goal progress
  - getGoalsByCategory(userId, category) - get goals by category
- All functions return typed responses
- Base URL: http://localhost:8000/api/v1 (Focus Engine)

### ui\focus-flow-app\src\pages\Onboarding.tsx(NEW)

References: 

- ui\focus-flow-app\src\pages\Timer.tsx(MODIFY)

Create onboarding page component:
- Multi-step onboarding wizard with progress indicator
- Steps:
  1. Welcome screen with Quick Start vs Full Onboarding choice
  2. Profile setup (chronotype, personality questionnaire)
  3. Priority ranking (drag-and-drop interface for ranking categories)
  4. Goal setting (forms for each category: health, personal dev, relationships, etc.)
  5. Mandatory time blocks (calendar interface to mark fixed commitments)
  6. Review and confirmation
- Use React Hook Form for form management
- Use scheduleApi to submit onboarding data
- Navigate to Dashboard after completion
- Store onboarding progress in localStorage for resuming
- Responsive design for mobile and desktop

### ui\focus-flow-app\src\pages\Schedule.tsx(NEW)

References: 

- ui\focus-flow-app\src\pages\Timer.tsx(MODIFY)

Create schedule management page:
- Weekly calendar view with drag-and-drop time blocks
- Color-coded blocks by category (mandatory, health, personal dev, etc.)
- View modes: week-at-a-glance, day view, list view
- Drag-and-drop functionality to rearrange time blocks
- Add/edit/delete time block modals
- Sprint mode toggle and configuration
- Preview next week button
- Integration with scheduleSlice Redux state
- Use scheduleApi for CRUD operations
- Real-time validation for schedule conflicts
- AI warning system when schedule is unbalanced
- Responsive design with mobile-friendly touch interactions

### ui\focus-flow-app\src\pages\Goals.tsx(NEW)

References: 

- ui\focus-flow-app\src\pages\Templates.tsx

Create goals management page:
- List of all goals grouped by category
- Progress bars for each goal
- Add/edit/delete goal functionality
- Goal detail modal with progress tracking and history
- Filter by category and status (active, completed, paused)
- Goal recommendations section (from AI Insights)
- Visual indicators for on-track vs behind goals
- Integration with goalsSlice Redux state
- Use goalsApi for CRUD operations
- Charts showing goal progress over time
- Celebrate goal completions with animations
- Responsive design

### ui\focus-flow-app\src\pages\Gamification.tsx(NEW)

References: 

- ui\focus-flow-app\src\pages\Dashboard.tsx(MODIFY)

Create gamification page:
- User level and XP display with progress bar to next level
- Achievement showcase with locked/unlocked states
- Achievement detail modals with unlock criteria
- Current streak display with streak calendar
- Streak milestones and history
- Leaderboards (XP, streaks, total sessions) with user's rank
- Recent level-ups and achievement unlocks
- Rewards and unlockables showcase
- Integration with gameSlice Redux state
- Use gameApi for data fetching
- Animations for level-ups and achievement unlocks
- Responsive design with engaging visuals

### ui\focus-flow-app\src\pages\Music.tsx(NEW)

References: 

- ui\focus-flow-app\src\pages\Settings.tsx(MODIFY)

Create music control page:
- Connected music services display (Spotify, YouTube Music)
- OAuth connection buttons for each service
- User's playlists library
- Playlist recommendations for focus sessions
- Playlist search functionality
- Playlist effectiveness metrics (which playlists boost productivity)
- Now playing widget with playback controls
- Volume control
- Discover section with curated focus playlists
- Filter by genre and mood
- Integration with musicSlice Redux state
- Use musicApi for all operations
- Responsive design

### ui\focus-flow-app\src\pages\Insights.tsx(NEW)

References: 

- ui\focus-flow-app\src\pages\Analytics.tsx(MODIFY)

Create AI insights page:
- Unread insights feed with priority indicators
- Insight cards with read/dismiss actions
- Detected patterns section (time-of-day, duration, music, consistency)
- Pattern detail views with supporting data and charts
- Weekly summary display
- Coaching recommendations section
- Actionable suggestions with expected impact
- Insights history and archive
- Filter by insight type and priority
- Integration with insightsSlice Redux state
- Use insightsApi for data fetching
- Responsive design with clear visual hierarchy

### ui\focus-flow-app\src\components\schedule\WeeklyCalendar.tsx(NEW)

References: 

- ui\focus-flow-app\src\components\timer\Timer.tsx

Create weekly calendar component:
- 7-day grid layout with time slots (hourly or 30-minute intervals)
- Render TimeBlock components for each scheduled block
- Drag-and-drop functionality using react-dnd or native drag events
- Drop zones for each time slot
- Visual feedback during drag (ghost block, drop indicators)
- Handle drag start, drag over, and drop events
- Update scheduleSlice state on drop
- Call scheduleApi.updateTimeBlock on successful drop
- Color coding by category
- Responsive design that adapts to mobile (vertical scroll, day-by-day view)
- Props: schedule, timeBlocks, onBlockDrop, onBlockClick

### ui\focus-flow-app\src\components\schedule\TimeBlock.tsx(NEW)

References: 

- ui\focus-flow-app\src\components\ui\Card.tsx

Create time block component:
- Display time block with category color, activity name, time range
- Draggable element (draggable attribute or react-dnd)
- Click handler to open edit modal
- Lock icon for mandatory blocks (non-draggable)
- Flexible/rigid indicator
- Visual states: default, hover, dragging, selected
- Props: block (TimeBlock data), isDraggable, onDragStart, onDragEnd, onClick
- Responsive design with touch-friendly sizing
- Accessibility: keyboard navigation, ARIA labels

### ui\focus-flow-app\src\components\goals\GoalCard.tsx(NEW)

References: 

- ui\focus-flow-app\src\components\ui\Card.tsx

Create goal card component:
- Display goal name, category, target, and current progress
- Progress bar with percentage
- Status indicator (on track, behind, completed)
- Edit and delete buttons
- Click handler to open goal detail modal
- Visual category icon
- Props: goal (Goal data), onEdit, onDelete, onClick
- Responsive design
- Animations for progress updates

### ui\focus-flow-app\src\components\gamification\AchievementCard.tsx(NEW)

References: 

- ui\focus-flow-app\src\components\ui\Card.tsx

Create achievement card component:
- Display achievement icon, title, description
- Locked/unlocked state with visual distinction (grayscale for locked)
- Progress bar for in-progress achievements
- Unlock date for completed achievements
- Click handler to show achievement details
- Props: achievement (Achievement data), onClick
- Animations for unlock reveal
- Responsive design

### ui\focus-flow-app\src\components\gamification\LevelDisplay.tsx(NEW)

References: 

- ui\focus-flow-app\src\components\ui\Badge.tsx

Create level display component:
- Show current level number with visual badge
- XP progress bar to next level
- Current XP / Required XP text
- Level-up animation when level increases
- Props: level, currentXP, xpToNextLevel, showAnimation
- Responsive design
- Engaging visual design with gradients and effects

### ui\focus-flow-app\src\components\gamification\StreakCalendar.tsx(NEW)

References: 

- ui\focus-flow-app\src\components\ui\Card.tsx

Create streak calendar component:
- Calendar grid showing last 30-90 days
- Visual indicators for days with sessions (filled) vs missed days (empty)
- Current streak highlighted
- Longest streak indicator
- Hover tooltips showing session count per day
- Props: streakData, currentStreak, longestStreak
- Responsive design
- Color intensity based on session count (heatmap style)

### ui\focus-flow-app\src\components\music\PlaylistCard.tsx(NEW)

References: 

- ui\focus-flow-app\src\components\ui\Card.tsx

Create playlist card component:
- Display playlist cover image, name, track count, duration
- Music service badge (Spotify, YouTube Music)
- Effectiveness score indicator (if available)
- Play button to start playlist
- Save/favorite button
- Click handler to view playlist details
- Props: playlist (Playlist data), onPlay, onSave, onClick
- Responsive design
- Hover effects

### ui\focus-flow-app\src\components\music\NowPlaying.tsx(NEW)

References: 

- ui\focus-flow-app\src\components\ui\Card.tsx

Create now playing widget component:
- Display current track info (title, artist, album art)
- Playback controls (play/pause, next, previous)
- Progress bar with current time / total time
- Volume control slider
- Playlist name
- Minimize/expand toggle
- Props: playbackState, onPlay, onPause, onNext, onPrevious, onVolumeChange
- Responsive design
- Sticky positioning (bottom of screen or sidebar)
- Animations for track changes

### ui\focus-flow-app\src\components\insights\InsightCard.tsx(NEW)

References: 

- ui\focus-flow-app\src\components\ui\Card.tsx

Create insight card component:
- Display insight title, content, and priority indicator
- Insight type badge (pattern, recommendation, coaching)
- Read/unread visual state
- Mark as read button
- Dismiss button
- Timestamp
- Click handler to expand full insight
- Props: insight (Insight data), onMarkRead, onDismiss, onClick
- Responsive design
- Priority-based color coding

### ui\focus-flow-app\src\components\insights\PatternVisualization.tsx(NEW)

References: 

- ui\focus-flow-app\src\components\ui\Card.tsx

Create pattern visualization component:
- Chart/graph displaying detected pattern data
- Support different pattern types (time-of-day: bar chart, duration: histogram, consistency: line chart)
- Use recharts or chart.js for visualizations
- Insight text explaining the pattern
- Actionable recommendations
- Props: pattern (Pattern data), type
- Responsive design
- Interactive tooltips

### ui\focus-flow-app\src\types\index.ts(MODIFY)

Extend TypeScript type definitions:
- Add Goal interface (id, userId, category, goalType, targetValue, currentValue, timePeriod, priorityRank, isActive, createdAt, updatedAt)
- Add WeeklySchedule interface (id, userId, weekStartDate, isBaseSchedule, isActive, timeBlocks)
- Add TimeBlock interface (id, scheduleId, dayOfWeek, startTime, endTime, category, activityName, isLocked, isFlexible, notes)
- Add Achievement interface (id, userId, achievementType, title, description, icon, unlockedAt, progress, isUnlocked)
- Add UserLevel interface (userId, currentLevel, currentXP, xpToNextLevel, totalXP)
- Add Streak interface (userId, currentStreak, longestStreak, lastSessionDate)
- Add Playlist interface (id, name, source, trackCount, duration, effectivenessScore)
- Add Insight interface (id, userId, insightType, title, content, priority, isRead, generatedAt)
- Add Pattern interface (id, userId, patternType, description, confidenceScore, detectedAt)
- Export all new interfaces

### ui\focus-flow-app\src\App.tsx(MODIFY)

Update App component to include new routes:
- Add route for `/onboarding` -> Onboarding page
- Add route for `/schedule` -> Schedule page
- Add route for `/goals` -> Goals page
- Add route for `/gamification` -> Gamification page
- Add route for `/music` -> Music page
- Add route for `/insights` -> Insights page
- Update default redirect logic to check if user has completed onboarding (redirect to /onboarding if not, /dashboard if yes)
- Import all new page components

### ui\focus-flow-app\src\components\layout\Sidebar.tsx(MODIFY)

Update Sidebar component to include new navigation items:
- Add navigation link for Schedule (calendar icon)
- Add navigation link for Goals (target icon)
- Add navigation link for Gamification (trophy icon)
- Add navigation link for Music (music icon)
- Add navigation link for Insights (lightbulb icon)
- Maintain existing links: Dashboard, Timer, Analytics, Templates, Settings
- Update active state highlighting for new routes
- Add badge indicators for unread insights count
- Responsive design with collapsible sidebar on mobile

### ui\focus-flow-app\src\pages\Dashboard.tsx(MODIFY)

Enhance Dashboard page with new features:
- Add weekly schedule preview widget (next 3 days)
- Add active goals progress widget
- Add current level and XP widget
- Add current streak widget
- Add recent insights widget (top 3 unread)
- Add now playing music widget (if music is active)
- Update stats cards to include: Total Sessions, Focus Time, Weekly Goal Progress, Current Streak
- Add quick actions: Start Session, View Schedule, Check Insights
- Integrate with new Redux slices (gameSlice, scheduleSlice, goalsSlice, insightsSlice)
- Fetch data from multiple services on mount
- Responsive grid layout

### ui\focus-flow-app\src\pages\Analytics.tsx(MODIFY)

Enhance Analytics page with advanced features:
- Add trend charts (productivity over time, session count trends, completion rate trends)
- Add comparison view (week-over-week, month-over-month)
- Add category breakdown pie chart
- Add time-of-day productivity heatmap
- Add goal progress tracking section
- Add export functionality (CSV, JSON, PDF)
- Add date range selector
- Add filter by session type and category
- Integrate with Analytics service API
- Use recharts for visualizations
- Responsive design with mobile-optimized charts

### ui\focus-flow-app\src\pages\Timer.tsx(MODIFY)

Enhance Timer page with new integrations:
- Add music control widget (select playlist, playback controls)
- Add current goal display (which goal this session contributes to)
- Add XP preview (how much XP will be earned)
- Add achievement progress indicators (close to unlocking)
- Add session type selector with templates from Focus Engine
- Integrate with musicSlice for music controls
- Integrate with gameSlice for XP/achievement display
- Call Game Engine API on session completion to award XP
- Call Music Control API to track playlist effectiveness
- Enhanced session completion modal with XP earned, achievements unlocked, and insights

### ui\focus-flow-app\src\pages\Settings.tsx(MODIFY)

Enhance Settings page with new configuration options:
- Add User Profile section (chronotype, personality preferences, edit profile)
- Add Priorities section (edit category priorities with drag-and-drop ranking)
- Add Notification Preferences (schedule reminders, achievement notifications, insight notifications)
- Add Music Integration section (connect/disconnect Spotify, YouTube Music)
- Add AI Settings (enable/disable AI insights, coaching frequency)
- Add Gamification Settings (enable/disable gamification, show/hide leaderboards)
- Add Data & Privacy section (export data, delete account)
- Add existing timer settings
- Use appropriate API calls to save settings
- Responsive design with organized sections

### docker-compose.yml(NEW)

Create Docker Compose configuration for local development:
- Define services:
  - focus_engine (port 8000, depends on postgres, redis)
  - game_engine (port 8001, depends on postgres, redis)
  - music_control (port 8002, depends on postgres)
  - ai_insights (port 8003, depends on postgres)
  - analytics (port 8004, depends on postgres, redis)
  - postgres (port 5432, with volume for data persistence)
  - redis (port 6379, with volume for data persistence)
  - frontend (port 3000, depends on all backend services)
- Environment variables for each service
- Volume mounts for development (hot reload)
- Network configuration for inter-service communication
- Health checks for each service
- Restart policies

### README.md(MODIFY)

Update README with comprehensive project documentation:
- Add project overview describing the full vision from brainstorm document
- Add architecture diagram (microservices overview)
- Add features list (completed and planned)
- Add setup instructions:
  - Prerequisites (Python, Node.js, Docker, PostgreSQL, Redis)
  - Environment configuration (.env files for each service)
  - Database setup and migrations
  - Running services individually or with Docker Compose
  - Frontend setup and development
- Add API documentation links for each service
- Add development workflow guidelines
- Add testing instructions
- Add deployment considerations
- Add contributing guidelines
- Update technology stack section with all technologies used
- Add roadmap section with phases from brainstorm

### PROGRESS.md(MODIFY)

Update PROGRESS.md with new development phases:
- Mark Phase B (Focus Engine) as complete
- Add Phase C: Microservices Implementation
  - C1: Game Engine service (achievements, levels, streaks, leaderboards)
  - C2: Music Control service (Spotify/YouTube Music integration, playlists, playback)
  - C3: AI Insights service (pattern discovery, insights generation, coaching)
  - C4: Analytics service (trends, metrics, comparisons, export)
- Add Phase D: Frontend Integration
  - D1: New Redux slices and API clients
  - D2: Onboarding flow implementation
  - D3: Schedule management UI
  - D4: Goals management UI
  - D5: Gamification UI
  - D6: Music control UI
  - D7: Insights UI
  - D8: Enhanced Dashboard and Analytics
- Add Phase E: Advanced Features
  - E1: Schedule generation algorithm
  - E2: Sprint mode functionality
  - E3: Weekly/monthly feedback system
  - E4: AI-powered schedule optimization
  - E5: Calendar integration (Google, Apple, Outlook)
- Add Phase F: Polish and Launch
  - F1: Comprehensive testing
  - F2: Performance optimization
  - F3: Mobile responsiveness
  - F4: Documentation
  - F5: Deployment setup

### resources\docs\api\API_OVERVIEW.md(NEW)

Create API overview documentation:
- Document all microservices and their responsibilities
- List all API endpoints by service with brief descriptions
- Document inter-service communication patterns
- Document authentication and authorization (future)
- Document common request/response formats
- Document error handling conventions
- Document rate limiting policies
- Document WebSocket endpoints and events
- Include service URLs and ports
- Include example requests and responses for key endpoints

### resources\docs\architecture\MICROSERVICES_ARCHITECTURE.md(NEW)

Create microservices architecture documentation:
- Describe overall architecture and design principles
- Document each service's responsibilities and boundaries
- Document data flow between services
- Document database schema for each service
- Document shared data models and contracts
- Document service discovery and communication patterns
- Document scalability considerations
- Document deployment architecture
- Include architecture diagrams (service dependencies, data flow)
- Document technology choices and rationale

### resources\docs\features\SCHEDULING_ALGORITHM.md(NEW)

Create scheduling algorithm documentation:
- Describe the schedule generation algorithm in detail
- Document inputs: user profile, goals, priorities, mandatory blocks, chronotype
- Document algorithm steps:
  1. Place mandatory blocks (locked)
  2. Calculate available time per day
  3. Allocate time based on priority rankings
  4. Distribute goal-related activities
  5. Optimize timing based on chronotype
  6. Balance categories across the week
  7. Add buffer time and flexibility
- Document sprint mode modifications
- Document schedule validation rules
- Document AI-powered optimization (future)
- Include pseudocode and examples
- Document edge cases and handling