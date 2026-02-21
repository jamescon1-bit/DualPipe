"""
Cambridge NY Commercial Operations - Seasonal Planning System

Annual planning calendar for Cambridge NY operations covering:
- Holiday decor seasons (Thanksgiving → Christmas → New Year → Valentine's → Easter → Summer)
- Plant replacement cycles based on species and environmental conditions
- Seasonal flower availability and sourcing
- Budget forecasting per client and service line

Integrates with supplier schedules, client contracts, and historical data to optimize
seasonal operations and maximize profitability throughout the year.
"""

from datetime import datetime, timedelta, date
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple, Set
from enum import Enum
import calendar


class Season(Enum):
    """Seasonal periods for Cambridge NY operations."""
    SPRING = "spring"
    SUMMER = "summer"
    FALL = "fall"
    WINTER = "winter"


class HolidaySeason(Enum):
    """Holiday decoration seasons."""
    THANKSGIVING = "thanksgiving"
    CHRISTMAS = "christmas"
    NEW_YEAR = "new_year"
    VALENTINES = "valentines"
    EASTER = "easter"
    SUMMER_EVENTS = "summer_events"
    BACK_TO_SCHOOL = "back_to_school"
    HALLOWEEN = "halloween"


class PlantType(Enum):
    """Categories of plants handled by Cambridge NY."""
    TROPICAL_FOLIAGE = "tropical_foliage"
    FLOWERING_PLANTS = "flowering_plants"
    SUCCULENTS = "succulents"
    FERNS = "ferns"
    PALMS = "palms"
    SEASONAL_COLOR = "seasonal_color"
    OUTDOOR_PERENNIALS = "outdoor_perennials"
    ANNUALS = "annuals"


class ServiceType(Enum):
    """Types of services Cambridge NY provides."""
    PLANT_MAINTENANCE = "plant_maintenance"
    HOLIDAY_DECOR = "holiday_decor"
    LOBBY_FLOWERS = "lobby_flowers"
    LANDSCAPING = "landscaping"
    PLANT_RENTALS = "plant_rentals"


@dataclass
class PlantSpecies:
    """Individual plant species with seasonal characteristics."""
    name: str
    plant_type: PlantType
    replacement_cycle_months: int
    peak_seasons: List[Season]
    cost_per_unit: float
    availability_calendar: Dict[int, float]  # month -> availability (0.0-1.0)
    care_difficulty: int  # 1=easy, 5=very difficult
    preferred_environments: List[str]  # e.g., ["office", "hospital", "lobby"]


@dataclass
class HolidayDecorTheme:
    """Holiday decoration theme with seasonal timing."""
    name: str
    holiday_season: HolidaySeason
    install_window: Tuple[date, date]  # (earliest_install, latest_install)
    takedown_window: Tuple[date, date]  # (earliest_takedown, latest_takedown)
    materials_cost_per_sqft: float
    labor_hours_per_sqft: float
    markup_percentage: float
    popular_colors: List[str]
    required_materials: List[str]


@dataclass
class ClientProfile:
    """Client profile for seasonal planning."""
    id: str
    name: str
    industry: str  # "healthcare", "corporate", "education", etc.
    budget_annual: float
    services_subscribed: List[ServiceType]
    square_footage: float
    plant_count: int
    holiday_decor_preference: Optional[HolidayDecorTheme]
    contract_renewal_date: date
    seasonal_preferences: Dict[Season, List[str]]  # season -> preferred plants/themes


@dataclass
class SeasonalBudget:
    """Budget forecast for a specific season and client."""
    client_id: str
    season: Season
    year: int
    estimated_revenue: float
    estimated_costs: float
    estimated_profit: float
    service_breakdown: Dict[ServiceType, float]
    confidence_level: float  # 0.0-1.0


@dataclass
class SeasonalEvent:
    """Scheduled seasonal event or milestone."""
    name: str
    event_type: str  # "plant_replacement", "decor_install", "supplier_delivery"
    scheduled_date: date
    duration_days: int
    affected_clients: List[str]
    estimated_revenue: float
    notes: str = ""


class SeasonalPlanner:
    """
    Annual seasonal planning system for Cambridge NY operations.
    
    Manages holiday decoration cycles, plant replacement schedules,
    seasonal flower availability, and client budget forecasting.
    """
    
    def __init__(self):
        self.plant_species: List[PlantSpecies] = []
        self.holiday_themes: List[HolidayDecorTheme] = []
        self.clients: List[ClientProfile] = []
        self.seasonal_events: List[SeasonalEvent] = []
        
        # Initialize default holiday seasons
        self._initialize_holiday_seasons()
        
        # Initialize plant species database
        self._initialize_plant_database()
    
    def _initialize_holiday_seasons(self):
        """Initialize default holiday decoration seasons."""
        current_year = datetime.now().year
        
        self.holiday_themes = [
            HolidayDecorTheme(
                name="Thanksgiving Harvest",
                holiday_season=HolidaySeason.THANKSGIVING,
                install_window=(date(current_year, 10, 15), date(current_year, 11, 15)),
                takedown_window=(date(current_year, 11, 25), date(current_year, 12, 1)),
                materials_cost_per_sqft=3.50,
                labor_hours_per_sqft=0.3,
                markup_percentage=0.65,
                popular_colors=["orange", "gold", "burgundy", "brown"],
                required_materials=["pumpkins", "gourds", "fall_foliage", "corn_stalks"]
            ),
            HolidayDecorTheme(
                name="Christmas Traditional",
                holiday_season=HolidaySeason.CHRISTMAS,
                install_window=(date(current_year, 11, 20), date(current_year, 12, 15)),
                takedown_window=(date(current_year, 12, 26), date(current_year + 1, 1, 10)),
                materials_cost_per_sqft=5.25,
                labor_hours_per_sqft=0.5,
                markup_percentage=0.75,
                popular_colors=["red", "gold", "green", "silver"],
                required_materials=["garland", "wreaths", "lights", "ornaments", "poinsettias"]
            ),
            HolidayDecorTheme(
                name="New Year Elegant",
                holiday_season=HolidaySeason.NEW_YEAR,
                install_window=(date(current_year, 12, 26), date(current_year + 1, 1, 5)),
                takedown_window=(date(current_year + 1, 1, 15), date(current_year + 1, 1, 30)),
                materials_cost_per_sqft=4.00,
                labor_hours_per_sqft=0.35,
                markup_percentage=0.70,
                popular_colors=["gold", "silver", "black", "white"],
                required_materials=["metallic_accents", "champagne_florals", "sparklers"]
            ),
            HolidayDecorTheme(
                name="Valentine Romance",
                holiday_season=HolidaySeason.VALENTINES,
                install_window=(date(current_year + 1, 1, 25), date(current_year + 1, 2, 10)),
                takedown_window=(date(current_year + 1, 2, 15), date(current_year + 1, 2, 28)),
                materials_cost_per_sqft=4.75,
                labor_hours_per_sqft=0.4,
                markup_percentage=0.80,
                popular_colors=["red", "pink", "white", "gold"],
                required_materials=["roses", "heart_shapes", "romantic_lighting"]
            ),
            HolidayDecorTheme(
                name="Easter Spring",
                holiday_season=HolidaySeason.EASTER,
                install_window=(date(current_year + 1, 3, 1), date(current_year + 1, 4, 10)),
                takedown_window=(date(current_year + 1, 4, 15), date(current_year + 1, 4, 30)),
                materials_cost_per_sqft=3.75,
                labor_hours_per_sqft=0.3,
                markup_percentage=0.65,
                popular_colors=["pastel_pink", "lavender", "yellow", "green"],
                required_materials=["spring_flowers", "easter_eggs", "bunny_accents", "pastel_ribbons"]
            )
        ]
    
    def _initialize_plant_database(self):
        """Initialize database of plant species with seasonal characteristics."""
        self.plant_species = [
            PlantSpecies(
                name="Dracaena marginata",
                plant_type=PlantType.TROPICAL_FOLIAGE,
                replacement_cycle_months=18,
                peak_seasons=[Season.SPRING, Season.SUMMER],
                cost_per_unit=35.00,
                availability_calendar={1: 0.8, 2: 0.9, 3: 1.0, 4: 1.0, 5: 0.9, 6: 0.8,
                                     7: 0.7, 8: 0.8, 9: 1.0, 10: 1.0, 11: 0.9, 12: 0.8},
                care_difficulty=2,
                preferred_environments=["office", "lobby", "retail"]
            ),
            PlantSpecies(
                name="Pothos",
                plant_type=PlantType.TROPICAL_FOLIAGE,
                replacement_cycle_months=24,
                peak_seasons=[Season.SPRING, Season.SUMMER, Season.FALL],
                cost_per_unit=18.00,
                availability_calendar={i: 1.0 for i in range(1, 13)},  # Always available
                care_difficulty=1,
                preferred_environments=["office", "healthcare", "education"]
            ),
            PlantSpecies(
                name="Poinsettia",
                plant_type=PlantType.SEASONAL_COLOR,
                replacement_cycle_months=2,
                peak_seasons=[Season.WINTER],
                cost_per_unit=12.00,
                availability_calendar={1: 0.3, 2: 0.1, 3: 0.0, 4: 0.0, 5: 0.0, 6: 0.0,
                                     7: 0.0, 8: 0.0, 9: 0.0, 10: 0.3, 11: 0.9, 12: 1.0},
                care_difficulty=4,
                preferred_environments=["lobby", "retail", "hospitality"]
            ),
            PlantSpecies(
                name="Boston Fern",
                plant_type=PlantType.FERNS,
                replacement_cycle_months=12,
                peak_seasons=[Season.SPRING, Season.SUMMER],
                cost_per_unit=28.00,
                availability_calendar={1: 0.6, 2: 0.7, 3: 0.9, 4: 1.0, 5: 1.0, 6: 0.9,
                                     7: 0.8, 8: 0.8, 9: 0.9, 10: 0.8, 11: 0.6, 12: 0.5},
                care_difficulty=3,
                preferred_environments=["healthcare", "spa", "lobby"]
            ),
            PlantSpecies(
                name="Snake Plant",
                plant_type=PlantType.SUCCULENTS,
                replacement_cycle_months=36,
                peak_seasons=[Season.SPRING, Season.FALL],
                cost_per_unit=42.00,
                availability_calendar={i: 0.9 for i in range(1, 13)},  # Consistently available
                care_difficulty=1,
                preferred_environments=["office", "healthcare", "corporate"]
            ),
            PlantSpecies(
                name="Chrysanthemums",
                plant_type=PlantType.SEASONAL_COLOR,
                replacement_cycle_months=3,
                peak_seasons=[Season.FALL],
                cost_per_unit=15.00,
                availability_calendar={1: 0.0, 2: 0.0, 3: 0.0, 4: 0.0, 5: 0.0, 6: 0.0,
                                     7: 0.2, 8: 0.6, 9: 1.0, 10: 1.0, 11: 0.8, 12: 0.3},
                care_difficulty=2,
                preferred_environments=["lobby", "retail", "outdoor"]
            )
        ]
    
    def get_season_from_date(self, target_date: date) -> Season:
        """Determine season from a given date."""
        month = target_date.month
        
        if month in [3, 4, 5]:
            return Season.SPRING
        elif month in [6, 7, 8]:
            return Season.SUMMER
        elif month in [9, 10, 11]:
            return Season.FALL
        else:  # 12, 1, 2
            return Season.WINTER
    
    def add_client(self, client: ClientProfile):
        """Add a client to the seasonal planning system."""
        self.clients.append(client)
    
    def plan_plant_replacements(self, year: int) -> List[SeasonalEvent]:
        """
        Plan plant replacement schedule for the entire year.
        
        Args:
            year: Target year for planning
            
        Returns:
            List of scheduled plant replacement events
        """
        replacement_events = []
        
        for client in self.clients:
            if ServiceType.PLANT_MAINTENANCE not in client.services_subscribed:
                continue
            
            # Calculate replacement schedule based on plant species and cycles
            for species in self.plant_species:
                if species.plant_type == PlantType.SEASONAL_COLOR:
                    # Seasonal plants need more frequent replacement
                    replacements_per_year = 12 // species.replacement_cycle_months
                    
                    for replacement_num in range(replacements_per_year):
                        # Schedule replacement during peak availability
                        target_month = None
                        best_availability = 0.0
                        
                        for month, availability in species.availability_calendar.items():
                            if availability > best_availability:
                                best_availability = availability
                                target_month = month
                        
                        if target_month:
                            # Spread replacements throughout the year
                            actual_month = (target_month + replacement_num * species.replacement_cycle_months - 1) % 12 + 1
                            replacement_date = date(year, actual_month, 15)  # Mid-month
                            
                            # Estimate quantity based on client plant count
                            estimated_quantity = int(client.plant_count * 0.1)  # 10% seasonal plants
                            estimated_cost = estimated_quantity * species.cost_per_unit
                            
                            event = SeasonalEvent(
                                name=f"{species.name} Replacement - {client.name}",
                                event_type="plant_replacement",
                                scheduled_date=replacement_date,
                                duration_days=1,
                                affected_clients=[client.id],
                                estimated_revenue=estimated_cost * 1.5,  # 50% markup
                                notes=f"Replace {estimated_quantity} {species.name} plants"
                            )
                            replacement_events.append(event)
                
                else:
                    # Long-term plants - less frequent replacement
                    if species.replacement_cycle_months <= 12:
                        replacements_per_year = 12 // species.replacement_cycle_months
                        
                        for replacement_num in range(replacements_per_year):
                            # Schedule during peak seasons
                            peak_month = 4  # Default to April
                            if species.peak_seasons:
                                season_months = {
                                    Season.SPRING: 4,
                                    Season.SUMMER: 7,
                                    Season.FALL: 10,
                                    Season.WINTER: 1
                                }
                                peak_month = season_months[species.peak_seasons[0]]
                            
                            actual_month = (peak_month + replacement_num * species.replacement_cycle_months - 1) % 12 + 1
                            replacement_date = date(year, actual_month, 1)
                            
                            estimated_quantity = int(client.plant_count * 0.05)  # 5% long-term plants
                            estimated_cost = estimated_quantity * species.cost_per_unit
                            
                            event = SeasonalEvent(
                                name=f"{species.name} Replacement - {client.name}",
                                event_type="plant_replacement", 
                                scheduled_date=replacement_date,
                                duration_days=2,
                                affected_clients=[client.id],
                                estimated_revenue=estimated_cost * 1.5,
                                notes=f"Replace {estimated_quantity} {species.name} plants"
                            )
                            replacement_events.append(event)
        
        return replacement_events
    
    def plan_holiday_decorations(self, year: int) -> List[SeasonalEvent]:
        """
        Plan holiday decoration installations and takedowns for the year.
        
        Args:
            year: Target year for planning
            
        Returns:
            List of scheduled holiday decoration events
        """
        holiday_events = []
        
        for client in self.clients:
            if ServiceType.HOLIDAY_DECOR not in client.services_subscribed:
                continue
            
            for theme in self.holiday_themes:
                # Installation event
                install_date = theme.install_window[0]
                if install_date.year != year:
                    # Adjust for year boundary (e.g., New Year)
                    if install_date.month <= 6:
                        install_date = install_date.replace(year=year)
                    else:
                        install_date = install_date.replace(year=year - 1)
                
                install_revenue = (client.square_footage * theme.materials_cost_per_sqft * 
                                 (1 + theme.markup_percentage))
                
                install_event = SeasonalEvent(
                    name=f"{theme.name} Installation - {client.name}",
                    event_type="decor_install",
                    scheduled_date=install_date,
                    duration_days=1,
                    affected_clients=[client.id],
                    estimated_revenue=install_revenue,
                    notes=f"Install {theme.name} theme across {client.square_footage} sq ft"
                )
                holiday_events.append(install_event)
                
                # Takedown event
                takedown_date = theme.takedown_window[0]
                if takedown_date.year != year and takedown_date.year != year + 1:
                    if takedown_date.month <= 6:
                        takedown_date = takedown_date.replace(year=year + 1)
                    else:
                        takedown_date = takedown_date.replace(year=year)
                
                takedown_revenue = install_revenue * 0.3  # 30% of install cost
                
                takedown_event = SeasonalEvent(
                    name=f"{theme.name} Takedown - {client.name}",
                    event_type="decor_takedown",
                    scheduled_date=takedown_date,
                    duration_days=1,
                    affected_clients=[client.id],
                    estimated_revenue=takedown_revenue,
                    notes=f"Remove and store {theme.name} decorations"
                )
                holiday_events.append(takedown_event)
        
        return holiday_events
    
    def forecast_seasonal_budgets(self, year: int) -> List[SeasonalBudget]:
        """
        Generate budget forecasts for each client by season.
        
        Args:
            year: Target year for forecasting
            
        Returns:
            List of seasonal budget forecasts
        """
        budgets = []
        
        for client in self.clients:
            for season in Season:
                # Calculate seasonal revenue based on services
                service_revenue = {}
                total_revenue = 0.0
                
                if ServiceType.PLANT_MAINTENANCE in client.services_subscribed:
                    # Quarterly maintenance revenue
                    maintenance_revenue = client.budget_annual * 0.4 / 4  # 40% of budget, quarterly
                    service_revenue[ServiceType.PLANT_MAINTENANCE] = maintenance_revenue
                    total_revenue += maintenance_revenue
                
                if ServiceType.HOLIDAY_DECOR in client.services_subscribed:
                    # Seasonal holiday decor revenue
                    if season == Season.FALL:  # Thanksgiving + Christmas prep
                        holiday_revenue = client.budget_annual * 0.3
                    elif season == Season.WINTER:  # Christmas + New Year + Valentine's
                        holiday_revenue = client.budget_annual * 0.25
                    elif season == Season.SPRING:  # Easter
                        holiday_revenue = client.budget_annual * 0.1
                    else:  # Summer
                        holiday_revenue = client.budget_annual * 0.05
                    
                    service_revenue[ServiceType.HOLIDAY_DECOR] = holiday_revenue
                    total_revenue += holiday_revenue
                
                if ServiceType.LOBBY_FLOWERS in client.services_subscribed:
                    # Weekly flowers - consistent throughout year
                    flowers_revenue = client.budget_annual * 0.2 / 4
                    service_revenue[ServiceType.LOBBY_FLOWERS] = flowers_revenue
                    total_revenue += flowers_revenue
                
                if ServiceType.LANDSCAPING in client.services_subscribed:
                    # Seasonal landscaping
                    if season in [Season.SPRING, Season.FALL]:
                        landscaping_revenue = client.budget_annual * 0.15
                    elif season == Season.SUMMER:
                        landscaping_revenue = client.budget_annual * 0.1
                    else:  # Winter - minimal outdoor work
                        landscaping_revenue = client.budget_annual * 0.02
                    
                    service_revenue[ServiceType.LANDSCAPING] = landscaping_revenue
                    total_revenue += landscaping_revenue
                
                # Estimate costs (typically 60% of revenue)
                total_costs = total_revenue * 0.6
                profit = total_revenue - total_costs
                
                # Confidence level based on client history and contract status
                confidence = 0.85  # Default high confidence
                if client.contract_renewal_date.year == year:
                    confidence -= 0.15  # Lower confidence during renewal year
                
                budget = SeasonalBudget(
                    client_id=client.id,
                    season=season,
                    year=year,
                    estimated_revenue=total_revenue,
                    estimated_costs=total_costs,
                    estimated_profit=profit,
                    service_breakdown=service_revenue,
                    confidence_level=confidence
                )
                budgets.append(budget)
        
        return budgets
    
    def generate_seasonal_calendar(self, year: int) -> Dict[int, List[SeasonalEvent]]:
        """
        Generate complete seasonal calendar for the year.
        
        Args:
            year: Target year
            
        Returns:
            Dictionary mapping months to scheduled events
        """
        all_events = []
        
        # Add plant replacement events
        all_events.extend(self.plan_plant_replacements(year))
        
        # Add holiday decoration events
        all_events.extend(self.plan_holiday_decorations(year))
        
        # Add custom seasonal events
        all_events.extend(self.seasonal_events)
        
        # Group events by month
        calendar_dict = {month: [] for month in range(1, 13)}
        
        for event in all_events:
            if event.scheduled_date.year == year:
                month = event.scheduled_date.month
                calendar_dict[month].append(event)
        
        # Sort events within each month
        for month_events in calendar_dict.values():
            month_events.sort(key=lambda e: e.scheduled_date.day)
        
        return calendar_dict
    
    def get_plant_availability(self, species_name: str, month: int) -> float:
        """Get plant availability for a specific species and month."""
        for species in self.plant_species:
            if species.name == species_name:
                return species.availability_calendar.get(month, 0.0)
        return 0.0
    
    def recommend_seasonal_plants(self, season: Season, environment: str) -> List[PlantSpecies]:
        """
        Recommend plants suitable for a season and environment.
        
        Args:
            season: Target season
            environment: Target environment (e.g., "office", "lobby")
            
        Returns:
            List of recommended plant species
        """
        recommendations = []
        
        for species in self.plant_species:
            if (season in species.peak_seasons and 
                environment in species.preferred_environments):
                recommendations.append(species)
        
        # Sort by care difficulty (easier first) and cost (lower first)
        recommendations.sort(key=lambda s: (s.care_difficulty, s.cost_per_unit))
        
        return recommendations


def create_sample_seasonal_data() -> Tuple[List[ClientProfile], SeasonalPlanner]:
    """Create sample data for testing seasonal planning."""
    
    planner = SeasonalPlanner()
    
    # Sample clients
    clients = [
        ClientProfile(
            id="client1",
            name="Weill Cornell Medical Center",
            industry="healthcare",
            budget_annual=45000.0,
            services_subscribed=[ServiceType.PLANT_MAINTENANCE, ServiceType.LOBBY_FLOWERS],
            square_footage=2500.0,
            plant_count=85,
            holiday_decor_preference=None,  # Healthcare facilities often skip holiday decor
            contract_renewal_date=date(2026, 6, 30),
            seasonal_preferences={
                Season.SPRING: ["pothos", "boston_fern"],
                Season.SUMMER: ["snake_plant", "dracaena"],
                Season.FALL: ["pothos", "snake_plant"],
                Season.WINTER: ["snake_plant", "pothos"]
            }
        ),
        ClientProfile(
            id="client2", 
            name="Brooklyn Corporate Plaza",
            industry="corporate",
            budget_annual=72000.0,
            services_subscribed=[
                ServiceType.PLANT_MAINTENANCE, 
                ServiceType.HOLIDAY_DECOR,
                ServiceType.LOBBY_FLOWERS
            ],
            square_footage=4200.0,
            plant_count=120,
            holiday_decor_preference=planner.holiday_themes[1],  # Christmas Traditional
            contract_renewal_date=date(2027, 12, 31),
            seasonal_preferences={
                Season.SPRING: ["dracaena", "boston_fern", "pothos"],
                Season.SUMMER: ["snake_plant", "dracaena"],
                Season.FALL: ["chrysanthemums", "pothos"],
                Season.WINTER: ["poinsettia", "snake_plant"]
            }
        ),
        ClientProfile(
            id="client3",
            name="Queens University Campus",
            industry="education", 
            budget_annual=38000.0,
            services_subscribed=[
                ServiceType.PLANT_MAINTENANCE,
                ServiceType.HOLIDAY_DECOR,
                ServiceType.LANDSCAPING
            ],
            square_footage=3100.0,
            plant_count=95,
            holiday_decor_preference=planner.holiday_themes[0],  # Thanksgiving Harvest
            contract_renewal_date=date(2026, 8, 15),
            seasonal_preferences={
                Season.SPRING: ["boston_fern", "dracaena"],
                Season.SUMMER: ["outdoor_plants", "snake_plant"],
                Season.FALL: ["chrysanthemums", "seasonal_color"],
                Season.WINTER: ["pothos", "snake_plant"]
            }
        )
    ]
    
    for client in clients:
        planner.add_client(client)
    
    return clients, planner


if __name__ == "__main__":
    # Example usage
    clients, planner = create_sample_seasonal_data()
    
    print("=== Cambridge NY Seasonal Planning Demo ===")
    
    # Generate seasonal calendar for 2026
    year = 2026
    seasonal_calendar = planner.generate_seasonal_calendar(year)
    
    print(f"\nSeasonal Calendar for {year}:")
    for month, events in seasonal_calendar.items():
        month_name = calendar.month_name[month]
        print(f"\n{month_name} ({len(events)} events):")
        
        for event in events[:3]:  # Show first 3 events per month
            print(f"  {event.scheduled_date.strftime('%m/%d')}: {event.name}")
            print(f"    Revenue: ${event.estimated_revenue:,.2f}")
    
    # Show budget forecasts
    print(f"\n=== Budget Forecasts for {year} ===")
    budgets = planner.forecast_seasonal_budgets(year)
    
    # Group by client
    client_budgets = {}
    for budget in budgets:
        if budget.client_id not in client_budgets:
            client_budgets[budget.client_id] = []
        client_budgets[budget.client_id].append(budget)
    
    for client_id, client_budget_list in client_budgets.items():
        client = next(c for c in clients if c.id == client_id)
        print(f"\n{client.name}:")
        
        annual_revenue = sum(b.estimated_revenue for b in client_budget_list)
        annual_profit = sum(b.estimated_profit for b in client_budget_list)
        
        print(f"  Annual Revenue: ${annual_revenue:,.2f}")
        print(f"  Annual Profit: ${annual_profit:,.2f}")
        print(f"  Profit Margin: {annual_profit/annual_revenue*100:.1f}%")
    
    # Plant recommendations
    print(f"\n=== Plant Recommendations ===")
    spring_office = planner.recommend_seasonal_plants(Season.SPRING, "office")
    print("Spring office plants:")
    for plant in spring_office[:3]:
        availability = planner.get_plant_availability(plant.name, 4)  # April
        print(f"  {plant.name}: ${plant.cost_per_unit} (availability: {availability*100:.0f}%)")