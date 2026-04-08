MONKEY_DATA = {
    "dart_monkey": {
        "base": {
            "cost": 200,
            "range": 150,
            "fire_rate": 800,  # ms
            "image": "dart_base.png",
            "projectile": "dart"
        },
        "upgrades": {
            "path_1": [
                {"name": "Long Range", "cost": 90, "range": 50, "fire_rate": 0},
                {"name": "Enhanced Eyesight", "cost": 160, "range": 60, "fire_rate": -100},
                {"name": "Spike-O-Pult", "cost": 500, "pierce": 40, "fire_rate": -600},
                {"name": "Juggernaut", "cost": 1500, "pierce": 100, "fire_rate": 100},
            ],
            "path_2": [
                {"name": "Sharp Shots", "cost": 140, "pierce": 2},
                {"name": "Razor Sharp Shots", "cost": 170, "pierce": 4},
                {"name": "Triple Darts", "cost": 340, "pierce": 4},
                {"name": "Super Monkey Fan Club", "cost": 7500, "pierce": 4},
            ]
        }
    }
}