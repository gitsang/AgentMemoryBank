const { chromium } = require('playwright');
const { execSync } = require('child_process');
const path = require('path');

const VIDEO_DIR = __dirname;
const SLIDES_URL = `file://${path.join(VIDEO_DIR, 'slides.html')}`;
const FPS = 1;
const TOTAL_SEC = 7 * 27 + 5; // 7 slides * 27s + 5s buffer
const TOTAL_FRAMES = TOTAL_SEC * FPS;

(async () => {
  const browser = await chromium.launch({ headless: true });
  const page = await browser.newPage({ viewport: { width: 1280, height: 720 }, deviceScaleFactor: 2 });
  await page.goto(SLIDES_URL, { waitUntil: 'networkidle' });
  await page.waitForSelector('.slide.active');

  const frameDir = path.join(VIDEO_DIR, 'frames');
  execSync(`rm -rf "${frameDir}" && mkdir -p "${frameDir}"`);

  console.log(`Capturing ${TOTAL_FRAMES} frames at ${FPS} fps (${TOTAL_SEC}s)...`);
  const startTime = Date.now();

  for (let i = 0; i < TOTAL_FRAMES; i++) {
    await page.screenshot({
      path: path.join(frameDir, `f_${String(i).padStart(5, '0')}.png`),
      type: 'png',
    });
    await page.waitForTimeout(1000 / FPS);
    if (i % 10 === 0) process.stdout.write(`\rFrame ${i}/${TOTAL_FRAMES} (${Math.round((Date.now()-startTime)/1000)}s elapsed)`);
  }
  console.log(`\rFrame ${TOTAL_FRAMES}/${TOTAL_FRAMES} - Done in ${Math.round((Date.now()-startTime)/1000)}s`);

  await browser.close();

  // Build video from frames
  console.log('Encoding silent video...');
  execSync(
    `ffmpeg -y -framerate ${FPS} -i "${path.join(frameDir, 'f_%05d.png')}" ` +
    `-c:v libx264 -pix_fmt yuv420p -preset fast -crf 23 "${path.join(VIDEO_DIR, 'silent.mp4')}"`,
    { stdio: 'inherit', timeout: 120000 }
  );

  // Mux with audio
  console.log('Merging with audio...');
  execSync(
    `ffmpeg -y -i "${path.join(VIDEO_DIR, 'silent.mp4')}" ` +
    `-i "${path.join(VIDEO_DIR, 'voice.mp3')}" ` +
    `-c:v copy -c:a aac -shortest -map 0:v:0 -map 1:a:0 ` +
    `"${path.join(VIDEO_DIR, 'output.mp4')}"`,
    { stdio: 'inherit', timeout: 60000 }
  );

  // Cleanup frames
  execSync(`rm -rf "${frameDir}" "${path.join(VIDEO_DIR, 'silent.mp4')}"`);
  
  const outputPath = path.join(VIDEO_DIR, 'output.mp4');
  const size = require('fs').statSync(outputPath).size;
  console.log(`\n✅ Done! ${outputPath} (${(size/1024/1024).toFixed(1)}MB)`);
})().catch(err => { console.error(err); process.exit(1); });
