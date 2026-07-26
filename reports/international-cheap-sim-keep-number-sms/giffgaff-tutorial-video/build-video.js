#!/usr/bin/env node
/**
 * Giffgaff Tutorial Video Generator
 *
 * Pipeline:
 *   1. edge-tts  →  narration.mp3 (single merged audio)
 *   2. Playwright →  silent-video.webm (slideshow captured from HTML)
 *   3. ffmpeg     →  output.mp4 (video + audio merged)
 */

const { chromium } = require('playwright');
const { execSync, spawn } = require('child_process');
const path = require('path');
const fs = require('fs');

const PROJECT_DIR = __dirname;
const HTML_FILE = path.join(PROJECT_DIR, 'animation.html');
const NARRATION_TXT = path.join(PROJECT_DIR, 'narration.txt');
const TTS_AUDIO = path.join(PROJECT_DIR, 'narration.mp3');
const RAW_VIDEO = path.join(PROJECT_DIR, 'silent-video.webm');
const OUTPUT_VIDEO = path.join(PROJECT_DIR, 'giffgaff-tutorial.mp4');

// ─── helpers ───────────────────────────────────────────────
function run(cmd, opts = {}) {
  console.log(`  → ${cmd}`);
  execSync(cmd, { stdio: 'inherit', ...opts });
}

async function sleep(ms) {
  return new Promise(r => setTimeout(r, ms));
}

// ─── Step 1: edge-tts ──────────────────────────────────────
async function generateTTS() {
  console.log('\n🔊 [1/3] Generating TTS narration with edge-tts...');
  const narration = fs.readFileSync(NARRATION_TXT, 'utf-8');

  // edge-tts: write text to temp file, generate audio
  const tmpText = path.join(PROJECT_DIR, '.narration-tmp.txt');
  fs.writeFileSync(tmpText, narration);

  run(
    `edge-tts --voice zh-CN-XiaoxiaoNeural --rate=+5% --pitch=+5Hz -f "${tmpText}" --write-media "${TTS_AUDIO}"`,
    { timeout: 60_000 }
  );

  fs.unlinkSync(tmpText);

  // Get audio duration
  const dur = execSync(
    `ffprobe -v error -show_entries format=duration -of default=noprint_wrappers=1:nokey=1 "${TTS_AUDIO}"`,
    { encoding: 'utf-8' }
  ).trim();
  const durationSec = parseFloat(dur);
  console.log(`  ✅ TTS generated: ${durationSec.toFixed(1)}s`);
  return durationSec;
}

// ─── Step 2: Playwright record video ────────────────────────
async function recordSlideshow(totalDurationSec) {
  console.log('\n🎥 [2/3] Recording HTML slideshow with Playwright...');

  const browser = await chromium.launch({
    headless: true,
    args: ['--autoplay-policy=no-user-gesture-required'],
  });

  const context = await browser.newContext({
    viewport: { width: 1080, height: 1920 },
    recordVideo: {
      dir: PROJECT_DIR,
      size: { width: 1080, height: 1920 },
    },
  });

  const page = await context.newPage();
  await page.goto(`file://${HTML_FILE}`, { waitUntil: 'networkidle' });

  // Wait for the slideshow to complete (add buffer)
  const waitMs = (totalDurationSec + 2) * 1000;
  console.log(`  Recording for ${(waitMs / 1000).toFixed(0)}s...`);
  await sleep(waitMs);

  await context.close();
  await browser.close();

  // Find the recorded video file (Playwright names it *.webm)
  const files = fs.readdirSync(PROJECT_DIR).filter(f => f.endsWith('.webm'));
  if (files.length === 0) {
    // Playwright may put it in a subdirectory or name it differently
    const allFiles = fs.readdirSync(PROJECT_DIR);
    console.log('  All files in dir:', allFiles);
    throw new Error('No .webm video file found after recording');
  }

  const recordedFile = path.join(PROJECT_DIR, files[0]);
  if (recordedFile !== RAW_VIDEO) {
    fs.renameSync(recordedFile, RAW_VIDEO);
  }
  console.log(`  ✅ Video recorded: ${RAW_VIDEO}`);
}

// ─── Step 3: ffmpeg merge ───────────────────────────────────
function mergeVideoAudio() {
  console.log('\n🎬 [3/3] Merging video + audio with ffmpeg...');
  run(
    `ffmpeg -y -i "${RAW_VIDEO}" -i "${TTS_AUDIO}" -c:v libx264 -preset fast -crf 23 -c:a aac -b:a 128k -shortest -pix_fmt yuv420p "${OUTPUT_VIDEO}"`,
    { timeout: 120_000 }
  );
  console.log(`  ✅ Output: ${OUTPUT_VIDEO}`);

  const stat = fs.statSync(OUTPUT_VIDEO);
  console.log(`  📦 Size: ${(stat.size / 1024 / 1024).toFixed(1)} MB`);
}

// ─── main ───────────────────────────────────────────────────
(async () => {
  console.log('🎬 Giffgaff Tutorial Video Generator');
  console.log('═══════════════════════════════════\n');

  try {
    const audioDuration = await generateTTS();
    await recordSlideshow(audioDuration);
    mergeVideoAudio();

    // Clean up raw video
    if (fs.existsSync(RAW_VIDEO)) {
      fs.unlinkSync(RAW_VIDEO);
      console.log('  🧹 Cleaned up silent video');
    }

    console.log('\n✨ Done! Output: ' + OUTPUT_VIDEO);
  } catch (err) {
    console.error('\n❌ Error:', err.message);
    process.exit(1);
  }
})();
