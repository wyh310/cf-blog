#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
把图片自动压缩后放进仓库的 source/images/uploads/，并打印可直接粘进 Markdown 的链接。

不用你判断是照片还是截图：每张图同时压两版 —— WebP 有损(quality=80) 和 WebP 无损 ——
谁的文件更小就用谁。照片通常「有损」小得多；截图 / 文字 / 表格 / 图标通常「无损」又小又清晰。
原图永远不改动，只把结果写进 uploads/；已压过的 .webp、动图、SVG 原样复制，不会反复压。

用法（在任意目录执行都可以，脚本会自己找到仓库）：
  python3 tools/add_images.py 照片.jpg
  python3 tools/add_images.py ./photos/            # 整个目录
  python3 tools/add_images.py *.png
  python3 tools/add_images.py --no-resize 手机原图.jpg
  python3 tools/add_images.py --dry-run ./photos/  # 只看效果、不写文件

常用参数：
  --no-resize     不缩小大图（默认超过 1600 宽的图等比缩到 1600，只缩不放）
  --max-width N   最大宽度，默认 1600
  --quality N     有损质量，默认 80
  --force         覆盖已存在的同名结果（默认跳过，避免把同一张图压了一遍又一遍）
  --no-compress   不压缩，只复制
  --dry-run       预览，不写文件

依赖（可选）：pip3 install Pillow   （Windows 用 pip install Pillow）
没装也能用，只是原样复制、不压缩，并会打印安装提示。
"""
import argparse
import io
import re
import shutil
import sys
from pathlib import Path

try:
    from PIL import Image, ImageOps
    HAS_PIL = True
except ImportError:
    HAS_PIL = False

try:
    sys.stdout.reconfigure(errors="replace")
except Exception:
    pass

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "source" / "images" / "uploads"
EXTS = {".png", ".jpg", ".jpeg", ".webp", ".gif", ".svg",
        ".avif", ".bmp", ".tif", ".tiff", ".heic", ".heif"}
# 这些格式一律原样复制、不压缩；理由会打印出来让用户看明白
SKIP_REASON = {
    ".svg": "SVG 矢量图，本身就不大，不需要压缩",
    ".webp": "已是 WebP，跳过（避免反复压、画质再降）",
    ".gif": "GIF 一律原样复制，避免丢动画",
}
ADMIN_LIMIT = 2 * 1024 * 1024          # 与 source/admin/config.yml 的 max_file_size 一致


class Skip(Exception):
    """这张图不压缩，原样复制。"""


def kb(n):
    if n < 1024:
        return f"{n} B"
    if n < 1024 * 1024:
        return f"{n / 1024:.1f} KB"
    return f"{n / 1024 / 1024:.1f} MB"


def collect(paths):
    found, seen = [], set()
    for raw in paths:
        p = Path(raw)
        if p.is_dir():
            for f in sorted(p.iterdir()):
                if f.is_file() and f.suffix.lower() in EXTS and not f.name.startswith("."):
                    found.append(f)
        elif p.is_file():
            found.append(p)
        else:
            print(f"  跳过（不存在）: {raw}")
    uniq = []
    for f in found:
        key = str(f.resolve())
        if key not in seen:
            seen.add(key)
            uniq.append(f)
    return uniq


def safe_name(f):
    """空白换成短横线，避免 Markdown 链接被空格截断；中文文件名保留。"""
    return re.sub(r"\s+", "-", f.stem) + f.suffix.lower()


def make_webp(f, args):
    """返回 (字节, 信息字典)；不适合压缩时抛 Skip。"""
    if not HAS_PIL:
        raise Skip("未安装 Pillow")
    try:
        im = Image.open(f)
    except Exception as e:
        raise Skip(f"Pillow 打不开这个格式（{type(e).__name__}），原样复制")
    if getattr(im, "n_frames", 1) > 1:
        raise Skip("动图，原样复制以保留动画")

    has_alpha = im.mode in ("RGBA", "LA", "PA") or \
        (im.mode == "P" and "transparency" in im.info)
    im = ImageOps.exif_transpose(im)          # 修正手机照片的旋转方向
    im = im.convert("RGBA" if has_alpha else "RGB")
    ow, oh = im.size
    nw, nh = ow, oh
    if not args.no_resize and ow > args.max_width:
        nh = max(1, round(oh * args.max_width / ow))
        nw = args.max_width
        im = im.resize((nw, nh), Image.LANCZOS)

    def enc(**kw):
        buf = io.BytesIO()
        im.save(buf, "WEBP", method=4, **kw)
        return buf.getvalue()

    lossy = enc(quality=args.quality)
    lossless = enc(lossless=True)
    if len(lossless) < len(lossy):          # 相等时选无损，画质优先
        data, picked = lossless, "无损"
    else:
        data, picked = lossy, "有损"

    info = {
        "lossy": len(lossy), "lossless": len(lossless), "picked": picked,
        "ow": ow, "oh": oh, "nw": nw, "nh": nh,
        "resized": (nw != ow or nh != oh),
    }
    return data, info


def process(f, args):
    src_size = f.stat().st_size
    name = safe_name(f)
    stem = Path(name).stem
    ext = f.suffix.lower()
    data, info, reason = None, None, ""

    if ext in SKIP_REASON:
        reason = SKIP_REASON[ext]
    elif args.no_compress:
        reason = "指定了 --no-compress"
    else:
        try:
            data, info = make_webp(f, args)
            if len(data) >= src_size:
                raise Skip("压缩后反而更大，保留原图更划算")
        except Skip as e:
            data, info, reason = None, None, str(e)

    dst_name = stem + ".webp" if data is not None else name
    dst = OUT / dst_name
    link = f"![{stem}](/images/uploads/{dst_name})"

    print(f"  {f.name}")
    if data is None:
        print(f"    → {dst_name}   {kb(src_size)}   原样复制（{reason}）")
    else:
        pct = round(100 * (1 - len(data) / src_size))
        print(f"    → {dst_name}   {kb(src_size)} → {kb(len(data))}   省 {pct}%")
        print(f"      两版对比：有损 q{args.quality} {kb(info['lossy'])} / "
              f"无损 {kb(info['lossless'])} → 选「{info['picked']}」")
        if info["resized"]:
            print(f"      尺寸 {info['ow']}×{info['oh']} → {info['nw']}×{info['nh']}"
                  f"（超过 {args.max_width} 宽等比缩小，只缩不放）")
        else:
            print(f"      尺寸 {info['ow']}×{info['oh']}（未缩小）")

    action = "preview"
    if dst.resolve() == f.resolve():
        print("    （图片已经在 uploads/ 里，无需处理）")
        action = "same"
    elif dst.exists() and not args.force:
        print(f"    （{dst_name} 已存在，跳过、未覆盖；要重压加 --force）")
        action = "skipped"
    elif not args.dry_run:
        OUT.mkdir(parents=True, exist_ok=True)
        if data is None:
            shutil.copyfile(f, dst)
            action = "copied"
        else:
            dst.write_bytes(data)
            action = "compressed"
    print(f"    {link}")
    print()

    final_size = len(data) if data is not None else src_size
    return {
        "before": src_size, "after": final_size,
        "action": action,
        "will_compress": data is not None and action not in ("skipped", "same"),
        "too_big": final_size > ADMIN_LIMIT,
    }


def main():
    ap = argparse.ArgumentParser(
        description="把图片自动压缩后放进 source/images/uploads/，并打印 Markdown 链接")
    ap.add_argument("paths", nargs="+", help="图片文件或目录，可写多个")
    ap.add_argument("--quality", type=int, default=80, help="有损质量，默认 80")
    ap.add_argument("--max-width", type=int, default=1600, help="最大宽度，默认 1600")
    ap.add_argument("--no-resize", action="store_true", help="不缩小大图")
    ap.add_argument("--no-compress", action="store_true", help="不压缩，只复制")
    ap.add_argument("--force", action="store_true", help="覆盖已存在的同名结果")
    ap.add_argument("--dry-run", action="store_true", help="预览，不写文件")
    args = ap.parse_args()

    files = collect(args.paths)
    if not files:
        print("没有找到图片文件。")
        return 1

    print("图片自动压缩：每张图同时压「有损 q%d」和「无损」两版，谁小用谁" % args.quality)
    print("  → 照片通常选有损；截图 / 文字 / 表格 / 图标通常选无损（画质一点不丢）")
    if not HAS_PIL:
        print("  → 当前未安装 Pillow，本次只复制不压缩。装一次即可自动压缩：")
        print("     pip3 install Pillow        （Windows：pip install Pillow）")
    if args.dry_run:
        print("  → 预览模式，不会写入任何文件")
    print(f"  输出目录：{OUT}")
    print()

    results = [process(f, args) for f in files]
    comp = [r for r in results if r["action"] == "compressed"]
    wrote = [r for r in results if r["action"] in ("compressed", "copied")]
    skipped = [r for r in results if r["action"] == "skipped"]
    saved = sum(r["before"] - r["after"] for r in comp)
    if args.dry_run:
        will = sum(1 for r in results if r["will_compress"])
        print(f"预览完成：{len(files)} 张，其中 {will} 张会被压缩；未写入任何文件。"
              f"去掉 --dry-run 即实际执行。")
    elif not wrote:
        print(f"没有改动任何文件：{len(skipped)} 张结果都已存在。要重压加 --force。")
    else:
        print(f"完成：写入 {len(wrote)} 张（压缩 {len(comp)} 张，共省 {kb(max(saved, 0))}），"
              f"{len(skipped)} 张已存在被跳过。原图未改动。")
    big = [f for f, r in zip(files, results) if r["too_big"]]
    if big:
        hint = ("先装 Pillow：pip3 install Pillow" if not HAS_PIL
                else "去掉 --no-compress 让脚本自动压缩，或加 --quality 70")
        print(f"注意：{len(big)} 张结果超过后台单张 2 MB 上限（{', '.join(x.name for x in big)}），"
              f"后台上传会被拒。{hint}。")
    print("把上面的链接粘进 md，或直接在后台插图。")
    if wrote:
        print("别忘了提交：git add -A && git commit -m '加图' && git push")
    return 0


if __name__ == "__main__":
    sys.exit(main())
