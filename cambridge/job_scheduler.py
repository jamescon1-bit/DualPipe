"""
Cambridge NY Commercial Operations - Job Scheduling System

Multi-crew job scheduling system for optimal assignment of maintenance crews 
to client locations across NYC boroughs. Handles weekly plant maintenance routes,
holiday decor install/takedown windows, lobby flower delivery schedules.

Supports priorities (urgent replacements vs routine maintenance), travel time
between NYC locations, and crew skill matching.
"""

from datetime import datetime, timedelta
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple, Set
from enum import Enum
import math


class JobType(Enum):
    """Types of jobs Cambridge NY handles."""
    PLANT_MAINTENANCE = "plant_maintenance"
    HOLIDAY_DECOR_INSTALL = "holiday_decor_install" 
    HOLIDAY_DECOR_TAKEDOWN = "holiday_decor_takedown"
    LOBBY_FLOWERS = "lobby_flowers"
    EMERGENCY_REPLACEMENT = "emergency_replacement"
    LANDSCAPING = "landscaping"


class Priority(Enum):
    """Job priority levels."""
    URGENT = 1          # Same day service needed
    HIGH = 2            # Within 24-48 hours  
    NORMAL = 3          # Standard weekly maintenance
    LOW = 4             # Can be delayed if needed


class CrewSkill(Enum):
    """Crew skill categories."""
    PLANT_CARE = "plant_care"
    HOLIDAY_DECOR = "holiday_decor" 
    LANDSCAPING = "landscaping"
    FLORAL_DESIGN = "floral_design"
    HEAVY_LIFTING = "heavy_lifting"
    NYC_DRIVING = "nyc_driving"


@dataclass
class Location:
    """Client location information."""
    id: str
    name: str
    address: str
    borough: str  # Manhattan, Brooklyn, Queens, Bronx, Staten Island
    coordinates: Tuple[float, float]  # (lat, lon)
    access_notes: str = ""


@dataclass
class CrewMember:
    """Individual crew member with skills."""
    id: str
    name: str
    skills: Set[CrewSkill]
    hourly_rate: float
    availability: Dict[str, List[Tuple[str, str]]]  # day_of_week -> [(start, end)]


@dataclass
class Job:
    """Individual job to be scheduled."""
    id: str
    job_type: JobType
    client_location: Location
    estimated_duration: timedelta
    required_skills: Set[CrewSkill]
    priority: Priority
    time_window: Tuple[datetime, datetime]  # (earliest_start, latest_finish)
    notes: str = ""
    plant_count: int = 0
    square_footage: float = 0.0


@dataclass
class CrewAssignment:
    """Assignment of crew members to jobs."""
    crew_members: List[CrewMember]
    jobs: List[Job]
    start_location: Location
    estimated_total_time: timedelta
    estimated_travel_time: timedelta
    total_cost: float


class JobScheduler:
    """
    Multi-crew job scheduling system for Cambridge NY operations.
    
    Optimally assigns maintenance crews to client locations across NYC,
    considering travel time, crew skills, priorities, and time windows.
    """
    
    def __init__(self):
        self.jobs: List[Job] = []
        self.crew_members: List[CrewMember] = []
        self.assignments: List[CrewAssignment] = []
        
        # NYC travel time matrix (simplified - minutes between boroughs)
        self.travel_times = {
            ("Manhattan", "Manhattan"): 20,
            ("Manhattan", "Brooklyn"): 35,
            ("Manhattan", "Queens"): 45,
            ("Manhattan", "Bronx"): 40,
            ("Manhattan", "Staten Island"): 60,
            ("Brooklyn", "Brooklyn"): 25,
            ("Brooklyn", "Queens"): 30,
            ("Brooklyn", "Bronx"): 50,
            ("Brooklyn", "Staten Island"): 45,
            ("Queens", "Queens"): 30,
            ("Queens", "Bronx"): 35,
            ("Queens", "Staten Island"): 55,
            ("Bronx", "Bronx"): 25,
            ("Bronx", "Staten Island"): 70,
            ("Staten Island", "Staten Island"): 20,
        }
        
        # Make travel times symmetric
        for (a, b), time in list(self.travel_times.items()):
            if (b, a) not in self.travel_times:
                self.travel_times[(b, a)] = time
    
    def add_job(self, job: Job) -> None:
        """Add a job to be scheduled."""
        self.jobs.append(job)
    
    def add_crew_member(self, crew_member: CrewMember) -> None:
        """Add a crew member to available workforce."""
        self.crew_members.append(crew_member)
    
    def get_travel_time(self, from_borough: str, to_borough: str) -> int:
        """Get estimated travel time between boroughs in minutes."""
        return self.travel_times.get((from_borough, to_borough), 45)  # default 45min
    
    def calculate_distance(self, loc1: Location, loc2: Location) -> float:
        """Calculate approximate distance between locations in miles."""
        lat1, lon1 = loc1.coordinates
        lat2, lon2 = loc2.coordinates
        
        # Haversine formula approximation for NYC area
        dlat = math.radians(lat2 - lat1)
        dlon = math.radians(lon2 - lon1)
        a = (math.sin(dlat/2) * math.sin(dlat/2) + 
             math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * 
             math.sin(dlon/2) * math.sin(dlon/2))
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
        distance = 3959 * c  # Earth radius in miles
        return distance
    
    def crew_has_skills(self, crew: List[CrewMember], required_skills: Set[CrewSkill]) -> bool:
        """Check if crew collectively has required skills."""
        available_skills = set()
        for member in crew:
            available_skills.update(member.skills)
        return required_skills.issubset(available_skills)
    
    def schedule_weekly_maintenance(self, week_start: datetime) -> List[CrewAssignment]:
        """
        Schedule weekly plant maintenance routes across NYC.
        
        Args:
            week_start: Start date of the week to schedule
            
        Returns:
            List of crew assignments for the week
        """
        # Filter jobs for plant maintenance in the target week
        maintenance_jobs = [
            job for job in self.jobs 
            if job.job_type == JobType.PLANT_MAINTENANCE
            and week_start <= job.time_window[0] < week_start + timedelta(days=7)
        ]
        
        # Sort by priority and time window
        maintenance_jobs.sort(key=lambda j: (j.priority.value, j.time_window[0]))
        
        assignments = []
        available_crew = self.crew_members.copy()
        
        for job in maintenance_jobs:
            # Find best crew for this job
            best_crew = self._find_optimal_crew(job, available_crew)
            if best_crew:
                assignment = self._create_assignment([job], best_crew, week_start)
                assignments.append(assignment)
                
                # Remove assigned crew members for this time slot
                for member in best_crew:
                    if member in available_crew:
                        available_crew.remove(member)
        
        return assignments
    
    def schedule_holiday_decor(self, season: str, year: int) -> List[CrewAssignment]:
        """
        Schedule holiday decor installation and takedown for a season.
        
        Args:
            season: Holiday season (e.g., 'christmas', 'valentines')
            year: Target year
            
        Returns:
            List of crew assignments for holiday decor
        """
        # Define holiday windows
        holiday_windows = {
            'thanksgiving': (datetime(year, 11, 1), datetime(year, 11, 25)),
            'christmas': (datetime(year, 11, 25), datetime(year, 12, 23)),
            'newyear': (datetime(year, 12, 26), datetime(year + 1, 1, 8)),
            'valentines': (datetime(year + 1, 1, 15), datetime(year + 1, 2, 10)),
            'easter': (datetime(year + 1, 3, 1), datetime(year + 1, 4, 15)),
        }
        
        window = holiday_windows.get(season.lower())
        if not window:
            raise ValueError(f"Unknown holiday season: {season}")
        
        # Filter holiday decor jobs
        decor_jobs = [
            job for job in self.jobs 
            if job.job_type in [JobType.HOLIDAY_DECOR_INSTALL, JobType.HOLIDAY_DECOR_TAKEDOWN]
            and window[0] <= job.time_window[0] <= window[1]
        ]
        
        return self._optimize_assignments(decor_jobs)
    
    def _find_optimal_crew(self, job: Job, available_crew: List[CrewMember]) -> Optional[List[CrewMember]]:
        """Find the optimal crew for a specific job."""
        required_skills = job.required_skills
        
        # Try different crew sizes (1-3 members typically)
        for crew_size in range(1, min(4, len(available_crew) + 1)):
            from itertools import combinations
            
            for crew_combo in combinations(available_crew, crew_size):
                crew = list(crew_combo)
                if self.crew_has_skills(crew, required_skills):
                    return crew
        
        return None
    
    def _create_assignment(self, jobs: List[Job], crew: List[CrewMember], 
                         start_date: datetime) -> CrewAssignment:
        """Create a crew assignment with cost and time estimates."""
        # Calculate total time and costs
        total_duration = sum([job.estimated_duration for job in jobs], timedelta())
        
        # Estimate travel time between job locations
        total_travel = timedelta()
        if len(jobs) > 1:
            for i in range(len(jobs) - 1):
                travel_min = self.get_travel_time(
                    jobs[i].client_location.borough,
                    jobs[i + 1].client_location.borough
                )
                total_travel += timedelta(minutes=travel_min)
        
        # Calculate cost
        total_cost = 0.0
        total_time_hours = (total_duration + total_travel).total_seconds() / 3600
        for member in crew:
            total_cost += member.hourly_rate * total_time_hours
        
        # Default start location (Cambridge office)
        start_location = Location(
            id="cambridge_office",
            name="Cambridge NY Office", 
            address="22-12 40th Ave, Long Island City, NY 11101",
            borough="Queens",
            coordinates=(40.7589, -73.9441)
        )
        
        return CrewAssignment(
            crew_members=crew,
            jobs=jobs,
            start_location=start_location,
            estimated_total_time=total_duration + total_travel,
            estimated_travel_time=total_travel,
            total_cost=total_cost
        )
    
    def _optimize_assignments(self, jobs: List[Job]) -> List[CrewAssignment]:
        """Optimize crew assignments for a list of jobs."""
        assignments = []
        remaining_jobs = jobs.copy()
        available_crew = self.crew_members.copy()
        
        # Sort jobs by priority and time constraints
        remaining_jobs.sort(key=lambda j: (j.priority.value, j.time_window[0]))
        
        while remaining_jobs and available_crew:
            job = remaining_jobs.pop(0)
            crew = self._find_optimal_crew(job, available_crew)
            
            if crew:
                assignment = self._create_assignment([job], crew, job.time_window[0])
                assignments.append(assignment)
                
                # Remove crew from available pool
                for member in crew:
                    if member in available_crew:
                        available_crew.remove(member)
        
        return assignments
    
    def generate_daily_schedule(self, date: datetime) -> Dict[str, List[CrewAssignment]]:
        """
        Generate optimized daily schedule for all crews.
        
        Args:
            date: Target date for scheduling
            
        Returns:
            Dictionary mapping crew IDs to their daily assignments
        """
        daily_jobs = [
            job for job in self.jobs 
            if job.time_window[0].date() <= date.date() <= job.time_window[1].date()
        ]
        
        assignments = self._optimize_assignments(daily_jobs)
        
        # Group assignments by crew
        schedule = {}
        for i, assignment in enumerate(assignments):
            crew_id = f"crew_{i}"
            schedule[crew_id] = assignment
        
        return schedule


def create_sample_data() -> Tuple[List[Job], List[CrewMember]]:
    """Create sample data for testing the job scheduler."""
    
    # Sample locations across NYC
    locations = [
        Location("loc1", "Weill Cornell Medical Center", "1300 York Ave, New York, NY 10065", 
                "Manhattan", (40.7648, -73.9536)),
        Location("loc2", "Brooklyn Hospital Center", "121 DeKalb Ave, Brooklyn, NY 11201",
                "Brooklyn", (40.6892, -73.9814)),
        Location("loc3", "Queens Borough Hall", "120-55 Queens Blvd, Kew Gardens, NY 11424",
                "Queens", (40.7282, -73.8465)),
        Location("loc4", "Bronx Museum", "1040 Grand Concourse, Bronx, NY 10451",
                "Bronx", (40.8295, -73.9231)),
    ]
    
    # Sample jobs
    jobs = [
        Job(
            id="job1",
            job_type=JobType.PLANT_MAINTENANCE,
            client_location=locations[0],
            estimated_duration=timedelta(hours=2),
            required_skills={CrewSkill.PLANT_CARE},
            priority=Priority.NORMAL,
            time_window=(datetime(2026, 2, 24), datetime(2026, 2, 28)),
            plant_count=25,
            square_footage=1500.0
        ),
        Job(
            id="job2", 
            job_type=JobType.LOBBY_FLOWERS,
            client_location=locations[1],
            estimated_duration=timedelta(hours=1),
            required_skills={CrewSkill.FLORAL_DESIGN},
            priority=Priority.HIGH,
            time_window=(datetime(2026, 2, 24), datetime(2026, 2, 24)),
            notes="Weekly lobby arrangement replacement"
        ),
        Job(
            id="job3",
            job_type=JobType.HOLIDAY_DECOR_INSTALL,
            client_location=locations[2], 
            estimated_duration=timedelta(hours=4),
            required_skills={CrewSkill.HOLIDAY_DECOR, CrewSkill.HEAVY_LIFTING},
            priority=Priority.NORMAL,
            time_window=(datetime(2026, 11, 20), datetime(2026, 11, 30)),
            notes="Christmas decor installation"
        )
    ]
    
    # Sample crew members
    crew_members = [
        CrewMember(
            id="crew1",
            name="Maria Rodriguez",
            skills={CrewSkill.PLANT_CARE, CrewSkill.FLORAL_DESIGN, CrewSkill.NYC_DRIVING},
            hourly_rate=28.0,
            availability={"monday": [("08:00", "16:00")], "tuesday": [("08:00", "16:00")]}
        ),
        CrewMember(
            id="crew2", 
            name="James Chen",
            skills={CrewSkill.HOLIDAY_DECOR, CrewSkill.HEAVY_LIFTING, CrewSkill.NYC_DRIVING},
            hourly_rate=32.0,
            availability={"monday": [("07:00", "15:00")], "wednesday": [("08:00", "16:00")]}
        ),
        CrewMember(
            id="crew3",
            name="Sarah Williams",
            skills={CrewSkill.PLANT_CARE, CrewSkill.LANDSCAPING, CrewSkill.NYC_DRIVING},
            hourly_rate=30.0,
            availability={"tuesday": [("09:00", "17:00")], "thursday": [("08:00", "16:00")]}
        )
    ]
    
    return jobs, crew_members


if __name__ == "__main__":
    # Example usage
    scheduler = JobScheduler()
    
    # Load sample data
    jobs, crew_members = create_sample_data()
    
    for job in jobs:
        scheduler.add_job(job)
    
    for crew_member in crew_members:
        scheduler.add_crew_member(crew_member)
    
    # Schedule weekly maintenance
    week_start = datetime(2026, 2, 24)
    weekly_assignments = scheduler.schedule_weekly_maintenance(week_start)
    
    print(f"Weekly maintenance schedule starting {week_start.strftime('%Y-%m-%d')}:")
    for i, assignment in enumerate(weekly_assignments):
        print(f"\nAssignment {i + 1}:")
        print(f"  Crew: {', '.join([m.name for m in assignment.crew_members])}")
        print(f"  Jobs: {', '.join([j.id for j in assignment.jobs])}")
        print(f"  Total time: {assignment.estimated_total_time}")
        print(f"  Travel time: {assignment.estimated_travel_time}")
        print(f"  Estimated cost: ${assignment.total_cost:.2f}")
    
    # Generate daily schedule
    daily_schedule = scheduler.generate_daily_schedule(datetime(2026, 2, 24))
    print(f"\nDaily schedule for 2026-02-24:")
    for crew_id, assignment in daily_schedule.items():
        print(f"  {crew_id}: {len(assignment.jobs)} jobs, ${assignment.total_cost:.2f}")