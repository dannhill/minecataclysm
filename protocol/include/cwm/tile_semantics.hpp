#pragma once
#include <cstdint>

namespace cdda::cwm {
// Semantic state, independent of the presentation engine. Material describes
// terrain; furniture overlays it instead of replacing the underlying floor.
enum TileState : uint32_t {
    DOOR = 1u << 0,
    BLOCKS_MOVEMENT = 1u << 1,
    FURNITURE = 1u << 2,
    TALL_FURNITURE = 1u << 3,
};
// Presentation cues from the native avatar state; they never change coordinates
// or grant passage/swimming abilities in the presentation runtime.
enum ActorState : uint32_t {
    WINDOW_PASSAGE = 1u << 0,
    WADING = 1u << 1,
    SWIMMING = 1u << 2,
    UNDERWATER = 1u << 3,
};
enum Material : uint16_t {
    AIR = 0, DIRT = 1, GRASS = 2, WALL = 3, FLOOR = 4,
    DOOR_CLOSED = 5, DOOR_OPEN = 6, WINDOW = 7, PAVEMENT = 8,
    LEGACY_FURNITURE = 9, WINDOW_OPEN = 10, WINDOW_BOARDED = 11,
    OBSTACLE = 12, GLASS_WALL = 13, WATER = 14, LOW_OBSTACLE = 15,
    SAND = 16, SHRUB = 17, TREE = 18, SIDEWALK = 19, TALL_GRASS = 20,
};
// orientation 0: opening in an east-west wall; 1: north-south wall.
}
