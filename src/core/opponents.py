import random

class Opponent:
    """
    Represents a competing AI lab/organization that the player is racing against.
    Each opponent has hidden stats that can be discovered through espionage.
    """
    
    def __init__(self, name, budget, capabilities_researchers, lobbyists, compute, description=""):
        """
        Initialize an opponent with hidden stats.
        
        Args:
            name (str): Display name of the opponent organization
            budget (int): Available funding for the opponent
            capabilities_researchers (int): Number of researchers working on capabilities
            lobbyists (int): Number of lobbyists influencing policy
            compute (int): Available compute resources
            description (str): Optional description of the opponent
        """
        self.name = name
        self.budget = budget
        self.capabilities_researchers = capabilities_researchers
        self.lobbyists = lobbyists
        self.compute = compute
        self.description = description
        
        # Progress toward deploying dangerous AGI (0-100)
        self.progress = random.randint(15, 40)
        
        # Track what stats have been discovered by the player
        self.discovered_stats = {
            'budget': False,
            'capabilities_researchers': False,
            'lobbyists': False,
            'compute': False,
            'progress': False
        }
        
        # Track known values (what the player thinks they are)
        self.known_stats = {
            'budget': None,
            'capabilities_researchers': None,
            'lobbyists': None,
            'compute': None,
            'progress': None
        }
        
        # Whether this opponent has been discovered at all
        self.discovered = False
        
    def scout_stat(self, stat_name):
        """
        Attempt to scout a specific stat of this opponent.
        Returns tuple (success, revealed_value, message)
        """
        if stat_name not in self.discovered_stats:
            return False, None, f"Unknown stat: {stat_name}"
            
        if self.discovered_stats[stat_name]:
            # Already discovered, return known value
            actual_value = getattr(self, stat_name)
            return True, actual_value, f"{self.name}'s {stat_name}: {actual_value} (already known)"
            
        # Attempt to discover the stat (70% success rate)
        if random.random() < 0.7:
            self.discovered_stats[stat_name] = True
            actual_value = getattr(self, stat_name)
            # Add some noise to the discovered value
            if stat_name == 'progress':
                noise = random.randint(-3, 3)
                revealed_value = max(0, min(100, actual_value + noise))
            else:
                noise = random.randint(-2, 2)
                revealed_value = max(0, actual_value + noise)
                
            self.known_stats[stat_name] = revealed_value
            return True, revealed_value, f"Discovered {self.name}'s {stat_name}: {revealed_value}"
        else:
            return False, None, f"Failed to scout {self.name}'s {stat_name}"
            
    def discover(self):
        """Mark this opponent as discovered by the player."""
        self.discovered = True
        
    def take_turn(self):
        """
        Execute the opponent's AI behavior for one turn.
        Returns a list of messages describing what the opponent did.
        """
        messages = []
        
        if not self.discovered:
            # Undiscovered opponents act in secret
            return []
            
        # Simple AI logic: spend budget on various activities
        if self.budget > 0:
            # Prioritize capabilities research if low on progress
            if self.progress < 60 and self.budget >= 50:
                spent = min(50, self.budget)
                self.budget -= spent
                progress_gain = random.randint(3, 8)
                self.progress = min(100, self.progress + progress_gain)
                messages.append(f"{self.name} invested ${spent}k in capabilities research (+{progress_gain} progress)")
                
            # Hire more researchers if budget allows
            elif self.budget >= 80 and self.capabilities_researchers < 20:
                self.budget -= 80
                new_researchers = random.randint(1, 3)
                self.capabilities_researchers += new_researchers
                messages.append(f"{self.name} hired {new_researchers} new researchers")
                
            # Buy compute if needed
            elif self.budget >= 60 and self.compute < 50:
                self.budget -= 60
                new_compute = random.randint(15, 25)
                self.compute += new_compute
                messages.append(f"{self.name} purchased {new_compute} compute units")
                
            # Lobbying efforts
            elif self.budget >= 40 and self.lobbyists < 10:
                self.budget -= 40
                new_lobbyists = random.randint(1, 2)
                self.lobbyists += new_lobbyists
                messages.append(f"{self.name} hired {new_lobbyists} lobbyists")
                
        # Research progress based on resources
        base_progress = self.capabilities_researchers * 0.5
        compute_bonus = min(self.compute * 0.1, 5)  # Cap compute bonus
        total_progress = base_progress + compute_bonus
        
        if total_progress > 0:
            actual_gain = random.randint(int(total_progress * 0.5), int(total_progress * 1.5))
            self.progress = min(100, self.progress + actual_gain)
            if actual_gain > 0:
                messages.append(f"{self.name} made research progress (+{actual_gain}, total: {self.progress}/100)")
                
        return messages
        
    def get_impact_on_doom(self):
        """
        Calculate how much this opponent's capabilities research increases global doom.
        Called during turn processing to add doom pressure.
        """
        if not self.discovered:
            # Undiscovered opponents still contribute to doom, but less visibly
            return random.randint(0, 2)
            
        # Discovered opponents' doom impact is based on their capabilities research
        base_doom = self.capabilities_researchers * 0.2
        progress_multiplier = 1 + (self.progress / 100)  # More dangerous as they get closer
        return int(base_doom * progress_multiplier)


def create_default_opponents():
    """
    Create the default set of 3 opponents for the game.
    Returns a list of Opponent objects with varied stats and personalities.
    """
    opponents = []
    
    # Opponent 1: Well-funded tech giant
    opponents.append(Opponent(
        name="TechCorp Labs",
        budget=random.randint(800, 1200),
        capabilities_researchers=random.randint(15, 25),
        lobbyists=random.randint(8, 12),
        compute=random.randint(60, 100),
        description="A massive tech corporation with deep pockets and aggressive timelines"
    ))
    
    # Opponent 2: Government-backed research institute
    opponents.append(Opponent(
        name="National AI Initiative",
        budget=random.randint(600, 900),
        capabilities_researchers=random.randint(12, 20),
        lobbyists=random.randint(15, 20),
        compute=random.randint(40, 80),
        description="Government-funded program with strong regulatory influence"
    ))
    
    # Opponent 3: Stealth startup with unknown backing
    opponents.append(Opponent(
        name="Frontier Dynamics",
        budget=random.randint(400, 800),
        capabilities_researchers=random.randint(8, 15),
        lobbyists=random.randint(2, 6),
        compute=random.randint(20, 60),
        description="Secretive startup with mysterious funding and rapid development"
    ))
    
    # Opponent 4: Palandir - Advanced surveillance and intelligence corporation
    opponents.append(Opponent(
        name="Palandir",
        budget=random.randint(1000, 1500),
        capabilities_researchers=random.randint(20, 30),
        lobbyists=random.randint(12, 18),
        compute=random.randint(80, 120),
        description="Advanced surveillance technology corporation with global data monitoring capabilities"
    ))
    
    return opponents