package dev.torchbag;

public enum BombTier {
    I("torch_bomb_i", 4), II("torch_bomb_ii", 8), III("torch_bomb_iii", 16);
    public final String id;
    public final int chunkRadius;
    BombTier(String id, int chunkRadius) { this.id = id; this.chunkRadius = chunkRadius; }
}
