#!/usr/bin/env bash
# 把图片【自动压缩】后放进仓库的 source/images/uploads/，并打印可直接粘进 Markdown 的链接。
# 图片随 git push 一起发布，不需要 R2、不需要绑卡、不需要任何密钥。
#
# 压缩规则不用你操心：每张图同时压「有损 q80」和「无损」两版，谁小用谁。
#   照片 → 自动有损；截图 / 文字 / 表格 / 图标 → 自动无损（又小又清晰）。
# 原图不会改动；已是 .webp、动图、SVG 原样复制，不会反复压。
#
# 用法（在任意目录执行都可以）：
#   bash tools/add-images.sh 照片.jpg
#   bash tools/add-images.sh ./photos/                 # 整个目录
#   bash tools/add-images.sh *.png
#   bash tools/add-images.sh --no-resize 手机原图.jpg  # 只压缩、不缩小尺寸
#   python3 tools/add_images.py --dry-run ./photos/    # Windows 可直接这样跑
#
# 依赖（可选，装一次即可）：pip3 install Pillow   （Windows：pip install Pillow）
# 没装也能用，只是原样复制、不压缩。
#
# 执行完记得提交：git add -A && git commit -m "加图" && git push
set -euo pipefail

HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

PY=""
for c in python3 python; do
  if command -v "$c" >/dev/null 2>&1; then PY="$c"; break; fi
done

if [ -n "$PY" ]; then
  exec "$PY" "$HERE/add_images.py" "$@"
fi

# 没有 Python：降级为「原样复制」，不阻断流程
echo "提示：本机没有 Python 3，本次只复制不压缩。装 Python 3 + Pillow 后即可自动压缩。"
echo "      pip3 install Pillow   （Windows：pip install Pillow）"
DIR="$HERE/../source/images/uploads"
mkdir -p "$DIR"
if [ "$#" -eq 0 ]; then
  echo "用法: bash tools/add-images.sh <图片文件或目录> [更多...]"
  exit 1
fi
count=0
for f in "$@"; do
  if [ -d "$f" ]; then
    while IFS= read -r -d '' one; do
      name="$(basename "$one")"; safe="$(printf '%s' "$name" | tr ' ' '-')"
      cp -f "$one" "$DIR/$safe"; echo "![${safe%.*}](/images/uploads/$safe)"
      count=$((count + 1))
    done < <(find "$f" -maxdepth 1 -type f \
      \( -iname '*.png' -o -iname '*.jpg' -o -iname '*.jpeg' -o -iname '*.webp' \
         -o -iname '*.gif' -o -iname '*.svg' -o -iname '*.avif' \) -print0)
  elif [ -f "$f" ]; then
    name="$(basename "$f")"; safe="$(printf '%s' "$name" | tr ' ' '-')"
    cp -f "$f" "$DIR/$safe"; echo "![${safe%.*}](/images/uploads/$safe)"
    count=$((count + 1))
  else
    echo "跳过（不存在）: $f" >&2
  fi
done
echo "完成，共 $count 张。把上面的链接粘进 md，或直接在后台插图。"
echo "别忘了提交：git add -A && git commit -m '加图' && git push"
