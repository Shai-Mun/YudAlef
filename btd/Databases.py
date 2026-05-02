BLOON_CONFIG = {
    "bloon_0": {"color": "red", "count": 8, "load_time": 800},  # grouped
    "bloon_1": {"color": "blue", "count": 6, "load_time": 1000},
    "bloon_2": {"color": "blue", "count": 6, "load_time": 600},  # grouped
    "bloon_3": {"color": "pink", "count": 3, "load_time": 1000},
    "bloon_4": {"color": "green", "count": 5, "load_time": 500},
    "bloon_5": {"color": "black", "count": 3, "load_time": 1000},
    "bloon_6": {"color": "yellow", "count": 5, "load_time": 250},
}


MONKEY_DATA = {
    "dart_monkey": {
        "image": 'Dart Monkey.png',
        "base": {
            "cost": 200,
            "range": 150,
            "pierce": 1,
            "fire_rate": 940,  # ms
            "image": "dart_base.png",
            "projectile": "dart"
        },
        "upgrades": {
            "path_1": [
                {"name": "Long Range", "cost": 90, "range": 187.5, "fire_rate": 0},
                {"name": "Enhanced Eyesight", "cost": 160, "range": 225, "fire_rate": -100},
                {"name": "Spike-O-Pult", "cost": 500, "pierce": 40, "fire_rate": -600},
                {"name": "Juggernaut", "cost": 1900, "pierce": 100, "fire_rate": 100},
            ],
            "path_2": [
                {"name": "Sharp Shots", "cost": 140, "pierce": 2},
                {"name": "Razor Sharp Shots", "cost": 170, "pierce": 5},
                {"name": "Triple Darts", "cost": 475, "pierce": 4},
                {"name": "Super Monkey Fan Club", "cost": 8000, "pierce": 4},
            ]
        }
    }
}