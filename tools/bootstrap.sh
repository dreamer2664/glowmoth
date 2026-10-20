#!/usr/bin/env bash
# bootstrap.sh — 90 seconds to a working sandbox. Run FIRST, every session.
# Idempotent: safe to re-run. Prints a capability profile the agent should
# paste into its first checkpoint (evidence of what the box can do).
set -uo pipefail

echo "== sandbox bootstrap $(date -u +%FT%TZ) =="
echo "cores: $(nproc) · ram: $(free -m | awk '/Mem:/{print $7"MB avail"}') · disk: $(df -h /home | awk 'NR==2{print $4" free"}')"

# 1. tools the work loop needs (ffmpeg for media; time for RSS measurement; blender only if the job needs it)
NEED=""
for t in ffmpeg time; do command -v $t >/dev/null || NEED="$NEED $t"; done
if [ "${WITH_BLENDER:-0}" = "1" ] && ! command -v blender >/dev/null; then NEED="$NEED blender"; fi
if [ -n "$NEED" ]; then
  echo "installing:$NEED"
  sudo -n apt-get update -qq >/dev/null 2>&1
  sudo -n apt-get install -y --no-install-recommends $NEED >/dev/null 2>&1 \
    && echo "install: OK" || echo "install: FAILED (apt unavailable — adapt)"
fi

# 2. memory doctrine: never let one process eat the box (no swap here — OOM is instant death)
echo "mem ceiling: ${MEM_CEILING_MB:-1200}MB per process (no swap; OOM kills are silent)"
echo "scratch: use /tmp for intermediates (tmpfs ~1GB, dies with the session)"
echo "persistence: ONLY pushed git survives. checkpoint every phase."

# 3. capability profile — this IS evidence; paste into the first checkpoint
cat <<EOF
-- profile --
python $(python3 --version | cut -d' ' -f2) · node $(node --version) · ffmpeg $(ffmpeg -version 2>/dev/null | head -1 | cut -d' ' -f3 || echo none)
blender: $(blender --version 2>/dev/null | head -1 | cut -d' ' -f2 || echo 'not installed (WITH_BLENDER=1 to add)')
known traps: Debian blender has NO OpenImageDenoise -> sc.cycles.use_denoising = False
             subsurf+high object counts OOM at ~2GB (200x subsurf2 dies; 1x1080p Cycles 32spp ~176MB ok)
             /usr/bin/time needs the 'time' package
EOF
