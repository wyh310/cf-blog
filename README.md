# cf-blog：放在 Cloudflare 上的 Hexo 博客骨架（零绑卡版）

文章 = `source/_posts/*.md`，**图片 = GitHub 仓库 `source/images/uploads/`**，可选在线后台 = `source/admin/`。

> **这一版不需要银行卡。** 不用 Cloudflare R2、不用绑定付款方式、不用 Access Key / Secret Key、不用图片子域名、不用配 CORS。图片随文章一起提交到 GitHub，由 Cloudflare Pages 免费分发。

## 部署前只改两处

| 占位符 | 换成什么 | 在哪改 |
| --- | --- | --- |
| `blog.example.com` | 你要绑定的博客域名 | `_config.yml` 的 `url` |
| `你的GitHub用户名/cf-blog` | 你的仓库（`用户名/仓库名`） | `source/admin/config.yml` 的 `repo` |

绑域名是在 Cloudflare 后台点，不用写进源码。详见《Cloudflare博客搭建方法与数据说明.html》。

## 目录里有什么

| 路径 | 作用 |
| --- | --- |
| `_config.yml`、`_config.butterfly.yml`、`package.json` | 站点与主题配置 |
| `source/_posts/*.md` | 文章，一个 md 文件就是一篇 |
| `source/admin/index.html`、`source/admin/config.yml` | 可选的在线后台（Sveltia CMS），已配好「图片直接进仓库 **+ 拖进去自动压缩**」 |
| `source/images/uploads/` | 正文图片放这里，会随仓库一起发布 |
| `source/images/cover.svg` | 默认封面 |
| `tools/add-images.sh`、`tools/add_images.py` | 可选进阶：命令行批量放图并自动压缩（能选像素级无损），打印 Markdown 链接 |
| `wrangler.jsonc` | 可选的命令行部署配置 |

## 第一次本地跑起来（可选）

```bash
cd cf-blog
npm install
npm run build      # 生成 public/ 目录
npm run server     # 浏览器打开 http://localhost:4000 预览
```

## 上线（推荐：Cloudflare Pages 连 GitHub）

1. GitHub 新建仓库，把本目录（不含 `node_modules/`、`public/`）推上去：

```bash
git init && git add -A && git commit -m "init blog"
git remote add origin https://github.com/你的用户名/cf-blog.git
git push -u origin main
```

2. 把 `_config.yml` 里的 `url` 改成你要绑定的域名。
3. Cloudflare Dashboard → **Workers & Pages** → **Create**。新版会先弹出「创建应用 / 创建新项目」选择框，**点最下面「需要使用旧版 Pages 工作流？继续前往 Pages」**，再选 **Connect to Git** → 选这个仓库。
4. 构建设置：Framework preset = `None`，Build command = `npm run build`，Build output directory = `public`。
5. Save and Deploy。拿到 `xxx.pages.dev` 后，进项目 → **Custom domains** → 填你的域名，自动加解析 + 自动签证书。

> 如果填自定义域时提示该主机名已有记录，先到 Cloudflare DNS 删掉旧的 A / CNAME 记录再填。

## 在线后台（可选，手机也能发文）

`source/admin/` 里已经放好一个**纯前端**的可视化后台：打开 `https://你的域名/admin/` 就能填表写文章，不用手敲 front-matter。它没有服务器、没有数据库，本质是替你把 `.md` 文件写进 GitHub 仓库；文章仍然躺在 `source/_posts/` 里，跟手写完全一样。

**一次性配置（3 步，只做一次）**：

1. 用记事本打开 `source/admin/config.yml`，把标「←」的 `repo` 换成你自己的仓库，提交到 GitHub。
2. GitHub → 头像 → **Settings** → **Developer settings** → **Personal access tokens** → **Fine-grained tokens** → **Generate new token**，仓库范围只选这一个仓库，权限勾 **Contents: Read and write**。生成后复制保存。
3. 浏览器打开 `https://你的域名/admin/`，点 **Sign In with Token** 粘贴登录。

> 手机上用同样地址打开，浏览器菜单选「添加到主屏幕」，以后点图标就像 App 一样写文章。别人访问 `/admin` 只会看到登录框，没有你的令牌什么也改不了。

**插图不用额外配置，压缩也不用你管**：`config.yml` 里已写好 `media_folder: source/images/uploads` / `public_folder: /images/uploads`，以及 `media_libraries.default.config.transformations`（Sveltia 官方的「上传时自动优化图片」）。后台拖进去的图片会**先在浏览器里转 WebP、缩到 1600 以内、去掉 EXIF**，压好的小图才提交进 GitHub 仓库，文件名和文章里的链接自动改成 `.webp`，不会破图。大原图从没进过仓库、更不会留在 Git 历史里。手机、电脑、换浏览器都一样生效，不用装软件、不用跑命令。不需要任何密钥、不需要 CORS、不需要第二个域名。

- 默认参数：照片 / HEIC 质量 80、PNG（多为截图）质量 95、最大 1600 × 1600（只缩不放）。嫌不够清晰把 `quality` 调成 85。
- 动图（GIF / 动态 WebP / PNG）保持原样（不会只剩第一帧）；SVG 只删冗余元数据。
- 这是**有损 WebP**，肉眼几乎无差但做不到「一个像素不丢」；截图要像素级无损用下面的 `add-images.sh`。
- 单张上限 10 MB，且比对的是**压缩后**的文件，手机 4~8 MB 原图能顺利进来。
- **只在后台拖图时生效**：在 GitHub 网页手动上传、或命令行直接 push 原图，不经过这一步。

### 图文混排怎么发

**不用先把所有图传好、记住链接、回来一个个拼，也不用先压图。** 在后台写文章就是：写一段文字 → 光标停住 → 点工具栏「插入图片」，或直接把图**拖进正文 / 粘贴** → 图片当场自动压缩、提交进仓库、链接自动出现在光标处 → 接着写下一段 → 再插下一张。手机上点「插入图片」从相册选图即可。

之前传过的图在后台左侧 **Asset Library** 里能翻到，点一下就能再插。封面框留默认 `/images/cover.svg` 即可；想换成自己传的图，在 Asset Library 复制 `/images/uploads/xxx.jpg` 粘进封面框。

## 以后发文章

三种方式，任选：

- **在线后台**（推荐手机用）：打开 `/admin/` 填表发布，图文混排最省事。
- **GitHub 网页**（零配置）：仓库 → `source/_posts/` → `Add file` → `Create new file`，文件名 `xxx.md`，开头按 `scaffolds/post.md` 填好 front-matter，正文写 Markdown，提交即自动发布。
- **本地命令行**（要 Node 22）：

```bash
npm run new -- "文章标题"     # 生成 source/_posts/文章标题.md
npm run server                # http://localhost:4000 本地预览
git add -A && git commit -m "新文章" && git push
```

之后每次提交都自动发布，没有部署命令、没有 CI 配置。

## 图片怎么放

**最常用：在后台正文里直接插图**（见上节），边写边传、**拖进去自动压缩**，不用管链接、不用先压图。

**手写 md 时**：把图片文件放进 `source/images/uploads/`，正文里写相对路径：

```markdown
![图片说明](/images/uploads/demo.png)
```

**可选进阶：批量放图（脚本自动压缩，能做到像素级无损）**

> 后台拖图已经会自动压缩，这一步**不是必须的**。只有「一次放几十张图」或「截图 / 文字图想要一个像素都不丢的真无损」时才用得上——后台统一走有损 WebP。

```bash
pip3 install Pillow                    # 依赖只装一次；Windows 用 pip install Pillow
bash tools/add-images.sh 照片.jpg       # 单张
bash tools/add-images.sh ./photos/      # 整个目录
bash tools/add-images.sh --dry-run ./photos/   # 只看效果、不写入
git add -A && git commit -m "加图" && git push
```

Windows 没有 bash 就跑 `python tools/add_images.py ./photos/`。脚本对每张图**同时压「有损 q80」和「无损」两版，谁小用谁**：照片自动有损、截图 / 文字 / 图标自动无损（画质不丢），超过 1600 宽等比缩小，**原图不动**。结果放进 `source/images/uploads/` 并打印上面那种 Markdown 链接。常用参数：`--no-resize`（不缩小）、`--quality 70`（更省）、`--force`（重压同名图）。没装 Pillow 也能用，只是原样复制、不压缩。

> **两条放图路径是独立的**：后台拖图走浏览器自动压缩（有损 WebP），脚本走本地压缩（能选无损）。同一张图挑一条用即可，别两边都放一遍。脚本结果超过后台 10 MB 上限时会当场提醒。

> 图片在仓库里，跟文章绑定在一起：**删了图，文章就会破图**；别随手删。GitHub 只建议仓库 1 GB 以内（5 GB 以内也强烈建议），**不按张数限制**；压成 WebP 后一张 100~200 KB，1 GB 能放几千张。**用后台写文章时图片已自动压好，不用手动压**；只有在 GitHub 网页 / 命令行直接传图，才需要先用 <https://squoosh.app> 把照片转 WebP、质量 80 左右（截图/文字图选「无损」）。Pages 免费额度是无限带宽、500 次构建/月，个人博客远远够。
>
> 四个提醒：① **后台拖图自动压缩**（`source/admin/config.yml` 的 `transformations`），单张上限 10 MB、比对的是压缩后的文件，手机 4~8 MB 原图能顺利进来；② 主题已开**图片懒加载**（`_config.butterfly.yml` 的 `lazyload`），一篇文章里图多也只加载读者看到的那几张；③ **照片用质量 80、截图/文字图用无损，压一次就定稿、别反复另存**，压缩不可逆，原图留本地备份（详见部署手册「5.5」）；④ **删图不能给仓库「减肥」**——Git 历史里还留着，详见「附一」。后台压缩的好处正是**大原图一次都没进过历史**，从源头少占地方。

## 数据存哪

| 数据 | 位置 |
| --- | --- |
| 文章原文、主题配置、后台页面 | **你的 Git 仓库**（唯一源数据） |
| **正文图片** | **同一个 Git 仓库** `source/images/uploads/` |
| 上线后的 HTML/CSS/JS | Cloudflare 边缘节点（只读副本，随时重建） |
| 数据库 | 没有 |

Cloudflare 不保管你的文章原文。平台换掉，只要仓库还在，改一条 DNS 就能搬家，文章和图片一篇不丢。

## 命令行部署（可选）

想用 Workers + Static Assets 而不是 Pages：

```bash
npx wrangler login
npm run build
npx wrangler deploy
```

`wrangler.jsonc` 里 `name` 改成你的 Worker 名；自定义域在 Worker 的 Settings → Domains & Routes 添加（要求域名 DNS 托管在 Cloudflare）。

## 以后有卡了想换 R2

R2 免费 10 GB，但**开通必须绑定付款方式**（Visa / Mastercard / 银联 / PayPal 等，免费额度内不扣费）。真要换的话：建桶并绑自定义域 → 把 `config.yml` 改回 `media_libraries.cloudflare_r2` 并给桶加 CORS → 把图片搬进桶、把文章里的 `/images/uploads/` 前缀换成图片域名。个人博客一般不必折腾。
