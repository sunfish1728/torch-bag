from pathlib import Path
import json

ROOT = Path(__file__).resolve().parents[1]
COMMON = ROOT / 'common/src/main/resources'
def save(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')

tiers = ['leather']
bombs = ['torch_bomb_i', 'torch_bomb_ii', 'torch_bomb_iii']
zh = {
    'item.torch_bag.leather_torch_bag': '火把袋',
    'item.torch_bag.torch_bomb_i': '火把爆彈(I)',
    'item.torch_bag.torch_bomb_ii': '火把爆彈(II)',
    'item.torch_bag.torch_bomb_iii': '火把爆彈(III)',
}
zh.update({
    'tooltip.torch_bag.capacity': '容量：%s 格　補光半徑：%s 格',
    'tooltip.torch_bag.density': '光源密度：%s',
    'tooltip.torch_bag.usage': '手持或裝備在腰帶欄位，自動補光',
    'tooltip.torch_bag.curios': '右鍵開啟；已穿戴時使用「開啟火把袋」按鍵',
    'screen.torch_bag.status': '%s / %s 支　半徑 %s 格',
    'screen.torch_bag.settings': '設定',
    'screen.torch_bag.radius': '補光半徑',
    'screen.torch_bag.radius_value': '%s 格',
    'screen.torch_bag.density': '光源密度',
    'screen.torch_bag.density_0': '低',
    'screen.torch_bag.density_1': '中（2倍）',
    'screen.torch_bag.density_2': '高（2.5倍）',
    'key.torch_bag.open': '開啟已裝備的火把袋',
    'key.categories.torch_bag': '火把袋',
    'tooltip.torch_bag.bomb_radius': '放置半徑：%s 個區塊',
    'tooltip.torch_bag.bomb_usage': '右鍵消耗，逐區塊向外補光',
    'message.torch_bag.bomb_started': '火把爆彈已啟動',
    'message.torch_bag.bomb_busy': '上一顆火把爆彈尚未完成：%s%%',
    'message.torch_bag.bomb_server_busy': '目前同時運行的火把爆彈太多',
    'message.torch_bag.bomb_progress': '火把放置進度：%s%%',
    'message.torch_bag.bomb_complete': '火把爆彈完成：100%',
    'message.torch_bag.bomb_too_complex': '地形過於複雜，爆彈已停止；已放置的火把會保留。',
})
en = {
    'item.torch_bag.leather_torch_bag': 'Torch Bag',
    'item.torch_bag.torch_bomb_i': 'Torch Bomb (I)',
    'item.torch_bag.torch_bomb_ii': 'Torch Bomb (II)',
    'item.torch_bag.torch_bomb_iii': 'Torch Bomb (III)',
}
en.update({
    'tooltip.torch_bag.capacity': '%s slots | Radius: %s blocks',
    'tooltip.torch_bag.density': 'Light density: %s',
    'tooltip.torch_bag.usage': 'Hold or equip in a Belt slot to light dark areas',
    'tooltip.torch_bag.curios': 'Right-click to open; use Open Torch Bag when equipped',
    'screen.torch_bag.status': '%s / %s | Radius %s',
    'screen.torch_bag.settings': 'Settings',
    'screen.torch_bag.radius': 'Light radius',
    'screen.torch_bag.radius_value': '%s blocks',
    'screen.torch_bag.density': 'Light density',
    'screen.torch_bag.density_0': 'Low',
    'screen.torch_bag.density_1': 'Medium (2x)',
    'screen.torch_bag.density_2': 'High (2.5x)',
    'key.torch_bag.open': 'Open Equipped Torch Bag',
    'key.categories.torch_bag': 'Torch Bag',
    'tooltip.torch_bag.bomb_radius': 'Placement radius: %s chunks',
    'tooltip.torch_bag.bomb_usage': 'Right-click to consume and light chunks outward',
    'message.torch_bag.bomb_started': 'Torch Bomb started',
    'message.torch_bag.bomb_busy': 'Your previous Torch Bomb is still running: %s%%',
    'message.torch_bag.bomb_server_busy': 'Too many Torch Bombs are running',
    'message.torch_bag.bomb_progress': 'Torch placement progress: %s%%',
    'message.torch_bag.bomb_complete': 'Torch Bomb complete: 100%',
    'message.torch_bag.bomb_too_complex': 'The terrain is too complex, so the Torch Bomb stopped. Placed torches remain.',
})
save(COMMON / 'assets/torch_bag/lang/zh_tw.json', zh)
save(COMMON / 'assets/torch_bag/lang/en_us.json', en)
zh_cn = {
    'item.torch_bag.leather_torch_bag': '火把袋',
    'item.torch_bag.torch_bomb_i': '火把爆弹(I)',
    'item.torch_bag.torch_bomb_ii': '火把爆弹(II)',
    'item.torch_bag.torch_bomb_iii': '火把爆弹(III)',
    'tooltip.torch_bag.capacity': '容量：%s 格　照明半径：%s 格',
    'tooltip.torch_bag.density': '光源密度：%s',
    'tooltip.torch_bag.usage': '手持或装备在腰带栏位，自动补充照明',
    'tooltip.torch_bag.curios': '右键打开；已装备时使用“打开火把袋”按键',
    'screen.torch_bag.status': '%s / %s 支　半径 %s 格',
    'screen.torch_bag.settings': '设置',
    'screen.torch_bag.radius': '照明半径',
    'screen.torch_bag.radius_value': '%s 格',
    'screen.torch_bag.density': '光源密度',
    'screen.torch_bag.density_0': '低',
    'screen.torch_bag.density_1': '中（2倍）',
    'screen.torch_bag.density_2': '高（2.5倍）',
    'key.torch_bag.open': '打开已装备的火把袋',
    'key.categories.torch_bag': '火把袋',
    'tooltip.torch_bag.bomb_radius': '放置半径：%s 个区块',
    'tooltip.torch_bag.bomb_usage': '右键消耗，逐区块向外补充照明',
    'message.torch_bag.bomb_started': '火把爆弹已启动',
    'message.torch_bag.bomb_busy': '上一颗火把爆弹尚未完成：%s%%',
    'message.torch_bag.bomb_server_busy': '目前同时运行的火把爆弹过多',
    'message.torch_bag.bomb_progress': '火把放置进度：%s%%',
    'message.torch_bag.bomb_complete': '火把爆弹完成：100%',
    'message.torch_bag.bomb_too_complex': '地形过于复杂，爆弹已停止；已经放置的火把会保留。',
}
save(COMMON / 'assets/torch_bag/lang/zh_cn.json', zh_cn)
for tier in tiers:
    save(COMMON / f'assets/torch_bag/models/item/{tier}_torch_bag.json', {
        'parent': 'minecraft:item/generated', 'textures': {'layer0': f'torch_bag:item/{tier}_torch_bag'}})
for bomb in bombs:
    save(COMMON / f'assets/torch_bag/models/item/{bomb}.json', {
        'parent': 'minecraft:item/generated', 'textures': {'layer0': f'torch_bag:item/{bomb}'}})
save(COMMON / 'data/torch_bag/curios/slots/belt.json', {
    'size': 1, 'operation': 'SET', 'order': 180, 'icon': 'curios:slot/empty_belt_slot',
    'add_cosmetic': False, 'use_native_gui': True, 'render_toggle': False, 'validators': ['curios:tag']})
save(COMMON / 'data/torch_bag/curios/entities/player.json', {'entities': ['minecraft:player'], 'slots': ['belt']})
(COMMON / 'data/torch_bag/curios/slots/torch_bag.json').unlink(missing_ok=True)
(COMMON / 'assets/minecraft/atlases/blocks.json').unlink(missing_ok=True)
(COMMON / 'assets/torch_bag/textures/slot/torch_bag.png').unlink(missing_ok=True)

for version in ['forge-1.20.1', 'neoforge-1.21.1']:
    modern = version.startswith('neoforge')
    res = ROOT / version / 'src/main/resources'
    recipes = 'recipe' if modern else 'recipes'
    tags = 'item' if modern else 'items'
    save(res / f'data/curios/tags/{tags}/belt.json', {'replace': False, 'values': [f'torch_bag:{tier}_torch_bag' for tier in tiers]})
    (res / f'data/curios/tags/{tags}/torch_bag.json').unlink(missing_ok=True)
    save(res / f'data/torch_bag/{recipes}/leather_torch_bag.json', {
        'type': 'minecraft:crafting_shaped', 'category': 'equipment',
        'pattern': ['LTL', 'TCT', 'LPL'],
        'key': {'L': {'item': 'minecraft:leather'}, 'T': {'item': 'minecraft:torch'}, 'C': {'item': 'minecraft:chest'}, 'P': {'item': 'minecraft:ender_pearl'}},
        'result': {'id' if modern else 'item': 'torch_bag:leather_torch_bag', 'count': 1}})
    save(res / f'data/torch_bag/{recipes}/torch_bomb_i.json', {
        'type': 'minecraft:crafting_shaped', 'category': 'equipment',
        'pattern': [' C ', 'CEC', ' C '],
        'key': {'C': {'item': 'minecraft:coal_block'}, 'E': {'item': 'minecraft:ender_eye'}},
        'result': {'id' if modern else 'item': 'torch_bag:torch_bomb_i', 'count': 1}})
    for level, previous in [('ii', 'i'), ('iii', 'ii')]:
        save(res / f'data/torch_bag/{recipes}/torch_bomb_{level}.json', {
            'type': 'minecraft:crafting_shapeless', 'category': 'equipment',
            'ingredients': [{'item': f'torch_bag:torch_bomb_{previous}'}, {'item': f'torch_bag:torch_bomb_{previous}'}],
            'result': {'id' if modern else 'item': f'torch_bag:torch_bomb_{level}', 'count': 1}})
    advancement = 'advancement' if modern else 'advancements'
    save(res / f'data/torch_bag/{advancement}/recipes/leather_torch_bag.json', {
        'parent': 'minecraft:recipes/root',
        'criteria': {
            'has_torch': {'trigger': 'minecraft:inventory_changed', 'conditions': {'items': [{'items': ['minecraft:torch']}] }},
            'has_recipe': {'trigger': 'minecraft:recipe_unlocked', 'conditions': {'recipe': 'torch_bag:leather_torch_bag'}}},
        'requirements': [['has_torch', 'has_recipe']],
        'rewards': {'recipes': ['torch_bag:leather_torch_bag']}})
