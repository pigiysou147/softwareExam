## 外包前端（中级偏上）面试题（含提示与深入）

### 带提示点的题目（建议从中选 10–12 题）
1) 事件循环与渲染顺序（micro/macro、rAF）
- 提示点：按顺序排 `Promise.then`、`setTimeout`、`requestAnimationFrame`；microtask 饥饿如何卡帧；避免强制同步布局。

2) 原型链与 this 绑定
- 提示点：方法解构导致 this 丢失；箭头函数 vs `bind`；`class` 与原型本质。

3) 闭包与内存泄漏
- 提示点：未清理计时器/监听器；`WeakMap` 缓存；DevTools Heap 快照与 retainers。

4) 模块与 Tree‑shaking
- 提示点：ESM 静态分析；命名导出优于默认导出；`sideEffects` 字段与顶层副作用。

5) 回流重绘与合成层
- 提示点：读写分离（measure vs mutate）；`transform/opacity` 避免布局；`will-change` 滥用代价。

6) 构建优化与分包（Vite/Webpack）
- 提示点：路由/页面级拆分；vendor 抽离与共享依赖；预构建与缓存；产物可视化分析。

7) 长效缓存与版本策略
- 提示点：`contenthash + immutable`；入口 HTML/入口脚本短缓存；CDN 与回滚策略。

8) TypeScript 高级类型
- 提示点：可辨识联合建模 API；条件类型与工具类型；运行时校验（zod）。

9) Monorepo 与内包管理
- 提示点：pnpm workspace 去重；Turborepo 增量；版本一致性与发布流程。

10) CSS 架构与复用
- 提示点：BEM vs 原子化（Tailwind）取舍；主题（CSS Variables）；样式隔离与按需加载。

11) 设计系统与组件库
- 提示点：Design Token → 组件 → 文档/Storybook；按需引入与摇树；a11y 基线。

12) HTTP 缓存（强/协商组合）
- 提示点：静态资源强缓存+版本化；HTML 协商/短缓存；ETag 与回源成本。

13) CORS 与身份/安全
- 提示点：预检与凭证；SameSite 跨站 Cookie 限制；Authorization 携带策略。

14) XSS/CSRF/Clickjacking
- 提示点：`v-html/innerHTML` 风险、CSP；SameSite/双重提交；`frame-ancestors`。

15) OAuth2/OIDC（前端侧）
- 提示点：PKCE vs 隐式流；Token 存储与刷新；登出与撤销。

16) Core Web Vitals（LCP/CLS/INP）
- 提示点：LCP 候选识别；内联关键 CSS；尺寸保留与优先级；输入延迟来源与切片。

17) 资源优化（图像/字体）
- 提示点：AVIF/WebP、自适应图；`preload/prefetch/priorities`；`font-display` 与子集化。

18) SSR/SSG/ISR/流式/岛架构
- 提示点：TTFB/TTI 权衡；缓存层与回源；局部水合与边界。

19) 前端监控与稳定性
- 提示点：RUM 指标；错误上报与 Source Map 管理；长任务监控与分片化。

20) Server State vs Client State
- 提示点：失效/重试/去重策略；与本地业务状态解耦；并发请求控制。

21) 路由高级
- 提示点：并发导航；数据预取；滚动还原；权限控制与错误边界。

22) 复杂表单
- 提示点：异步校验时机；受控/非受控取舍；性能（分片渲染/虚拟化）。

### 深入加考（选 2–3 题）
A) 构建体积与分包优化（对应题 6）
- 场景：首屏 JS 3MB，冷启动慢，两周内减半。
- 追问：可视化/重复依赖定位；替换与拆分（moment→dayjs、图表库按需、UI 精简）；动态导入边界与缓存命中。
- 评估：度量-改进-复测闭环；缓存与分包联动理解。

B) HTTP 缓存与回滚（对应题 12）
- 场景：灰度发布后需快速回退，用户端尽量少刷新。
- 追问：入口 HTML 短缓存 + 资源长缓存；版本清单/manifest；CDN 回源与回滚策略。
- 评估：命中率/回源成本平衡；版本切换原子性。

C) Core Web Vitals 实战（对应题 16）
- 场景：LCP 3.2s、CLS 0.18、INP 300ms，目标一周内过线。
- 追问：LCP 候选与关键 CSS；图片优先级与尺寸保留；事件处理切片/去抖；监控验证与回归防护。
- 评估：指标归因与优先级管理；副作用控制。

D) SSR/SSG/ISR/流式/岛架构选型（对应题 18）
- 场景：营销页、后台系统、内容站点三类场景。
- 追问：各自适配模式；边缘缓存/回源；局部水合与数据一致性（闪烁/双重请求）。
- 评估：场景-方案映射清晰；成本、团队栈与运维复杂度。

E) 超大表格的交互与性能（对应题 22）
- 场景：10 万行表格，需排序/筛选/冻结列。
- 追问：行/列虚拟化与粘性列；可变行高测量；滚动同步与分片计算；服务器端分页/排序权衡。
- 评估：虚拟化抽象正确；操作反馈与可用性不退化。

F) WebSocket 断线重连与幂等（扩展）
- 场景：移动弱网，消息偶发丢失/重复。
- 追问：指数退避+抖动；心跳/超时；消息 ack/序列号/去重缓存；离线队列与幂等键设计。
- 评估：一致性与资源消耗平衡；异常流覆盖。

