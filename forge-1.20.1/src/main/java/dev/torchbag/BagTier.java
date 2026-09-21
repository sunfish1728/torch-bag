package dev.torchbag;

public enum BagTier {
    LEATHER("leather", 6, 16);
    public final String id;
    public final int rows, radius;
    BagTier(String id, int rows, int radius) { this.id = id; this.rows = rows; this.radius = radius; }
    public int slots() { return rows * 9; }
    public static BagTier of(int index) { return LEATHER; }
}
