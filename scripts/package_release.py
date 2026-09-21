"""Collect already-built artifacts, verify their contents, and make a source archive."""
from pathlib import Path
import hashlib
import json
import shutil
import zipfile

ROOT = Path(__file__).resolve().parents[1]
DIST = ROOT / 'dist'
if DIST.exists(): shutil.rmtree(DIST)
DIST.mkdir()
hashes = []
for version in ['forge-1.20.1','neoforge-1.21.1']:
    src = ROOT / version / 'build/libs/torch_bag-0.6.0.jar'
    with zipfile.ZipFile(src) as jar:
        names = set(jar.namelist())
        assert 'dev/torchbag/TorchBagMod.class' in names
        assert 'dev/torchbag/TorchBombItem.class' in names
        assert 'dev/torchbag/BombPlacer.class' in names
        assert not any('BagGameTests' in n or 'ClientVisualTest' in n for n in names)
        assert not any(n.endswith('/empty.nbt') for n in names)
        assert 'data/torch_bag/curios/slots/belt.json' in names
        assert 'data/torch_bag/curios/slots/torch_bag.json' not in names
        belt_slot = json.loads(jar.read('data/torch_bag/curios/slots/belt.json'))
        assert belt_slot['size'] == 1 and belt_slot['operation'] == 'SET'
        assert 'assets/torch_bag/textures/item/leather_torch_bag.png' in names
        assert 'assets/torch_bag/textures/gui/gear_button.png' in names
        assert 'assets/torch_bag/lang/zh_cn.json' in names
        zh_tw = json.loads(jar.read('assets/torch_bag/lang/zh_tw.json'))
        zh_cn = json.loads(jar.read('assets/torch_bag/lang/zh_cn.json'))
        en_us = json.loads(jar.read('assets/torch_bag/lang/en_us.json'))
        assert '區塊' in zh_tw['tooltip.torch_bag.bomb_radius']
        assert '区块' in zh_cn['tooltip.torch_bag.bomb_radius']
        assert 'chunks' in en_us['tooltip.torch_bag.bomb_radius']
        for lang in [zh_tw, zh_cn, en_us]:
            assert 'tooltip.torch_bag.density' in lang
            assert 'screen.torch_bag.density' in lang
            for level in range(3):
                assert f'screen.torch_bag.density_{level}' in lang
        assert '2倍' in zh_tw['screen.torch_bag.density_1']
        assert '2.5倍' in zh_tw['screen.torch_bag.density_2']
        assert '2倍' in zh_cn['screen.torch_bag.density_1']
        assert '2.5倍' in zh_cn['screen.torch_bag.density_2']
        assert '2x' in en_us['screen.torch_bag.density_1']
        assert '2.5x' in en_us['screen.torch_bag.density_2']
        for key in ['bomb_progress', 'bomb_complete', 'bomb_busy', 'bomb_too_complex']:
            assert f'message.torch_bag.{key}' in zh_tw
        for bomb in ['torch_bomb_i', 'torch_bomb_ii', 'torch_bomb_iii']:
            assert f'assets/torch_bag/textures/item/{bomb}.png' in names
            assert f'assets/torch_bag/models/item/{bomb}.json' in names
        assert not any(tier + '_torch_bag' in name for name in names for tier in ['iron','gold','diamond'])
        for name in names:
            if name.endswith('.json'): json.loads(jar.read(name))
        modern = version.startswith('neo')
        tag_folder = 'item' if modern else 'items'
        assert f'data/curios/tags/{tag_folder}/belt.json' in names
        assert f'data/curios/tags/{tag_folder}/torch_bag.json' not in names
        recipe = f'data/torch_bag/{"recipe" if modern else "recipes"}/leather_torch_bag.json'
        assert json.loads(jar.read(recipe))['pattern'] == ['LTL','TCT','LPL']
        folder = 'recipe' if modern else 'recipes'
        first = json.loads(jar.read(f'data/torch_bag/{folder}/torch_bomb_i.json'))
        assert first['pattern'] == [' C ', 'CEC', ' C ']
        for level, previous in [('ii', 'i'), ('iii', 'ii')]:
            upgrade = json.loads(jar.read(f'data/torch_bag/{folder}/torch_bomb_{level}.json'))
            assert len(upgrade['ingredients']) == 2
            assert all(x['item'] == f'torch_bag:torch_bomb_{previous}' for x in upgrade['ingredients'])
    target = DIST / f'torch_bag-0.6.0-{version}.jar'
    shutil.copyfile(src,target)
    hashes.append(hashlib.sha256(target.read_bytes()).hexdigest()+'  '+target.name)
    evidence = ROOT / 'verification' / version
    evidence.mkdir(parents=True,exist_ok=True)
    for image in (ROOT/version/'run/screenshots').glob('torch-bag*.png'):
        shutil.copyfile(image,evidence/image.name)
    for mode in ['full','none','curios','backpacks']:
        text=(ROOT/version/f'build/gametest-{mode}.log').read_text(encoding='utf-8',errors='replace')
        assert 'All 10 required tests passed' in text, (version,mode)
        assert 'BUILD SUCCESSFUL' in text, (version,mode)
        # Keep concise evidence rather than platform debug logs and machine paths.
        lines=[line for line in text.splitlines() if any(key in line for key in ['GAME TESTS COMPLETE','All 10 required','BUILD SUCCESSFUL'])]
        (evidence/f'gametest-{mode}.txt').write_text('\n'.join(lines)+'\n',encoding='utf-8')

for name in ['README.md','TESTING.md']:
    shutil.copyfile(ROOT/name,DIST/name)

archive = DIST / 'torch_bag-0.6.0-source.zip'
excluded = {'build','.gradle','run','runs','.reference','.tmp','dist','.git','artwork-python','mdk-downloads','__pycache__'}
with zipfile.ZipFile(archive,'w',zipfile.ZIP_DEFLATED) as z:
    for path in ROOT.rglob('*'):
        relative=path.relative_to(ROOT)
        if path.is_file() and not any(part in excluded for part in relative.parts):
            z.write(path,relative.as_posix())
hashes.append(hashlib.sha256(archive.read_bytes()).hexdigest()+'  '+archive.name)
(DIST/'SHA256SUMS.txt').write_text('\n'.join(hashes)+'\n',encoding='utf-8')
for path in DIST.iterdir(): print(path.name,path.stat().st_size)
