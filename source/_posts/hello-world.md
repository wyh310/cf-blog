---
title: 博客搭好了
date: 2026-11-10 09:00:00
tags:
  - 随笔
categories:
  - 默认分类
cover: /images/cover.svg
---

整站是一堆静态 HTML，放在 Cloudflare 的全球边缘节点上，不用服务器、不用数据库、不用续证书，也不用绑定银行卡。

## 以后怎么发文章

三种方式任选：打开 `/admin/` 用在线后台填表；在 GitHub 网页的 `source/_posts/` 里新建 `.md` 文件；或在本地写好后 `git push`。提交后 Cloudflare 自动构建并发布，大约 30 秒生效。

```bash
npm run new -- "文章标题"
git add -A && git commit -m "新文章" && git push
```

## 数据都放在哪

| 东西 | 位置 |
| --- | --- |
| 文章原文（Markdown） | 你的 Git 仓库 |
| 图片 | **同一个 Git 仓库** `source/images/uploads/`，随文章一起发布 |
| 网站页面（HTML） | Cloudflare 边缘节点，随时可从仓库重建 |
| 在线后台 `/admin/` | 也在这份仓库里，纯前端页面，不改数据存放位置 |

> Cloudflare 只是「发布出去的副本」。真正的家底全在 Git 仓库里，换平台只要改一条 DNS，文章和图片一篇不丢。
