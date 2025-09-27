import sharp from 'sharp';
import fs from 'fs';

const items = [
  { in: '/workspace/docs/patent/pro-diagrams/pro-fig1-arch.svg', out: '/workspace/docs/patent/pro-diagrams/pro-fig1-arch.png', width: 2400 },
  { in: '/workspace/docs/patent/pro-diagrams/pro-fig1-layered-arch.svg', out: '/workspace/docs/patent/pro-diagrams/pro-fig1-layered-arch.png', width: 2600 },
  { in: '/workspace/docs/patent/pro-diagrams/pro-fig2-flow.svg', out: '/workspace/docs/patent/pro-diagrams/pro-fig2-flow.png', width: 2400 },
  { in: '/workspace/docs/patent/pro-diagrams/pro-fig3-seq.svg', out: '/workspace/docs/patent/pro-diagrams/pro-fig3-seq.png', width: 2800 },
  { in: '/workspace/docs/patent/pro-diagrams/pro-fig4-exception.svg', out: '/workspace/docs/patent/pro-diagrams/pro-fig4-exception.png', width: 2200 },
  { in: '/workspace/docs/patent/pro-diagrams/pro-fig5-classes.svg', out: '/workspace/docs/patent/pro-diagrams/pro-fig5-classes.png', width: 2400 },
];

async function run() {
  for (const it of items) {
    const svg = fs.readFileSync(it.in);
    const png = await sharp(svg).png({ quality: 95 }).resize({ width: it.width }).toBuffer();
    fs.writeFileSync(it.out, png);
    console.log('Exported', it.out);
  }
}

run().catch(err => { console.error(err); process.exit(1); });