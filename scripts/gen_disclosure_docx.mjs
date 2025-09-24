import { Document, Packer, Paragraph, HeadingLevel, TextRun, ImageRun, AlignmentType, PageOrientation } from 'docx';
import fs from 'fs';

const outPath = '/workspace/docs/patent/技术交底书-路由分级预取-成品.docx';

function heading(text) {
  return new Paragraph({ text, heading: HeadingLevel.HEADING_1 });
}
function subheading(text) {
  return new Paragraph({ text, heading: HeadingLevel.HEADING_2 });
}
function para(text) {
  return new Paragraph({ children: [new TextRun(text)] });
}
function blank() { return new Paragraph({ text: '' }); }

function imagePara(imgPath, width) {
  const data = fs.readFileSync(imgPath);
  return new Paragraph({
    alignment: AlignmentType.CENTER,
    children: [new ImageRun({ data, transformation: { width, height: Math.round(width * 0.62) } })],
  });
}

async function main() {
  const doc = new Document({
    sections: [{
      properties: { page: { margin: { top: 720, right: 720, bottom: 720, left: 720 }, size: { orientation: PageOrientation.PORTRAIT } } },
      children: [
        heading('技术交底书'),
        blank(),
        subheading('一、发明名称'),
        para('一种基于大模型的智能前端路由分级预取与缓存预算调度方法及系统'),
        subheading('二、技术领域'),
        para('涉及前端性能优化与智能调度，具体为利用大模型驱动的路由级分级预取与缓存预算调度。'),
        subheading('三、背景技术'),
        para('现有单页/多页应用的路由切换受网络、设备与资源冷启动影响，首屏与二跳耗时大。传统预取多为静态或启发式，无法兼顾会话差异与实时网络波动；缺少带宽/CPU/存储等预算约束与可解释性。浏览器或CDN的投机预取/预渲染多不感知业务路由语义，不具备个体会话级精细化调度。'),
        subheading('四、发明目的'),
        para('在带宽/CPU/存储/隐私等约束下，最大化路由切换路径的时延收益，提升缓存命中率，降低无效预取，并具备可解释、可审计与灰度回滚能力。'),
        subheading('五、技术方案（概述）'),
        para('方法流程：1) 采集上下文并构建路由资源图；2) 大模型输出候选路由访问概率与资源效用得分（附解释元数据）；3) 在约束下求解分级预取计划（等级、时序、TTL、淘汰优先级）；4) 由Service Worker执行分级预取（并发控制、退避、SWR、动态TTL、降级/取消、在线重排）；5) 记录指标并进行反事实评估以校准阈值与预算。'),
        para('系统模块：上下文采集与图构建模块；大模型预测与打分模块；预算求解模块；SW执行模块；缓存与失效管理模块；反馈学习与反事实评估模块；策略与合规模块。'),
        subheading('六、附图'),
        para('图1 系统架构图'),
        imagePara('/workspace/docs/patent/diagrams/fig1-arch.png', 520),
        para('图2 程序逻辑流程图'),
        imagePara('/workspace/docs/patent/diagrams/fig2-flow.png', 520),
        para('图3 界面交互时序图'),
        imagePara('/workspace/docs/patent/diagrams/fig3-seq.png', 520),
        para('图4 异常与降级处理流程图'),
        imagePara('/workspace/docs/patent/diagrams/fig4-exception.png', 520),
        para('图5 数据结构示意图'),
        imagePara('/workspace/docs/patent/diagrams/fig5-classes.png', 520),
        subheading('七、具体实施方式'),
        para('前端集成：在React Router/Vue Router/Next.js注入中间件，上报候选路由与资源依赖；SW接管分级预取与缓存。'),
        para('预算求解：以期望收益最大化为目标，约束为带宽/CPU/存储与隐私/权限；可用效用密度贪心或近似整数规划。'),
        para('SW执行：维护优先队列、并发限制与SWR；网络恶化触发取消/降级与动态TTL收紧；跨标签页合并预取。'),
        para('反馈与评估：采集命中率、LCP/TTI、二跳耗时、带宽与回退率；反事实评估回写阈值与预算。'),
        para('安全与合规：跨域白/黑名单、隐私标签、权限过滤；策略具备灰度与回滚开关。'),
        subheading('八、权利要求书建议（摘要）'),
        para('独立方法权：包含步骤1)–5)并限定大模型输出“路由概率+资源效用+解释”、预算求解产出“等级/时序/TTL/淘汰”、SW动态调度与指标记录+反事实评估校准；独立系统权：对应模块化系统；并列介质/装置权；从属权要点：动态TTL、网络降级与取消、多标签页去重、反事实评估、端云蒸馏与灰度热更新。'),
        subheading('九、工业实用性'),
        para('适用于大规模Web前端，兼容主流框架与浏览器，部署成本低，收益稳定。'),
      ],
    }],
  });

  const buffer = await Packer.toBuffer(doc);
  fs.writeFileSync(outPath, buffer);
  console.log('Generated:', outPath);
}

main().catch(err => { console.error(err); process.exit(1); });