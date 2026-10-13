"""Render the receptionist demo call (SAMPLE, fictional) to call.mp3 + call.json (line timings). The timings are
inlined into index.html (var CALL); after a re-render, paste the new call.json there and delete the file.

Same Kokoro path as tle-main/products/video-audit/voice.py: KPipeline(lang_code='a') and brand/pronounce.yaml
applied right before TTS (captions keep the normal spelling). Agent = af_heart, caller = am_michael.

    cd ~/fable-films/tools && uv run python ~/autoants-site-demo-b/demo/receptionist/make_audio.py
"""
import json, pathlib, subprocess, sys
import numpy as np, soundfile as sf
from kokoro import KPipeline

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(pathlib.Path.home() / "tle-main" / "brand"))
import pronounce  # noqa: E402

VOICE = {"agent": "af_heart", "caller": "am_michael"}
SR = 24000
# who, transcript text, spoken text (only where it differs: phone numbers read the way people say them)
LINES = [
    ("agent", "Thanks for calling Sample Foundation Repair. I'm an AI assistant, and this call is recorded. I can take down your job request, and Marcus reviews every request personally. What's going on?"),
    ("caller", "Hi. My floors started sloping toward the back of the house, and two doors are sticking."),
    ("agent", "I'm sorry you're dealing with that. Can I get your name, the address, and a good number for you?"),
    ("caller", "It's Dan. 4100 Example Street, Uptown, in New Orleans. My number's 504-555-0142.",
     "It's Dan. Forty-one hundred Example Street, Uptown, in New Orleans. My number's five oh four, five five five, oh one four two."),
    ("agent", "Thanks, Dan. That's 504-555-0142. Is anything else going on with the house?",
     "Thanks, Dan. That's five oh four, five five five, oh one four two. Is anything else going on with the house?"),
    ("caller", "Well, since the floor shifted, I sometimes smell gas near the stove."),
    ("agent", "If you smell gas or see sparking or a collapse, please get everyone out of the house and call 911 first. Are you somewhere safe right now?",
     "If you smell gas or see sparking or a collapse, please get everyone out of the house and call nine one one first. Are you somewhere safe right now?"),
    ("caller", "Yeah, we're stepping outside now. I'll call them."),
    ("agent", "I've marked this urgent for Marcus. For the foundation, he could come take a look Tuesday at 2 PM or Wednesday at 10 AM. Which works better?",
     "I've marked this urgent for Marcus. For the foundation, he could come take a look Tuesday at two P M, or Wednesday at ten A M. Which works better?"),
    ("caller", "Tuesday at two."),
    ("agent", "I have you down for Tuesday at 2 PM. Marcus confirms every visit by text, so watch for that. Is it okay to text you at this number about this job?",
     "I have you down for Tuesday at two P M. Marcus confirms every visit by text, so watch for that. Is it okay to text you at this number about this job?"),
    ("caller", "Yes, that's fine."),
    ("agent", "Thanks, Dan. Please stay outside until the gas is checked. Goodbye."),
]
GAP = {"agent": 0.35, "caller": 0.45}   # pause before each line: who's starting to talk

pipe = KPipeline(lang_code="a")
chunks, timing, t = [], [], 0.4
chunks.append(np.zeros(int(SR * 0.4), dtype=np.float32))
for i, row in enumerate(LINES):
    who, text = row[0], row[1]
    spoken = row[2] if len(row) > 2 else text
    audio = np.concatenate([r.audio.numpy() if hasattr(r.audio, "numpy") else r.audio
                            for r in pipe(pronounce.apply(spoken, "a"), voice=VOICE[who], speed=1.06)]).astype(np.float32)
    if i:
        gap = np.zeros(int(SR * GAP[who]), dtype=np.float32)
        chunks.append(gap); t += len(gap) / SR
    timing.append({"who": who, "text": text, "start": round(t, 2), "end": round(t + len(audio) / SR, 2)})
    chunks.append(audio); t += len(audio) / SR
chunks.append(np.zeros(int(SR * 0.3), dtype=np.float32))
mix = np.concatenate(chunks)
mix = mix / max(1e-6, float(np.abs(mix).max())) * 0.89
wav = HERE / "_call.wav"
sf.write(wav, mix, SR)
mp3 = HERE / "call.mp3"
subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", str(wav), "-ac", "1", "-ar", "24000",
                "-c:a", "libmp3lame", "-b:a", "64k", str(mp3)], check=True)
wav.unlink()
(HERE / "call.json").write_text(json.dumps({"seconds": round(len(mix) / SR, 2), "lines": timing}, indent=1))
print(f"{mp3.name}: {mp3.stat().st_size/1024:.0f} KB, {len(mix)/SR:.1f} s, {len(timing)} lines")
