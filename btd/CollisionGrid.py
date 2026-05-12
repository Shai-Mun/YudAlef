class CollisionGrid:
    def __init__(self, cell_size=100):
        self.cell_size = cell_size
        self.grid = {}

    def clear(self):
        self.grid = {}

    def insert_bloon(self, bloon):
        # Calculate which cell the bloon is in
        gx = int(bloon.rect.centerx // self.cell_size)
        gy = int(bloon.rect.centery // self.cell_size)

        cell_coords = (gx, gy)
        if cell_coords not in self.grid:
            self.grid[cell_coords] = []
        self.grid[cell_coords].append(bloon)

    def get_nearby_bloons(self, projectile):
        # Find the cell the projectile is in
        gx = int(projectile.rect.centerx // self.cell_size)
        gy = int(projectile.rect.centery // self.cell_size)

        nearby = []
        # Check the projectile's cell AND the 8 surrounding cells
        # (in case a bloon is just over the line)
        for x in range(gx - 1, gx + 2):
            for y in range(gy - 1, gy + 2):
                if (x, y) in self.grid:
                    nearby.extend(self.grid[(x, y)])
        return nearby