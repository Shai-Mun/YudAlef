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
            "fire_rate": 940,
            "dmg": 1,
            "image": "dart_base.png",
            "projectile": "dart",
            "weaknesses": ["lead"],
            "projectile_speed": 805,
            "proj_dist_mult": 1.07,
            "proj_count": 1,
            "proj_angle": 0
        },
        "upgrades": {
            "path_1": [
                {"name": "Long Range", "cost": 90, "original_range": 187.5, "fire_rate": 0},
                {"name": "Enhanced Eyesight", "cost": 160, "original_range": 225},
                {"name": "Spike-O-Pult", "cost": 500, "pierce": 40, "fire_rate": -600, "projectile": "spike", "projectile_speed": 450, "proj_dist_mult": 100, "size": [80, 80]},
                {"name": "Juggernaut", "cost": 1900, "pierce": 100, "fire_rate": 100, "weaknesses": "lead", "projectile_speed": 600},
            ],
            "path_2": [
                {"name": "Quick Shots", "cost": 140, "fire_rate": 141},
                {"name": "Very Quick Shots", "cost": 170, "fire_rate": 280},
                {"name": "Triple Darts", "cost": 475, "pierce": 4, "proj_count": 3, "proj_angle": 30},
                {
                    "name": "Super Monkey Fan Club",
                    "cost": 8000,
                    "pierce": 4,
                    "ability": {"type": "super_monkey_fan_club", "cooldown": 45000, "duration": 10000}
                }
            ]
        }
    },

    "tack_shooter": {
        "image": 'Tack Shooter.png',
        "base": {
            "cost": 280,
            "original_range": 90,
            "pierce": 1,
            "fire_rate": 850,
            "dmg": 1,
            "image": "tack_base.png",
            "projectile": "tack",
            "weaknesses": ["lead"],
            "size": [80, 80],
            "projectile_speed": 700,
            "proj_dist_mult": 0.8,
            "proj_count": 8,
            "proj_angle": 45,
            "proj_size": (20, 10)
        },
        "upgrades": {
            "path_1": [
                {"name": "Faster Shooting", "cost": 150, "fire_rate": 150},
                {"name": "Even Faster Shooting", "cost": 225, "fire_rate": 200},
                {"name": "Tack Sprayer", "cost": 400, "proj_count": 16, "proj_angle": 22.5},
                {"name": "Ring of Fire", "cost": 2500, "pierce": 60, "projectile": "fire", "proj_count": 1, "weaknesses": "lead"}
            ],
            "path_2": [
                {"name": "Extra Range Tacks", "cost": 100, "original_range": 115},
                {"name": "Super Range Tacks", "cost": 225, "original_range": 140},
                {"name": "Blade Shooter", "cost": 680, "pierce": 2, "projectile": "blade", "projectile_speed": 850, "proj_dist_mult": 1.1, "proj_size": (30, 30)},
                # Added active ability config here
                {
                    "name": "Blade Maelstrom",
                    "cost": 2700,
                    "pierce": 5,
                    "fire_rate": 50,
                    "ability": {"type": "blade_maelstrom", "cooldown": 20000, "duration": 3000, "fire_rate": 60}
                }
            ]
        }
    },

    "sniper_monkey": {
        "image": 'Sniper Monkey.png',
        "base": {
            "cost": 350,
            "original_range": 3000,
            "pierce": 1,
            "fire_rate": 1930,
            "dmg": 1,
            "image": "sniper_base.png",
            "hitscan": True,
            "projectile": None,
            "weaknesses": ["lead"],
            "projectile_speed": 4000,
            "proj_dist_mult": 1.0,
            "proj_count": 1,
            "proj_angle": 0,
            "size": [100, 100]
        },
        "upgrades": {
            "path_1": [
                {"name": "Full Metal Jacket", "cost": 350, "weaknesses": "lead", "dmg": 4},
                {"name": "Point Five Oh", "cost": 400, "dmg": 7},
                {"name": "Deadly Precision", "cost": 1800, "dmg": 18},
                {"name": "Cripple MOAB", "cost": 5500, "dmg": 45, "proj_angle": 1}
            ],
            "path_2": [
                {"name": "Faster Firing", "cost": 400, "fire_rate": 570},
                {"name": "Night Vision Goggles", "cost": 400},
                {"name": "Semi-Automatic Rifle", "cost": 2750, "fire_rate": 1010},
                # Added cash yield ability config here
                {
                    "name": "Supply Drop",
                    "cost": 4200,
                    "ability": {"type": "supply_drop", "cooldown": 60000, "min_cash": 500, "max_cash": 1000} # 60000
                }
            ]
        }
    },

    "bomb_shooter": {
        "image": 'Bomb Shooter.png',
        "base": {
            "cost": 650,
            "original_range": 135,
            "pierce": 18,
            "fire_rate": 1500,
            "dmg": 1,
            "image": "bomb_base.png",
            "projectile": "bomb",
            "weaknesses": ["black", "zebra"],
            "projectile_speed": 450,
            "proj_dist_mult": 1.0,
            "proj_count": 1,
            "proj_angle": 0,
            "size": [70, 70]
        },
        "upgrades": {
            "path_1": [
                {"name": "Extra Range Bombs", "cost": 200, "original_range": 175},
                {"name": "Frag Bombs", "cost": 300, "weaknesses": "black", "projectile": "frag_bomb"},
                {"name": "Cluster Bombs", "cost": 800, "pierce": 50, "projectile": "cluster_bomb"},
                {"name": "Bloon Impact", "cost": 3200, "pierce": 100, "projectile": "impact_bomb"}
            ],
            "path_2": [
                {"name": "Bigger Bombs", "cost": 400, "pierce": 30},
                {"name": "Missile Launcher", "cost": 400, "fire_rate": 400, "projectile_speed": 900, "projectile": "missile", "original_range": 160},
                {"name": "MOAB Mauler", "cost": 900, "projectile": "mauler_missile", "pierce": 40},
                # Added targeted burst damage ability config here
                {
                    "name": "MOAB Assassin",
                    "cost": 3200,
                    "ability": {"type": "moab_assassin", "cooldown": 30000, "damage": 1000}
                }
            ]
        }
    }
}


SOUNDS = {
    "place": "18_PlaceTower.mp3",
    "frozenHit": "20_FrozenBloonHit.mp3",
    "leadHit": "23_MetalBloonHit.mp3",
    "ceramicHit": "27_CeramicBloonHit.mp3",
    "pop4": "28_Pop4.mp3",
    "pop3": "29_Pop2.mp3",
    "pop2": "30_Pop3.mp3",
    "pop1": "31_Pop1.mp3",
    "explosion": "32_ExplosionSmall.mp3",
    "cash": "59_ReceivedCash.mp3",
    "sell": "62_Sell.mp3",
    "upgrade": "70_Upgrade.mp3"
}

NATURAL_ROUNDS = {
    # --- EARLY GAME: Basic speed and volume ---
    1: [{"color": "red", "count": 20, "spacing": 1000}],
    2: [{"color": "red", "count": 30, "spacing": 800}],
    3: [{"color": "red", "count": 20, "spacing": 600}, {"color": "blue", "count": 5, "spacing": 1000}],
    4: [{"color": "red", "count": 30, "spacing": 500}, {"color": "blue", "count": 15, "spacing": 800}],
    5: [{"color": "blue", "count": 25, "spacing": 600}, {"color": "green", "count": 5, "spacing": 1200}],
    6: [{"color": "blue", "count": 20, "spacing": 400}, {"color": "green", "count": 15, "spacing": 800}],
    7: [{"color": "green", "count": 25, "spacing": 600}, {"color": "yellow", "count": 5, "spacing": 1000}],
    8: [{"color": "green", "count": 20, "spacing": 400}, {"color": "yellow", "count": 20, "spacing": 600}],
    9: [{"color": "yellow", "count": 30, "spacing": 500}],

    # --- MID GAME: Speedsters and Immunities ---
    10: [{"color": "yellow", "count": 20, "spacing": 400}, {"color": "pink", "count": 10, "spacing": 600}],
    11: [{"color": "pink", "count": 25, "spacing": 400}],
    12: [{"color": "pink", "count": 15, "spacing": 300}, {"color": "black", "count": 5, "spacing": 800}],
    13: [{"color": "black", "count": 10, "spacing": 600}, {"color": "white", "count": 10, "spacing": 600}],
    14: [{"color": "pink", "count": 30, "spacing": 200}, {"color": "black", "count": 15, "spacing": 500}],
    15: [{"color": "lead", "count": 10, "spacing": 1000}, {"color": "pink", "count": 20, "spacing": 300}],
    16: [{"color": "lead", "count": 15, "spacing": 800}, {"color": "zebra", "count": 10, "spacing": 600}],
    17: [{"color": "zebra", "count": 20, "spacing": 500}, {"color": "rainbow", "count": 5, "spacing": 1000}],
    18: [{"color": "rainbow", "count": 15, "spacing": 600}],
    19: [{"color": "lead", "count": 20, "spacing": 400}, {"color": "rainbow", "count": 20, "spacing": 500}],

    # --- LATE GAME: MOAB-Class and Ceramics ---
    20: [{"color": "moab", "count": 1, "spacing": 1000}],
    21: [{"color": "rainbow", "count": 30, "spacing": 300}, {"color": "ceramic", "count": 5, "spacing": 800}],
    22: [{"color": "ceramic", "count": 15, "spacing": 600}],
    23: [{"color": "moab", "count": 2, "spacing": 2000}, {"color": "ceramic", "count": 10, "spacing": 500}],
    24: [{"color": "ceramic", "count": 30, "spacing": 400}],
    25: [{"color": "moab", "count": 5, "spacing": 1000}],
    26: [{"color": "bfb", "count": 1, "spacing": 1000}],
    27: [{"color": "ceramic", "count": 50, "spacing": 200}, {"color": "moab", "count": 4, "spacing": 800}],
    28: [{"color": "bfb", "count": 2, "spacing": 2000}],
    29: [{"color": "ceramic", "count": 80, "spacing": 150}, {"color": "bfb", "count": 3, "spacing": 1500}],
    30: [{"color": "zomg", "count": 1, "spacing": 1000}, {"color": "moab", "count": 10, "spacing": 500}],
}