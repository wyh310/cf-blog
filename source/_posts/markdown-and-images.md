---
title: 用 Markdown 写文章和传图片
date: 2026-11-10 09:30:00
tags:
  - 教程
categories:
  - 使用说明
cover: /images/cover.svg
---

这个博客的文章就是一个个 `.md` 文件，支持标准 Markdown 语法。

## 常用语法

**加粗**、*斜体*、`行内代码`、[链接](https://example.com)、引用：

> 这是一段引用。

- 列表项一
- 列表项二

| 项目 | 说明 |
| --- | --- |
| 标题 | front-matter 里的 `title` |
| 日期 | front-matter 里的 `date` |

围栏代码块自带右上角一键复制按钮：

```bash
cd cf-blog
npm install
npm run build
```

## 怎么放图片

正文图片放在仓库的 `source/images/uploads/`，跟文章一起提交、一起由 Cloudflare Pages 分发。**不用绑卡、不用密钥、不用图片域名**，文章里写相对路径即可：

```markdown
![图片说明](/images/uploads/demo.png)
```

三种放图方式：

- **在线后台**（最省事）：写一段 → 把图拖进正文 / 粘贴 → 图片**当场自动压成 WebP**、提交进仓库、链接自动插入，接着写下一段。不用先压图，手机也一样。
- **GitHub 网页**：在 `source/images/uploads/` 里 `Add file → Upload files` 把图传上去，再在文章里写上面那行链接。这条路径不经过后台压缩，传之前最好自己压一下。
- **批量 / 想要无损**：本地执行 `bash tools/add-images.sh ./photos/`，脚本会压缩图片（截图能选像素级无损）并打印可直接粘贴的链接，提交即可。

> 图片和文章在同一个仓库：删了图，文章就会破图。用后台写时图片已自动压好；走 GitHub 网页 / 命令行传大图，先用 <https://squoosh.app> 或脚本压成 WebP。仓库建议保持在 1 GB 以内。

仓库的 `source/images/cover.svg` 是默认封面，也可以这样引用：

```markdown
![示例封面](/images/cover.svg)
```

![示例封面](/images/cover.svg)
