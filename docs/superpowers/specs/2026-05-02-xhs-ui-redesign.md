---
title: 小红书风格 UI 改版设计规范
date: 2026-05-02
status: approved
---

# 小红书风格 UI 改版

## 目标

将现有社区论坛前端升级为参考小红书风格的视觉设计，提升内容发现体验。不改变后端 API，不新增数据字段（封面图占位，后续迭代）。

---

## 设计决策

| 维度 | 决策 |
|------|------|
| 布局 | 瀑布流双列（移动端）/ 四列（PC 端） |
| 主色 | `#FF2442`（小红书红） |
| 卡片 | 图片优先，封面区用渐变粉色占位图 |
| 导航 | 白色顶栏 + 胶囊频道筛选 |

---

## 配色系统

```
主色:       #FF2442
主色浅背景:  #FFF0F2
主色边框:    #FFCCD3
背景:        #F5F5F5
卡片背景:    #FFFFFF
主文字:      #1A1A1A
次文字:      #666666
辅助文字:    #999999
分割线:      #F0F0F0
```

---

## 导航栏（AppLayout.vue）

单行高度 56px，白底，`box-shadow: 0 1px 0 #F0F0F0`，`position: sticky; top: 0`。

结构（左→右）：
1. **Logo** — "社区"，`#FF2442`，20px bold
2. **频道胶囊** — 横向滚动，`flex: 1`，隐藏滚动条
   - 默认态：白底，`#E8E8E8` 边框，`#666` 文字
   - 选中态：`#FF2442` 底，白字，600 weight
3. **发布按钮** — `#FF2442` 圆角按钮，仅登录后显示（替代现有 FAB，FAB 保留移动端）
4. **头像** — 32px 圆形，点击展开下拉菜单；未登录显示"登录"文字按钮

移动端（<768px）：Logo + 发布按钮 + 头像，频道胶囊移到导航栏下方独立一行。

---

## 频道筛选

现有 `el-tabs` 替换为胶囊 pill 横向滚动条。

- PC：嵌在导航栏内（`flex: 1` 区域）
- 移动：导航栏下方独立行，`padding: 8px 12px`，可横向滚动
- 选中态同步 URL query `?channel_id=xxx`（逻辑不变）

---

## 瀑布流卡片（PostCard.vue）

用 CSS `columns` 实现瀑布流，替换现有 `el-card` 单列列表。

### 响应式列数

| 断点 | 列数 | 间距 |
|------|------|------|
| ≥1024px | 4 列 + 右侧边栏 | 10px |
| 768–1023px | 3 列，无侧边栏 | 8px |
| <768px | 2 列，无侧边栏 | 6px |

### 卡片结构

```
┌─────────────────┐
│   封面区         │  ← 渐变粉色占位（后续替换为 cover_url 字段）
│  aspect-ratio   │    tall(3:4) / mid(1:1) / short(4:3) 按 post.id % 3 分配
├─────────────────┤
│ 标题（2行截断）  │  13px, #1A1A1A
│ 频道标签         │  10px, #FF2442 胶囊
│ 头像 昵称  ♥数  │  11px, #999
└─────────────────┘
```

- 圆角 10px，白底，无阴影（hover 时 `translateY(-2px)` + 轻阴影）
- `break-inside: avoid`，`margin-bottom: 8px`（PC）/ `6px`（移动）
- 封面比例由 `post.id % 3` 决定：0→tall，1→mid，2→short（保证错落感，无需后端字段）

---

## 右侧边栏（PC ≥1024px）

宽度 240px，`flex-shrink: 0`，两个卡片：

1. **热门帖子** — 按 `like_count` 降序取前 5 条，前 3 名红色序号，点击跳转帖子详情
   - 数据来源：复用首页 `['posts']` 查询缓存，客户端排序取 top5
2. **全部频道** — 展示所有频道胶囊，点击筛选

---

## 页面级改动范围

| 文件 | 改动 |
|------|------|
| `AppLayout.vue` | 重写导航栏，嵌入频道胶囊（PC），移除 `el-menu` |
| `PostList.vue` | 移除 `el-tabs`，改为胶囊筛选（移动端）；列表改为瀑布流容器；新增侧边栏（PC） |
| `PostCard.vue` | 重写卡片样式，加封面占位区，调整底部布局 |
| `App.vue` | 全局 CSS 变量注入（颜色 token） |

其余页面（PostDetail、UserProfile、Favorites、PostCreate、PostEdit）本次不改版。

---

## 封面占位方案

当前无 `cover_url` 字段，封面区使用渐变色占位：

```css
background: linear-gradient(135deg, #FFF5F6 0%, #FFE0E5 100%);
```

中心显示 🖼️ emoji（低透明度）。后续迭代：后端 `PostModel` 加 `cover_url` 字段，前端判断有值则 `<img>`，无值则占位。

---

## CSS 变量

在 `App.vue` `<style>` 中注入全局变量：

```css
:root {
  --color-primary: #FF2442;
  --color-primary-light: #FFF0F2;
  --color-primary-border: #FFCCD3;
  --color-bg: #F5F5F5;
  --color-card: #FFFFFF;
  --color-text-primary: #1A1A1A;
  --color-text-secondary: #666666;
  --color-text-muted: #999999;
  --color-divider: #F0F0F0;
}
```

---

## 不在本次范围内

- 封面图上传功能
- 搜索框
- 用户关注/粉丝
- PostDetail / UserProfile / Favorites 页面改版
- 深色模式
