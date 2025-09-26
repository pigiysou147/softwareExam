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

### 模块化清单（完整）
#### 模块一｜核心 JS 与浏览器机制（约 8 分钟）
1) 事件循环与渲染顺序：micro/macro tasks、requestAnimationFrame 在帧内何时执行
- 期望要点：任务队列优先级、渲染阶段、避免布局抖动

2) 原型链与 this 绑定：class vs 原型、bind/apply/call 的差异与常见陷阱
- 期望要点：词法 vs 动态绑定、箭头函数 this、方法丢失

3) 闭包与内存泄漏：常见泄漏源与排查手段
- 期望要点：定时器/事件未清理、全局缓存、DevTools heap/retainers

4) 模块系统与 Tree‑shaking：ESM vs CJS、sideEffects 字段影响
- 期望要点：静态可分析、命名导出、摇树失效场景

5) 渲染与回流重绘：避免强制同步布局与布局抖动
- 期望要点：读写分离、合成层、will-change 的利弊

#### 模块二｜工程化与可维护（约 10 分钟）
6) 构建优化：Vite/Webpack 的分包策略与动态导入边界
- 期望要点：路由/页面级拆分、共享依赖抽离、预构建与缓存

7) 长效缓存与版本策略：hash、CDN、Cache‑Control/ETag
- 期望要点：immutable、入口文件短缓存、资源失效与回滚

8) TypeScript 高级类型：Discriminated Union、条件类型、实用工具类型
- 期望要点：API 响应类型建模、窄化、最小可信输入校验

9) Monorepo 与内包管理：pnpm workspace/Turborepo/Nx 取舍
- 期望要点：版本一致性、构建加速、依赖去重、发布流程

10) CSS 架构与复用：BEM、CSS Modules、Tailwind、CSS‑in‑JS 取舍
- 期望要点：作用域、主题化、原子化 vs 语义化、性能与维护成本

11) 设计系统与组件库：设计 Token、按需引入、Tree‑shaking
- 期望要点：可定制性、无障碍、文档/Storybook、回归风险控制

#### 模块三｜网络与安全（约 8 分钟）
12) HTTP 缓存：强缓存 vs 协商缓存如何组合落地
- 期望要点：资源分级、回源开销、灰度与回滚策略

13) CORS 与身份：预检、凭证、SameSite 与跨域 Cookie 风险
- 期望要点：Authorization 头、跨域携带策略、替代方案

14) XSS/CSRF/Clickjacking 防护
- 期望要点：CSP/模板转义、SameSite/双重提交、Frame‑Options

15) OAuth2/OIDC 前端实践
- 期望要点：PKCE、Token 存储与刷新、重放与注销处理

#### 模块四｜性能与交付（约 8 分钟）
16) Core Web Vitals：LCP/CLS/INP 的典型优化手段
- 期望要点：关键资源优化、尺寸保留位、交互延迟来源

17) 资源优化：图片与字体策略
- 期望要点：AVIF/WebP、自适应图、preload/prefetch、font‑display

18) SSR/SSG/ISR/流式渲染/岛架构选型
- 期望要点：TTFB/TTI 权衡、缓存层设计、局部水合

19) 前端监控与稳定性
- 期望要点：RUM、错误上报、Source Map 管理、长任务监控

#### 模块五｜框架与状态（约 6 分钟）
20) Server State vs Client State：React Query/SWR 与 Redux/Pinia 的边界
- 期望要点：失效/缓存策略、副作用隔离、并发与重试

21) 路由高级：数据预取、滚动还原、权限控制、并发导航
- 期望要点：路由守卫、懒加载、错误边界

22) 复杂表单：异步校验、依赖联动与性能
- 期望要点：受控与非受控、节流/去抖、分片渲染

### 场景题（任选 3）
23) 首页 CLS 飙升，如何定位并在一周内恢复指标？
- 期望要点：RUM/回放、占位符策略、关键资源排序

24) 10 万行表格的交互与性能方案？
- 期望要点：虚拟滚动、窗口化渲染、滚动同步与粘性列

25) WebSocket 断线重连设计
- 期望要点：指数退避、心跳/超时、去重与幂等

26) 包体积 3MB，如何两周内减半？
- 期望要点：可视化分析、拆包与共享依赖、按需与替代库

27) 时区与国际化问题频发，如何制定全链路策略？
- 期望要点：UTC 存储/本地化显示、RTL、货币/复数

28) 低端机卡顿与掉帧，如何定位热点并缓解？
- 期望要点：Performance/Profiler、任务切片、Offscreen/Worker

### Vue 3 专项（中高级，含提示点）
1) 响应式系统与陷阱
- 提示点：`ref` vs `reactive` 解包规则；`toRef/toRefs`；解构/闭包/跨组件传递导致丢失；`shallowRef/shallowReactive` 的使用场景；`markRaw/readonly` 的边界。

2) computed / watch / watchEffect 策略
- 提示点：computed 纯派生与缓存；`watch({ deep, immediate, flush })` 取舍；依赖循环与防抖/节流；`watchEffect` 的依赖收集与清理。

3) 组件通信与 `v-model` 机制
- 提示点：`modelValue`/`update:modelValue` 契约；多 `v-model` 命名；修饰符透传与处理；受控/非受控组件设计。

4) provide/inject 与全局状态（Pinia）
- 提示点：跨层解耦与可测试性；何时上升为 store；服务定位器反模式风险；SSR 中的作用域隔离。

5) 路由与数据获取（Vue Router 4）
- 提示点：导航守卫与权限；路由级懒加载；数据预取与错误边界；滚动行为与并发导航。

6) 表单与校验
- 提示点：受控字段的性能开销；`v-model` 与 `:modelValue + @update` 的权衡；异步校验与提交防抖；通用表单项抽象与 `slots`/attrs 透传。

7) 性能优化
- 提示点：`<KeepAlive>` 命中条件与缓存策略；`Teleport` 的适用场景；长列表虚拟化策略；避免不必要渲染（分片、`v-memo`、`defineComponent` 性能注意点）。

8) SSR/同构
- 提示点：避免直接访问 `window/document`；`onServerPrefetch`；水合不匹配定位；静态站点生成与增量再生的取舍。

9) 生态与工程
- 提示点：Vite 环境变量与多环境构建；按需引入与 Tree‑shaking；组件库（Element Plus/Naive UI）二次封装；单元/端到端测试基线。

### Vue 3 深入场景（任选 2 深挖）
A) 自定义表单控件的 `v-model` 设计
- 场景：同一组件需要同时支持 `value` 与 `checked` 两种模型，并处理 `trim/number` 修饰符。
- 追问：多模型命名与事件；修饰符透传方案；受控/非受控切换与受控警告。
- 评估：契约清晰、边界覆盖、与表单生态的兼容。

B) 长列表交互卡顿
- 场景：1 万行列表，含筛选与高亮。
- 追问：虚拟滚动窗口化；计算派生数据的缓存与切片；`watchEffect` 清理；渲染热点定位。
- 评估：渲染与计算分离、体验不退化。

C) SSR 水合不匹配排查
- 场景：仅生产环境报水合警告。
- 追问：非确定性渲染源（时间、随机数、异步）；`onServerPrefetch`；差异定位与兜底策略。
- 评估：定位路径清晰、最小化影响。

D) 复杂表单与依赖校验
- 场景：多字段联动、异步唯一性校验。
- 追问：字段依赖图；节流/去抖与取消；错误聚合与可用性；回填与重置策略。
- 评估：一致性、可维护、性能友好。

