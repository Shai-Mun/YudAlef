class CollisionGrid:
    def __init__(self, cell_size=100):
        # Defines uniform grid cell dimensions for spatial partitioning
        self.cell_size = cell_size
        self.grid = {}

    def clear(self):
        # Flushes all spatial entries to rebuild the grid from scratch every frame
        self.grid = {}

    def insert_bloon(self, bloon):
        # Maps the absolute screen coordinates of a bloon to discrete grid indices
        gx = int(bloon.rect.centerx // self.cell_size)
        gy = int(bloon.rect.centery // self.cell_size)
        cell_coords = (gx, gy)

        # Groups entities tracking position collisions together by cell coordinates
        if cell_coords not in self.grid:
            self.grid[cell_coords] = []
        self.grid[cell_coords].append(bloon)

    def get_nearby_bloons(self, projectile):
        # Maps the projectile's pixel position to its corresponding grid cell
        gx = int(projectile.rect.centerx // self.cell_size)
        gy = int(projectile.rect.centery // self.cell_size)

        nearby = []
        # Evaluates the host cell and the adjacent 8 neighboring cells to handle boundary crossings
        for x in range(gx - 1, gx + 2):
            for y in range(gy - 1, gy + 2):
                if (x, y) in self.grid:
                    nearby.extend(self.grid[(x, y)])
        return nearby