# 火把袋貼圖來源

構圖草案以 Codex 內建 imagegen 產生，保存在 `originals/torch_bag_concept.png`。
遊戲實際使用的 `originals/torch_bag_16x16.png` 直接以 Minecraft 1.20.1
原版收納袋與火把的 16 × 16 像素為基礎重畫，因此色盤、硬邊與像素密度會和原版一致。
成品放在 `common/src/main/resources/assets/torch_bag/textures/item/`，飾品空格圖示使用同一張圖。

imagegen 草案提示：

> Create a single Minecraft Java Edition inventory item texture concept for a mod item named Torch Bag. Show a small tied brown leather bundle/pouch in the recognizable vanilla Minecraft item-sprite style, with one simple torch visibly sticking out of the opening. Exact straight-on inventory icon, centered, transparent background. Design for a logical 16 by 16 pixel canvas: chunky hard square pixels, crisp pixel clusters, one-pixel dark brown outline, extremely limited vanilla-like palette, flat shading, strong readable silhouette. No gradients, no glow halo, no smooth curves, no antialiasing, no painted detail, no 3D render, no text, no border, no UI, no drop shadow. The result should look like it belongs beside the vanilla bundle and torch icons in Minecraft 1.20/1.21.

沒有使用付費 API 或 CLI 圖像生成流程。
