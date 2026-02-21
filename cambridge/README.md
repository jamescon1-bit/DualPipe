# Cambridge NY Commercial Operations - DualPipe Job Scheduling & Route Optimization

This module provides AI-powered job scheduling and route optimization tools for Cambridge NY (cambridgeny.com), a commercial floral, plant, and landscaping design company serving all NYC boroughs.

## Overview

Cambridge NY handles:
- Commercial landscaping for office buildings, hospitals, universities
- Holiday decor installation/takedown
- Interior plant maintenance & rentals  
- Weekly lobby flower arrangements
- Municipal and HOA contracts

**Office Location:** 22-12 40th Ave, Long Island City, NY 11101

## Modules

### 1. Job Scheduler (`job_scheduler.py`)
Multi-crew job scheduling system that optimally assigns maintenance crews to client locations across NYC boroughs.

**Key Features:**
- Weekly plant maintenance route planning
- Holiday decor install/takedown scheduling  
- Lobby flower delivery coordination
- Priority handling (urgent vs routine maintenance)
- Travel time optimization between NYC locations
- Crew skill matching (plant care, holiday decor, landscaping, etc.)

**Example Usage:**
```python
from job_scheduler import JobScheduler, Job, CrewMember, JobType, Priority

scheduler = JobScheduler()

# Add jobs and crew members
scheduler.add_job(job)
scheduler.add_crew_member(crew_member)

# Schedule weekly maintenance
weekly_assignments = scheduler.schedule_weekly_maintenance(datetime(2026, 2, 24))

# Generate daily schedule
daily_schedule = scheduler.generate_daily_schedule(datetime(2026, 2, 24))
```

### 2. Route Optimizer (`route_optimizer.py`)
Daily route optimization for NYC service crews, accounting for traffic patterns and NYC-specific challenges.

**Key Features:**
- NYC borough-to-borough travel time estimation
- Rush hour and traffic pattern modeling
- Bridge/tunnel congestion factors
- Parking difficulty scoring
- Client time window constraints
- Multi-crew route coordination

**Example Usage:**
```python
from route_optimizer import NYCRouteOptimizer, RouteLocation, Borough

optimizer = NYCRouteOptimizer()

# Optimize single crew route
route = optimizer.optimize_route_greedy(start_location, client_locations, start_time)

# Optimize multiple crew routes
multi_routes = optimizer.optimize_multi_crew_routes(crews, start_locations, all_locations, start_time)

# Generate route summary
summary = optimizer.generate_route_summary(route)
```

### 3. Seasonal Planner (`seasonal_planner.py`)
Annual planning calendar for holiday seasons, plant cycles, and budget forecasting.

**Key Features:**
- Holiday decoration season management (Thanksgiving→Christmas→New Year→Valentine's→Easter→Summer)
- Plant replacement cycle planning based on species and environmental conditions
- Seasonal flower availability tracking
- Client budget forecasting by service line
- Supplier relationship management

**Example Usage:**
```python
from seasonal_planner import SeasonalPlanner, ClientProfile, Season

planner = SeasonalPlanner()
planner.add_client(client_profile)

# Plan plant replacements for the year
replacement_events = planner.plan_plant_replacements(2026)

# Plan holiday decorations
holiday_events = planner.plan_holiday_decorations(2026)

# Generate budget forecasts
budgets = planner.forecast_seasonal_budgets(2026)

# Get seasonal calendar
calendar = planner.generate_seasonal_calendar(2026)
```

## Data Models

### Core Entities
- **Location**: Client sites across NYC boroughs with coordinates and access details
- **Job**: Work orders with type, duration, skills required, priority, and time windows
- **CrewMember**: Staff with skills, availability, and hourly rates
- **PlantSpecies**: Plant varieties with replacement cycles and seasonal availability
- **HolidayDecorTheme**: Decoration packages with installation windows and pricing

### Enums
- **JobType**: Plant maintenance, holiday decor, lobby flowers, landscaping, etc.
- **Priority**: Urgent, high, normal, low
- **CrewSkill**: Plant care, holiday decor, landscaping, floral design, NYC driving
- **Borough**: Manhattan, Brooklyn, Queens, Bronx, Staten Island  
- **Season**: Spring, summer, fall, winter
- **HolidaySeason**: Thanksgiving, Christmas, New Year, Valentine's, Easter, etc.

## NYC-Specific Considerations

### Traffic Patterns
- Morning rush (7:00-10:00 AM): 1.8x travel time multiplier
- Evening rush (4:00-7:00 PM): 2.0x travel time multiplier
- Bridge/tunnel congestion factors
- Borough-specific parking difficulty scoring

### Seasonal Operations
- Holiday decor installation windows aligned with NYC business calendar
- Plant species availability based on Northeast growing seasons
- Weather-dependent outdoor work scheduling
- Municipal contract timing requirements

## Integration Points

This module integrates with:
- **LPLB**: Crew workload balancing and inventory optimization
- **DeepGEMM**: Financial analytics and profitability analysis
- **External APIs**: Weather, traffic, supplier inventory systems
- **Client Systems**: Building management, facility scheduling

## Performance Considerations

- Route optimization uses greedy algorithm for >8 locations (O(n²))
- Brute force optimization for ≤8 locations (optimal solution)
- Travel time matrix cached for common borough pairs
- Seasonal data pre-computed for faster planning

## Error Handling

- Graceful degradation when crew skills don't match job requirements
- Fallback routing when traffic data unavailable
- Time window constraint validation with warnings
- Missing plant availability handled with estimated defaults

---

*Built for Cambridge NY commercial operations - optimizing plant care and holiday magic across NYC since 2026.*