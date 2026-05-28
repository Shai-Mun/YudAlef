BLOON_CONFIG = {
    "bloon_0": {"round": 2, "color": "red", "count": 8, "load_time": 800, "cost": 25, "eco": 1},  # grouped
    "bloon_1": {"round": 2, "color": "blue", "count": 6, "load_time": 1000, "cost": 25, "eco": 1},
    "bloon_2": {"round": 4, "color": "blue", "count": 6, "load_time": 600, "cost": 42, "eco": 1.7},  # grouped
    "bloon_3": {"round": 4, "color": "pink", "count": 3, "load_time": 1000, "cost": 42, "eco": 1.7},
    "bloon_4": {"round": 6, "color": "green", "count": 5, "load_time": 500, "cost": 60, "eco": 2.4},
    "bloon_5": {"round": 6, "color": "black", "count": 3, "load_time": 1000, "cost": 60, "eco": 2.4},
    "bloon_6": {"round": 8, "color": "yellow", "count": 5, "load_time": 250, "cost": 75, "eco": 3},
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
            "projectile": "dart"
        },
        "upgrades": {
            "path_1": [
                {"name": "Long Range", "cost": 90, "original_range": 187.5, "fire_rate": 0},
                {"name": "Enhanced Eyesight", "cost": 160, "original_range": 225, "fire_rate": -100},
                {"name": "Spike-O-Pult", "cost": 500, "pierce": 40, "fire_rate": -600},
                {"name": "Juggernaut", "cost": 1900, "pierce": 100, "fire_rate": 100},
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