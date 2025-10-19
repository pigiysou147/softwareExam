## 平台域名切换整改指引（PC端，里约网关）

> 目标：将平台域名由 `https://fzh.ywtg.foshan.gov.cn` 平稳切换为 `https://yzhcs.fszsj.fs.gdgov.cn`，保障第三方应用、专题与平台间在里约网关同域代理下的兼容性与安全性。本文提供前端（Vue）与后端（Java）技术整改要点、示例与常见问题排查清单。

### 适用范围
- **终端形态**：PC Web（无小程序端）
- **网关形态**：腾讯里约网关统一代理，同域访问
- **对接方式**：平台提供前端登录 SDK，第三方应用通过 SDK 获取平台 token 并在后端调用平台 `auth` 服务获取用户信息

---

## 总体整改原则
- **同源优先**：所有静态资源、API、回调地址、WebSocket 统一使用相对路径或基于 `window.location.origin` 动态构造，避免硬编码域名。
- **配置注入**：所有域名、网关地址一律配置化（环境变量/配置文件/启动参数），严禁在代码中写死。
- **HTTPS-only**：全链路 HTTPS，禁止混合内容；同步更新并校验证书及中间证书链；必要时开启/校验 HSTS。
- **Cookie/SSO**：如涉及跨子域共享登录态，统一规划 Cookie `Domain`、`SameSite`、`Secure`；默认同域优先。
- **CORS最小化**：在同域前提下不启用 CORS；如确需跨域，优先在网关集中配置，后端仅兜底。
- **向后兼容**：在切换窗口内允许旧域名 301 跳转至新域名（或灰度），设置合适 `TTL` 并监控。

---

## 实施步骤（建议）
- **网关准备**
  - 注册新域名站点、导入 TLS 证书（含完整链）、配置路由/API 代理与 Host 规则
  - 对齐 `X-Forwarded-*` 透传策略，确认回源协议与主机头策略
- **DNS与发布**
  - 配置新域名记录（A/CNAME），降低 `TTL`，按需灰度；预发布环境先对齐
  - 预发/联调验证后上线，观察 24–48 小时，逐步提升流量
- **平台与第三方改造**
  - 前端改造：去除硬编码域名；动态 `baseURL`、`loginUrl`；静态资源与路由基于相对路径
  - 后端改造：平台服务调用全部配置化；必要时从请求头动态解析 `origin`
  - SDK：`loginUrl` 指向新域名或基于 `location.origin` 动态生成
- **回滚预案**
  - 保留旧域名路由配置与证书；必要时切回或临时 302/反代回旧域名

---

## 前端（Vue）整改清单与示例

### 必做检查
- **不要写死域名**：`https://fzh.ywtg.foshan.gov.cn/...` 或 `https://yzhcs.fszsj.fs.gdgov.cn/...` 统统替换为相对路径（`/api/...`、`/sso/login`、`/feature/list`）。
- **动态基址**：HTTP 客户端 `baseURL` 从环境变量或 `window.location.origin` 构造。
- **路由与资源**：`router base`、静态资源 `publicPath`/`base` 使用 `/`，避免绝对域名。
- **WebSocket**：基于 `location.protocol/host` 动态构造 `wss://<host>/ws/...`。
- **SDK loginUrl**：动态生成为 `location.origin + '/sso/login'`。

### Axios 基础封装（Vite 项目示例）
```ts
// src/utils/http.ts
import axios from 'axios';

const runtimeOrigin = window?.location?.origin ?? '';
const envBase = (import.meta as any).env?.VITE_API_BASE_URL?.trim?.();
const baseURL = envBase || `${runtimeOrigin}/api`;

export const http = axios.create({
  baseURL,
  withCredentials: true,
  timeout: 15000,
});

// 用法：
// http.get('/auth/userinfo') // 实际请求：{origin}/api/auth/userinfo
```

### 登录 SDK 初始化（loginUrl 动态）
```ts
// 伪示例：以第三方平台前端集成为例
import { PlatformSDK } from '@vendor/platform-sdk';

PlatformSDK.init({
  loginUrl: `${location.origin}/sso/login`,
  // 其他参数...
});
```

### WebSocket 动态地址
```ts
const scheme = location.protocol === 'https:' ? 'wss' : 'ws';
const ws = new WebSocket(`${scheme}://${location.host}/ws/notify`);
```

### Router 与静态资源
```ts
// src/router/index.ts
import { createRouter, createWebHistory } from 'vue-router';

export default createRouter({
  history: createWebHistory(import.meta.env.BASE_URL || '/'),
  routes: [/* ... */],
});
```

> Vite `base`/Webpack `publicPath` 建议保持 `'/'`，打包产物以相对路径引用资源，避免注入绝对域名。

---

## 后端（Java / Spring）整改清单与示例

### 必做检查
- **平台服务地址配置化**：如 `PLATFORM_BASE_URL=https://yzhcs.fszsj.fs.gdgov.cn`；禁用硬编码。
- **优先同域**：若后端仅在网关后，同域可用相对路径回调；但服务间调用通常仍需基址配置。
- **请求头透传**：确保网关透传 `X-Forwarded-Proto/Host`；服务从请求动态推导 `origin` 作为兜底。
- **Cookie 与回调**：如涉及跨子域，正确设置 `Domain`、`SameSite`、`Secure`；更新 OAuth/SSO 回调白名单。

### 动态解析平台基址（基于请求头兜底）
```java
// 示例：从配置优先，缺省则从请求头/X-Forwarded-* 推导
import jakarta.servlet.http.HttpServletRequest;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.util.StringUtils;

public class PlatformBaseUrlResolver {
    private final String configuredBaseUrl;

    public PlatformBaseUrlResolver(@Value("${platform.base-url:}") String configuredBaseUrl) {
        this.configuredBaseUrl = configuredBaseUrl;
    }

    public String resolve(HttpServletRequest request) {
        if (StringUtils.hasText(configuredBaseUrl)) {
            return configuredBaseUrl;
        }
        String proto = getFirstNonEmpty(
                request.getHeader("X-Forwarded-Proto"),
                request.getScheme()
        );
        String host = getFirstNonEmpty(
                request.getHeader("X-Forwarded-Host"),
                request.getHeader("Host")
        );
        if (!StringUtils.hasText(host)) {
            int port = request.getServerPort();
            String portStr = (port == 80 || port == 443) ? "" : ":" + port;
            host = request.getServerName() + portStr;
        }
        return proto + "://" + host;
    }

    private String getFirstNonEmpty(String... values) {
        for (String v : values) {
            if (StringUtils.hasText(v)) return v;
        }
        return null;
    }
}
```

### WebClient 调用平台 auth 服务
```java
import org.springframework.beans.factory.annotation.Value;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.http.HttpHeaders;
import org.springframework.http.MediaType;
import org.springframework.util.StringUtils;
import org.springframework.web.reactive.function.client.WebClient;

@Configuration
public class PlatformClientConfig {
    @Bean
    public WebClient platformWebClient(@Value("${platform.base-url:}") String baseUrl) {
        WebClient.Builder builder = WebClient.builder()
                .defaultHeader(HttpHeaders.ACCEPT, MediaType.APPLICATION_JSON_VALUE);
        if (StringUtils.hasText(baseUrl)) {
            builder.baseUrl(baseUrl);
        }
        return builder.build();
    }
}

// 使用：
// webClient.get()
//   .uri("/auth/userinfo")
//   .headers(h -> h.setBearerAuth(platformToken))
//   .retrieve()
//   .bodyToMono(UserInfo.class);
```

### CORS（仅兜底，优先在网关配置）
```java
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.web.servlet.config.annotation.CorsRegistry;
import org.springframework.web.servlet.config.annotation.WebMvcConfigurer;

@Configuration
public class CorsConfig {
    @Bean
    public WebMvcConfigurer corsConfigurer() {
        return new WebMvcConfigurer() {
            @Override
            public void addCorsMappings(CorsRegistry registry) {
                registry.addMapping("/**")
                        .allowedOrigins("https://yzhcs.fszsj.fs.gdgov.cn")
                        .allowedMethods("GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS")
                        .allowCredentials(true)
                        .maxAge(3600);
            }
        };
    }
}
```

### Cookie（如需跨子域共享）
```java
import org.springframework.http.ResponseCookie;

ResponseCookie cookie = ResponseCookie.from("PLATFORM_SSO", token)
        .domain("fszsj.fs.gdgov.cn") // 如需跨子域共享；同域可不设置
        .path("/")
        .httpOnly(true)
        .secure(true)
        .sameSite("Lax") // 若跨站回跳需携带，考虑 SameSite=None 且必须 Secure
        .build();
```

---

## SDK 对接注意事项（第三方/专题）
- **loginUrl 必须同域**：`loginUrl = location.origin + '/sso/login'`，不要写死旧/新域名。
- **回调与白名单**：更新 OAuth/SSO 回调 URI、跳转白名单至新域名；清理旧域名项。
- **Token 使用**：通过平台 token 调 `auth` 服务获取用户信息时，服务端基址配置为新域名或同域相对路径。
- **缓存刷新**：清理本地缓存/Service Worker，避免老配置残留。

---

## 冒烟与回归清单（建议）
- 登录/退出/续期：SDK 拉起、回跳、Cookie 有效，跨页身份保持
- 核心 API：`/api/auth/userinfo`、业务接口 2xx；无 CORS/Mixed Content 报错
- 资源加载：静态资源 200；无任何指向旧域名资源
- WebSocket：连通、心跳正常；`Origin`/`Host` 校验通过
- 文件上传/下载：跨域与大小限制符合预期；`Content-Disposition` 正确
- 跳转/路由：站内跳转使用相对路径；外链白名单可控

---

## 常见问题与排查
1. **网关未注册新域名站点，报 `resource not found`**：联系网关实施同学排查路由/站点/证书状态。
2. **网络不通**：需运维协助排查源、目标安全策略/ACL/防火墙，含网关到后端回源链路。
3. **预发布环境未部署服务**：补齐预发服务与网关配置，先在预发完成全量回归。
4. **前端/后端存在硬编码旧域名导致跨域**：统一改相对路径或新域名；修正 CORS；目标是全站资源和接口使用新域名访问。
5. **网关站点或 API 代理仍匹配旧域名 Host**：同步调整 Host 规则与回源策略，并清理旧域名专用匹配。
6. **证书问题（域名不匹配/中间证书缺失）**：重新签发或补齐链；浏览器/系统信任校验。
7. **HSTS/重定向循环**：网关与后端同时跳转导致 301/302 循环，保持仅一处强制 HTTPS。
8. **DNS 缓存/TTL 未失效**：客户端/操作系统/本地网络缓存未刷新；等待或显式清理。
9. **Cookie 丢失/登录态不生效**：`Domain/SameSite/Secure` 设置不当；跨子域回跳需 `SameSite=None; Secure`。
10. **OAuth 重定向 URI 未更新**：平台或第三方未更新白名单；严格大小写与路径一致性。
11. **WebSocket 403/握手失败**：`Origin/Host` 校验不通过；网关未转发升级头；确认 `wss://{host}`。
12. **Mixed Content**：页面或接口仍走 `http://`；统一替换为 `https://` 或相对协议。
13. **CDN/边缘缓存未刷新**：命中旧资源；刷新或版本化静态资源。
14. **预检（OPTIONS）被拦截**：非同域调用且网关未放行方法/头；按需在网关放开或改同域。
15. **SSR/构建时注入旧域名**：构建脚本/环境变量遗留；统一改为运行时可变配置。
16. **Referer 防盗链/来源校验**：新域名未加入白名单；更新后端/网关策略。

---

## 变更窗口建议（沟通与回滚）
- 明确发布窗口与回滚链路，旧域名保留 7–14 天可回退；对关键业务设置监控与告警阈值。
- 发布群：网关实施、运维、平台后端、前端、第三方各一名负责人在线待命。

---

## 附：运维与验证命令
```bash
# 基本连通与证书
curl -I https://yzhcs.fszsj.fs.gdgov.cn

# 资源/接口自检（期望 200 或 3xx）
curl -sS https://yzhcs.fszsj.fs.gdgov.cn/favicon.ico -o /dev/null -w "%{http_code}\n"
curl -sS https://yzhcs.fszsj.fs.gdgov.cn/api/auth/userinfo -o /dev/null -w "%{http_code}\n"
```

---

## 结语
按照本指引完成“去硬编码、配置化、同域化、HTTPS 化”整改，并配合网关、DNS 及发布流程进行灰度与回归，可平稳完成由 `fzh.ywtg.foshan.gov.cn` 向 `yzhcs.fszsj.fs.gdgov.cn` 的域名切换。