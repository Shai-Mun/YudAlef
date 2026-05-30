BLOON_CONFIG = {
    "bloon_0": {"round": 2, "color": "red", "count": 8, "load_time": 800, "cost": 25, "eco": 1},  # Grouped Red
    "bloon_1": {"round": 2, "color": "blue", "count": 6, "load_time": 1000, "cost": 25, "eco": 1}, # Spaced Blue

    "bloon_2": {"round": 4, "color": "blue", "count": 6, "load_time": 600, "cost": 42, "eco": 1.7},  # Grouped Blue
    "bloon_3": {"round": 4, "color": "pink", "count": 3, "load_time": 1000, "cost": 42, "eco": 1.7}, # Spaced Pink

    "bloon_4": {"round": 6, "color": "green", "count": 5, "load_time": 500, "cost": 60, "eco": 2.4},  # Grouped Green
    "bloon_5": {"round": 6, "color": "black", "count": 3, "load_time": 1000, "cost": 60, "eco": 2.4}, # Spaced Black

    "bloon_6": {"round": 8, "color": "yellow", "count": 5, "load_time": 250, "cost": 75, "eco": 3},  # Grouped Yellow
    "bloon_7": {"round": 8, "color": "white", "count": 4, "load_time": 1000, "cost": 90, "eco": 3},  # Spaced White

    "bloon_8": {"round": 10, "color": "pink", "count": 3, "load_time": 250, "cost": 90, "eco": 3.6}, # Grouped Pink
    "bloon_9": {"round": 10, "color": "lead", "count": 2, "load_time": 1000, "cost": 90, "eco": 3.6}, # Spaced Lead

    "bloon_10": {"round": 11, "color": "white", "count": 3, "load_time": 500, "cost": 125, "eco": 5}, # Grouped White
    "bloon_11": {"round": 11, "color": "zebra", "count": 3, "load_time": 1000, "cost": 125, "eco": 5},# Spaced Zebra

    "bloon_12": {"round": 12, "color": "black", "count": 3, "load_time": 500, "cost": 150, "eco": 6}, # Grouped Black
    "bloon_13": {"round": 12, "color": "rainbow", "count": 1, "load_time": 1000, "cost": 150, "eco": 3},# Spaced Rainbow

    "bloon_14": {"round": 13, "color": "zebra", "count": 3, "load_time": 500, "cost": 200, "eco": 6},  # Grouped Zebra
    "bloon_15": {"round": 13, "color": "rainbow", "count": 3, "load_time": 500, "cost": 450, "eco": 3},# Grouped Rainbow

    "bloon_16": {"round": 15, "color": "lead", "count": 4, "load_time": 1000, "cost": 200, "eco": 6},  # Grouped Lead
    "bloon_17": {"round": 15, "color": "ceramic", "count": 1, "load_time": 5000, "cost": 300, "eco": 0},# Spaced Ceramic

    "bloon_18": {"round": 18, "color": "ceramic", "count": 1, "load_time": 1000, "cost": 300, "eco": -5},# Fast Cooldown Ceramic
    "bloon_19": {"round": 18, "color": "moab", "count": 1, "load_time": 11000, "cost": 1500, "eco": -60},# Single MOAB

    "bloon_20": {"round": 20, "color": "moab", "count": 1, "load_time": 1000, "cost": 1500, "eco": -140},# Fast Cooldown MOAB
    "bloon_21": {"round": 20, "color": "bfb", "count": 1, "load_time": 15000, "cost": 2500, "eco": -350}, # Single BFB

    "bloon_22": {"round": 22, "color": "bfb", "count": 1, "load_time": 1000, "cost": 2500, "eco": -350}, # Fast Cooldown BFB
    "bloon_23": {"round": 22, "color": "zomg", "count": 1, "load_time": 22000, "cost": 9000, "eco": -1500},# Single ZOMG
}


MONKEY_DATA = {
    "dart_monkey": {
        "image": 'Dart Monkey.png',
        "base": {
            "cost": 200,
            "original_range": 150,
            "pierce": 1,
            "fire_rate": 940,  # ms
            "image": "dart_base.png",
            "projectile": "dart",
            "weaknesses": ["lead"],
            "projectile_speed": 805,
            "proj_dist_mult": 1.07
        },
        "upgrades": {
            "path_1": [
                {"name": "Long Range", "cost": 90, "original_range": 187.5, "fire_rate": 0},
                {"name": "Enhanced Eyesight", "cost": 160, "original_range": 225, "fire_rate": -100},
                {"name": "Spike-O-Pult", "cost": 500, "pierce": 40, "fire_rate": -600, "projectile": "spike", "projectile_speed": 450, "proj_dist_mult": 100},
                {"name": "Juggernaut", "cost": 1900, "pierce": 100, "fire_rate": 100, "weaknesses": "lead", "projectile_speed": 600},
            ],
            "path_2": [
                {"name": "Sharp Shots", "cost": 140, "pierce": 2},
                {"name": "Razor Sharp Shots", "cost": 170, "pierce": 5},
                {"name": "Triple Darts", "cost": 475, "pierce": 4, "proj_count": 3, "proj_angle": 30},
                {"name": "Super Monkey Fan Club", "cost": 8000, "pierce": 4},
            ]
        }
    }
}


SOUNDS = {
    "place": "18_PlaceTower.mp3",
    "frozenHit": "20_FrozenBloonHit.mp3",
    "leadHit": "23_MetalBloonHit.mp3",
    "pop4": "28_Pop4.mp3",
    "pop3": "29_Pop2.mp3",
    "pop2": "30_Pop3.mp3",
    "pop1": "31_Pop1.mp3",
    "cash": "59_ReceivedCash.mp3",
    "sell": "62_Sell.mp3",
    "upgrade": "70_Upgrade.mp3"
}