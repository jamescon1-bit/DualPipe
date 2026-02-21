"""
Cambridge NY Commercial Operations - Route Optimization System

Daily route optimization for NYC service crews. Optimizes routes considering
crew starting locations, client addresses across all NYC boroughs, time windows,
job durations, and NYC traffic patterns.

Accounts for rush hour traffic, bridge/tunnel congestion, and borough-specific
routing challenges to minimize travel time and maximize service efficiency.
"""

from datetime import datetime, timedelta, time
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple, Set
from enum import Enum
import math
from itertools import permutations


class TrafficPattern(Enum):
    """NYC traffic patterns throughout the day."""
    EARLY_MORNING = "early_morning"    # 5:00-7:00 AM
    MORNING_RUSH = "morning_rush"      # 7:00-10:00 AM  
    MID_DAY = "mid_day"                # 10:00 AM-2:00 PM
    AFTERNOON = "afternoon"            # 2:00-4:00 PM
    EVENING_RUSH = "evening_rush"      # 4:00-7:00 PM
    EVENING = "evening"                # 7:00-10:00 PM
    NIGHT = "night"                    # 10:00 PM-5:00 AM


class Borough(Enum):
    """NYC boroughs."""
    MANHATTAN = "Manhattan"
    BROOKLYN = "Brooklyn" 
    QUEENS = "Queens"
    BRONX = "Bronx"
    STATEN_ISLAND = "Staten Island"


@dataclass
class RouteLocation:
    """Location for route optimization."""
    id: str
    name: str
    address: str
    borough: Borough
    coordinates: Tuple[float, float]  # (lat, lon)
    service_duration: timedelta
    time_window: Optional[Tuple[datetime, datetime]] = None
    priority: int = 1  # 1=highest, 5=lowest
    access_notes: str = ""
    parking_difficulty: int = 1  # 1=easy, 5=very difficult


@dataclass 
class RouteSegment:
    """Segment between two locations in a route."""
    from_location: RouteLocation
    to_location: RouteLocation
    distance_miles: float
    estimated_travel_time: timedelta
    traffic_factor: float
    notes: str = ""


@dataclass
class OptimizedRoute:
    """Complete optimized route for a crew."""
    crew_id: str
    start_location: RouteLocation
    locations: List[RouteLocation]
    segments: List[RouteSegment]
    total_distance: float
    total_travel_time: timedelta
    total_service_time: timedelta
    estimated_completion: datetime
    efficiency_score: float


class NYCRouteOptimizer:
    """
    Route optimization system for Cambridge NY service crews.
    
    Optimizes daily routes across NYC boroughs considering:
    - Traffic patterns and rush hours
    - Bridge/tunnel congestion
    - Parking difficulty by location
    - Client time windows
    - Service priorities
    """
    
    def __init__(self):
        # Traffic multipliers by time of day (base = 1.0)
        self.traffic_multipliers = {
            TrafficPattern.EARLY_MORNING: 0.8,
            TrafficPattern.MORNING_RUSH: 1.8,
            TrafficPattern.MID_DAY: 1.0,
            TrafficPattern.AFTERNOON: 1.1,
            TrafficPattern.EVENING_RUSH: 2.0,
            TrafficPattern.EVENING: 1.2,
            TrafficPattern.NIGHT: 0.7,
        }
        
        # Base travel times between boroughs (minutes, mid-day traffic)
        self.base_travel_times = {
            # From Manhattan
            (Borough.MANHATTAN, Borough.MANHATTAN): 15,
            (Borough.MANHATTAN, Borough.BROOKLYN): 25,
            (Borough.MANHATTAN, Borough.QUEENS): 35,
            (Borough.MANHATTAN, Borough.BRONX): 30,
            (Borough.MANHATTAN, Borough.STATEN_ISLAND): 55,
            
            # From Brooklyn  
            (Borough.BROOKLYN, Borough.MANHATTAN): 25,
            (Borough.BROOKLYN, Borough.BROOKLYN): 20,
            (Borough.BROOKLYN, Borough.QUEENS): 25,
            (Borough.BROOKLYN, Borough.BRONX): 45,
            (Borough.BROOKLYN, Borough.STATEN_ISLAND): 35,
            
            # From Queens
            (Borough.QUEENS, Borough.MANHATTAN): 35,
            (Borough.QUEENS, Borough.BROOKLYN): 25, 
            (Borough.QUEENS, Borough.QUEENS): 25,
            (Borough.QUEENS, Borough.BRONX): 30,
            (Borough.QUEENS, Borough.STATEN_ISLAND): 50,
            
            # From Bronx
            (Borough.BRONX, Borough.MANHATTAN): 30,
            (Borough.BRONX, Borough.BROOKLYN): 45,
            (Borough.BRONX, Borough.QUEENS): 30,
            (Borough.BRONX, Borough.BRONX): 20,
            (Borough.BRONX, Borough.STATEN_ISLAND): 65,
            
            # From Staten Island
            (Borough.STATEN_ISLAND, Borough.MANHATTAN): 55,
            (Borough.STATEN_ISLAND, Borough.BROOKLYN): 35,
            (Borough.STATEN_ISLAND, Borough.QUEENS): 50,
            (Borough.STATEN_ISLAND, Borough.BRONX): 65,
            (Borough.STATEN_ISLAND, Borough.STATEN_ISLAND): 15,
        }
        
        # Bridge/tunnel congestion factors  
        self.bridge_tunnel_factors = {
            # Manhattan bridges/tunnels have higher congestion
            (Borough.MANHATTAN, Borough.BROOKLYN): 1.3,
            (Borough.MANHATTAN, Borough.QUEENS): 1.4,
            (Borough.BROOKLYN, Borough.MANHATTAN): 1.3,
            (Borough.QUEENS, Borough.MANHATTAN): 1.4,
            (Borough.STATEN_ISLAND, Borough.BROOKLYN): 1.2,
        }
    
    def get_traffic_pattern(self, dt: datetime) -> TrafficPattern:
        """Determine traffic pattern based on time of day."""
        hour = dt.hour
        
        if 5 <= hour < 7:
            return TrafficPattern.EARLY_MORNING
        elif 7 <= hour < 10:
            return TrafficPattern.MORNING_RUSH
        elif 10 <= hour < 14:
            return TrafficPattern.MID_DAY
        elif 14 <= hour < 16:
            return TrafficPattern.AFTERNOON
        elif 16 <= hour < 19:
            return TrafficPattern.EVENING_RUSH
        elif 19 <= hour < 22:
            return TrafficPattern.EVENING
        else:
            return TrafficPattern.NIGHT
    
    def calculate_travel_time(self, from_loc: RouteLocation, to_loc: RouteLocation, 
                            departure_time: datetime) -> timedelta:
        """
        Calculate travel time between two locations accounting for traffic.
        
        Args:
            from_loc: Starting location
            to_loc: Destination location  
            departure_time: When the crew will depart
            
        Returns:
            Estimated travel time including traffic
        """
        # Get base travel time
        base_minutes = self.base_travel_times.get(
            (from_loc.borough, to_loc.borough), 30
        )
        
        # Apply traffic multiplier
        traffic_pattern = self.get_traffic_pattern(departure_time)
        traffic_multiplier = self.traffic_multipliers[traffic_pattern]
        
        # Apply bridge/tunnel congestion if applicable
        bridge_factor = self.bridge_tunnel_factors.get(
            (from_loc.borough, to_loc.borough), 1.0
        )
        
        # Add parking difficulty factor
        parking_factor = 1.0 + (to_loc.parking_difficulty - 1) * 0.1
        
        # Calculate final travel time
        adjusted_minutes = base_minutes * traffic_multiplier * bridge_factor * parking_factor
        
        return timedelta(minutes=int(adjusted_minutes))
    
    def calculate_distance(self, from_loc: RouteLocation, to_loc: RouteLocation) -> float:
        """Calculate approximate distance between locations in miles."""
        lat1, lon1 = from_loc.coordinates
        lat2, lon2 = to_loc.coordinates
        
        # Haversine formula
        dlat = math.radians(lat2 - lat1)
        dlon = math.radians(lon2 - lon1)
        a = (math.sin(dlat/2) * math.sin(dlat/2) + 
             math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * 
             math.sin(dlon/2) * math.sin(dlon/2))
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
        distance = 3959 * c  # Earth radius in miles
        
        # Add NYC city factor (streets aren't straight lines)
        return distance * 1.3
    
    def optimize_route_greedy(self, start_location: RouteLocation, 
                            locations: List[RouteLocation],
                            start_time: datetime) -> OptimizedRoute:
        """
        Optimize route using greedy nearest-neighbor approach.
        Good for larger sets of locations where brute force is impractical.
        
        Args:
            start_location: Starting point (typically Cambridge office)
            locations: List of client locations to visit
            start_time: Route start time
            
        Returns:
            Optimized route
        """
        if not locations:
            return OptimizedRoute(
                crew_id="", start_location=start_location, locations=[],
                segments=[], total_distance=0.0, total_travel_time=timedelta(),
                total_service_time=timedelta(), estimated_completion=start_time,
                efficiency_score=0.0
            )
        
        route_locations = []
        remaining_locations = locations.copy()
        current_location = start_location
        current_time = start_time
        segments = []
        total_distance = 0.0
        total_travel_time = timedelta()
        total_service_time = timedelta()
        
        # Greedy selection: always go to nearest available location
        while remaining_locations:
            # Find nearest location that can be serviced
            best_location = None
            best_travel_time = timedelta(hours=24)  # Max time
            
            for location in remaining_locations:
                # Check if location can be visited within time window
                travel_time = self.calculate_travel_time(current_location, location, current_time)
                arrival_time = current_time + travel_time
                
                if location.time_window:
                    if arrival_time > location.time_window[1]:
                        continue  # Too late
                    # If we arrive early, wait until window opens
                    if arrival_time < location.time_window[0]:
                        arrival_time = location.time_window[0]
                        travel_time = arrival_time - current_time
                
                # Prefer higher priority locations in case of tie
                adjusted_time = travel_time.total_seconds() / location.priority
                
                if timedelta(seconds=adjusted_time) < best_travel_time:
                    best_location = location
                    best_travel_time = travel_time
            
            if not best_location:
                # No more locations can be reached, end route
                break
            
            # Add location to route
            distance = self.calculate_distance(current_location, best_location)
            segment = RouteSegment(
                from_location=current_location,
                to_location=best_location,
                distance_miles=distance,
                estimated_travel_time=best_travel_time,
                traffic_factor=self.traffic_multipliers[self.get_traffic_pattern(current_time)]
            )
            
            segments.append(segment)
            route_locations.append(best_location)
            remaining_locations.remove(best_location)
            
            # Update totals
            total_distance += distance
            total_travel_time += best_travel_time
            total_service_time += best_location.service_duration
            
            # Move to next location
            current_location = best_location
            current_time += best_travel_time + best_location.service_duration
        
        # Calculate efficiency score
        efficiency_score = self._calculate_efficiency_score(
            segments, total_service_time, total_travel_time
        )
        
        return OptimizedRoute(
            crew_id="",
            start_location=start_location,
            locations=route_locations,
            segments=segments,
            total_distance=total_distance,
            total_travel_time=total_travel_time,
            total_service_time=total_service_time,
            estimated_completion=current_time,
            efficiency_score=efficiency_score
        )
    
    def optimize_route_brute_force(self, start_location: RouteLocation,
                                 locations: List[RouteLocation], 
                                 start_time: datetime) -> OptimizedRoute:
        """
        Optimize route using brute force (try all permutations).
        Best for small sets of locations (≤8 locations).
        
        Args:
            start_location: Starting point  
            locations: List of client locations to visit
            start_time: Route start time
            
        Returns:
            Optimal route
        """
        if len(locations) > 8:
            # Too many locations for brute force, use greedy
            return self.optimize_route_greedy(start_location, locations, start_time)
        
        if not locations:
            return OptimizedRoute(
                crew_id="", start_location=start_location, locations=[],
                segments=[], total_distance=0.0, total_travel_time=timedelta(),
                total_service_time=timedelta(), estimated_completion=start_time,
                efficiency_score=0.0
            )
        
        best_route = None
        best_score = float('inf')
        
        # Try all permutations of locations
        for perm in permutations(locations):
            route = self._evaluate_route_permutation(start_location, list(perm), start_time)
            if route and route.efficiency_score < best_score:
                best_route = route
                best_score = route.efficiency_score
        
        return best_route or self.optimize_route_greedy(start_location, locations, start_time)
    
    def _evaluate_route_permutation(self, start_location: RouteLocation,
                                  ordered_locations: List[RouteLocation],
                                  start_time: datetime) -> Optional[OptimizedRoute]:
        """Evaluate a specific permutation of locations."""
        current_location = start_location
        current_time = start_time
        segments = []
        total_distance = 0.0
        total_travel_time = timedelta()
        total_service_time = timedelta()
        
        for location in ordered_locations:
            travel_time = self.calculate_travel_time(current_location, location, current_time)
            arrival_time = current_time + travel_time
            
            # Check time window constraints
            if location.time_window:
                if arrival_time > location.time_window[1]:
                    return None  # Infeasible route
                if arrival_time < location.time_window[0]:
                    # Wait until window opens
                    arrival_time = location.time_window[0]
                    travel_time = arrival_time - current_time
            
            distance = self.calculate_distance(current_location, location)
            segment = RouteSegment(
                from_location=current_location,
                to_location=location,
                distance_miles=distance,
                estimated_travel_time=travel_time,
                traffic_factor=self.traffic_multipliers[self.get_traffic_pattern(current_time)]
            )
            
            segments.append(segment)
            total_distance += distance
            total_travel_time += travel_time
            total_service_time += location.service_duration
            
            current_location = location
            current_time = arrival_time + location.service_duration
        
        efficiency_score = self._calculate_efficiency_score(
            segments, total_service_time, total_travel_time
        )
        
        return OptimizedRoute(
            crew_id="",
            start_location=start_location,
            locations=ordered_locations,
            segments=segments,
            total_distance=total_distance,
            total_travel_time=total_travel_time,
            total_service_time=total_service_time,
            estimated_completion=current_time,
            efficiency_score=efficiency_score
        )
    
    def _calculate_efficiency_score(self, segments: List[RouteSegment],
                                  service_time: timedelta, travel_time: timedelta) -> float:
        """
        Calculate route efficiency score (lower is better).
        
        Factors:
        - Travel time vs service time ratio
        - Distance penalty
        - Traffic penalty during rush hours
        """
        if not segments:
            return 0.0
        
        # Travel to service ratio (want more service, less travel)
        if service_time.total_seconds() > 0:
            time_ratio = travel_time.total_seconds() / service_time.total_seconds()
        else:
            time_ratio = float('inf')
        
        # Distance penalty
        total_distance = sum(s.distance_miles for s in segments)
        distance_penalty = total_distance * 0.1
        
        # Rush hour penalty
        rush_penalty = sum(
            s.traffic_factor - 1.0 for s in segments 
            if s.traffic_factor > 1.5
        )
        
        return time_ratio + distance_penalty + rush_penalty
    
    def optimize_multi_crew_routes(self, crews: List[str], 
                                 start_locations: Dict[str, RouteLocation],
                                 all_locations: List[RouteLocation],
                                 start_time: datetime) -> Dict[str, OptimizedRoute]:
        """
        Optimize routes for multiple crews simultaneously.
        
        Args:
            crews: List of crew IDs
            start_locations: Starting location for each crew
            all_locations: All client locations to be visited
            start_time: Route start time
            
        Returns:
            Dictionary mapping crew IDs to their optimized routes
        """
        # Simple load balancing: distribute locations among crews
        locations_per_crew = len(all_locations) // len(crews)
        remainder = len(all_locations) % len(crews)
        
        routes = {}
        location_index = 0
        
        for i, crew_id in enumerate(crews):
            # Determine how many locations this crew gets
            crew_location_count = locations_per_crew
            if i < remainder:
                crew_location_count += 1
            
            # Assign locations to this crew
            crew_locations = all_locations[location_index:location_index + crew_location_count]
            location_index += crew_location_count
            
            # Optimize route for this crew
            start_loc = start_locations.get(crew_id)
            if start_loc and crew_locations:
                route = self.optimize_route_greedy(start_loc, crew_locations, start_time)
                route.crew_id = crew_id
                routes[crew_id] = route
        
        return routes
    
    def generate_route_summary(self, route: OptimizedRoute) -> str:
        """Generate a human-readable summary of the route."""
        summary = f"Route for {route.crew_id or 'crew'}:\n"
        summary += f"  Start: {route.start_location.name} ({route.start_location.borough.value})\n"
        summary += f"  Locations: {len(route.locations)}\n"
        summary += f"  Total distance: {route.total_distance:.1f} miles\n"
        summary += f"  Travel time: {route.total_travel_time}\n" 
        summary += f"  Service time: {route.total_service_time}\n"
        summary += f"  Estimated completion: {route.estimated_completion.strftime('%I:%M %p')}\n"
        summary += f"  Efficiency score: {route.efficiency_score:.2f}\n"
        
        summary += "\n  Stop sequence:\n"
        for i, location in enumerate(route.locations):
            summary += f"    {i+1}. {location.name} ({location.borough.value})\n"
            summary += f"       Service: {location.service_duration}\n"
            if location.time_window:
                tw_start = location.time_window[0].strftime('%I:%M %p')
                tw_end = location.time_window[1].strftime('%I:%M %p') 
                summary += f"       Window: {tw_start} - {tw_end}\n"
        
        return summary


def create_sample_route_data() -> Tuple[RouteLocation, List[RouteLocation]]:
    """Create sample data for testing route optimization."""
    
    # Cambridge NY office (starting point)
    cambridge_office = RouteLocation(
        id="cambridge_office",
        name="Cambridge NY Office",
        address="22-12 40th Ave, Long Island City, NY 11101", 
        borough=Borough.QUEENS,
        coordinates=(40.7589, -73.9441),
        service_duration=timedelta(minutes=0),
        parking_difficulty=2
    )
    
    # Sample client locations across NYC
    locations = [
        RouteLocation(
            id="weill_cornell",
            name="Weill Cornell Medical Center",
            address="1300 York Ave, New York, NY 10065",
            borough=Borough.MANHATTAN,
            coordinates=(40.7648, -73.9536),
            service_duration=timedelta(hours=1, minutes=30),
            time_window=(datetime(2026, 2, 24, 9, 0), datetime(2026, 2, 24, 17, 0)),
            priority=2,
            parking_difficulty=4
        ),
        RouteLocation(
            id="brooklyn_hospital",
            name="Brooklyn Hospital Center", 
            address="121 DeKalb Ave, Brooklyn, NY 11201",
            borough=Borough.BROOKLYN,
            coordinates=(40.6892, -73.9814),
            service_duration=timedelta(hours=1),
            time_window=(datetime(2026, 2, 24, 10, 0), datetime(2026, 2, 24, 16, 0)),
            priority=1,
            parking_difficulty=3
        ),
        RouteLocation(
            id="queens_courthouse",
            name="Queens County Supreme Court",
            address="88-11 Sutphin Blvd, Jamaica, NY 11435",
            borough=Borough.QUEENS,
            coordinates=(40.7021, -73.8074),
            service_duration=timedelta(minutes=45),
            time_window=(datetime(2026, 2, 24, 11, 0), datetime(2026, 2, 24, 15, 0)),
            priority=2,
            parking_difficulty=2
        ),
        RouteLocation(
            id="bronx_zoo",
            name="Bronx Zoo Administrative Building",
            address="2300 Southern Blvd, Bronx, NY 10460", 
            borough=Borough.BRONX,
            coordinates=(40.8502, -73.8772),
            service_duration=timedelta(hours=2),
            time_window=(datetime(2026, 2, 24, 8, 0), datetime(2026, 2, 24, 18, 0)),
            priority=3,
            parking_difficulty=1
        ),
        RouteLocation(
            id="hospital_brooklyn",
            name="NYU Langone Hospital Brooklyn",
            address="150 55th St, Brooklyn, NY 11220",
            borough=Borough.BROOKLYN,
            coordinates=(40.6414, -74.0134),
            service_duration=timedelta(hours=1, minutes=15),
            time_window=(datetime(2026, 2, 24, 12, 0), datetime(2026, 2, 24, 16, 0)),
            priority=1,
            parking_difficulty=3
        )
    ]
    
    return cambridge_office, locations


if __name__ == "__main__":
    # Example usage
    optimizer = NYCRouteOptimizer()
    
    # Load sample data
    start_location, client_locations = create_sample_route_data()
    
    # Optimize route starting at 8:00 AM
    start_time = datetime(2026, 2, 24, 8, 0)
    
    print("=== Route Optimization Demo ===")
    print(f"Start time: {start_time.strftime('%Y-%m-%d %I:%M %p')}")
    print(f"Start location: {start_location.name}")
    print(f"Client locations: {len(client_locations)}")
    
    # Try greedy optimization
    print("\n--- Greedy Optimization ---")
    greedy_route = optimizer.optimize_route_greedy(start_location, client_locations, start_time)
    print(optimizer.generate_route_summary(greedy_route))
    
    # Try brute force optimization (for comparison)
    print("\n--- Brute Force Optimization ---")
    bf_route = optimizer.optimize_route_brute_force(start_location, client_locations, start_time)
    print(optimizer.generate_route_summary(bf_route))
    
    # Multi-crew example
    print("\n--- Multi-Crew Routing ---")
    crews = ["crew_1", "crew_2"]
    start_locations = {
        "crew_1": start_location,
        "crew_2": start_location  # Both start from office
    }
    
    multi_routes = optimizer.optimize_multi_crew_routes(
        crews, start_locations, client_locations, start_time
    )
    
    for crew_id, route in multi_routes.items():
        print(f"\n{crew_id.upper()}:")
        print(optimizer.generate_route_summary(route))