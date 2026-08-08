#!/usr/bin/env bash
# Build FFmpeg 8.1 + common codecs + NVENC/NVDEC
# Workspace: /tmp/$USER/ffmpeg
# Install prefix: /sw/pkgs/coe/o/ffmpeg/8.1.0 (change IDIR if needed)

set -euo pipefail
IFS=$'\n\t'
trap 'echo "ERROR on line $LINENO: $BASH_COMMAND" >&2' ERR
shopt -s nullglob

JOBS="${JOBS:-8}"

# ---------------------------------------------------------------
# Environment Setup
# ---------------------------------------------------------------
# Prevent "unbound variable" in sourced scripts under set -u
export LD_LIBRARY_PATH="${LD_LIBRARY_PATH:-}"
export PKG_CONFIG_PATH="${PKG_CONFIG_PATH:-}"
export PATH="${PATH:-}"

# Optional site environment (keep if you need it)
if [[ -f /sw/pkgs/coe/o/libimage/220318/source.bash ]]; then
  # shellcheck disable=SC1091
  source /sw/pkgs/coe/o/libimage/220318/source.bash
fi

# Modules (if available)
if command -v module &>/dev/null; then
  module load cuda/12.3.0 || true
  module add cmake        || true
fi

# CUDA_HOME detection
if [[ -z "${CUDA_HOME:-}" ]] && command -v nvcc &>/dev/null; then
  CUDA_HOME="$(dirname "$(dirname "$(command -v nvcc)")")"
  export CUDA_HOME
fi
echo "CUDA_HOME: ${CUDA_HOME:-<not set>}"

export MAIN_VER="8.1"
export IDIR="/sw/pkgs/coe/o/ffmpeg/8.1.0"
export PREFIX="$IDIR"
export DOCDIR="$IDIR/docs"

# NASM (adjust/remove if not needed)
export PATH="/sw/pkgs/coe/o/nasm/2.15.05/bin:$PATH"

# Workspace (NO /sw/src)
export TDIR="/tmp/${USER}/ffmpeg"
mkdir -p "$TDIR"
cd "$TDIR"

# Install prefix layout
mkdir -p "$IDIR" "$IDIR/lib" "$IDIR/include" "$IDIR/bin" "$DOCDIR"
[[ -L "$IDIR/lib64" ]] || ln -sfn lib "$IDIR/lib64"

# Prefer our prefix headers/libs when building
export PATH="$IDIR/bin:$PATH"
export LD_LIBRARY_PATH="$IDIR/lib:$LD_LIBRARY_PATH"
export PKG_CONFIG_PATH="$IDIR/lib/pkgconfig:$PKG_CONFIG_PATH"
export CPPFLAGS="-I$IDIR/include ${CPPFLAGS:-}"
export CFLAGS="-I$IDIR/include ${CFLAGS:-}"
export CXXFLAGS="-I$IDIR/include ${CXXFLAGS:-}"
export LDFLAGS="-L$IDIR/lib ${LDFLAGS:-}"

# ---------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------
wget_if_missing () {
  local url="$1"
  local file
  file="$(basename "${url%%\?*}")"   # drop any ?query=...
  [[ -e "$file" ]] || wget -O "$file" "$url"
}

# SIGPIPE-safe under set -e + pipefail + ERR trap
extract_topdir () {
  local tf="$1"
  local first
  set +o pipefail
  first="$(tar -tf "$tf" 2>/dev/null | head -n 1 || true)"
  set -o pipefail
  printf '%s\n' "${first%%/*}"
}

pick_tarball () {
  # Usage: pick_tarball VAR_NAME pattern1 pattern2 ...
  # Sets VAR_NAME to the first matching file (full path), or empty if none.
  local __var="$1"; shift
  local matches=()
  local p
  for p in "$@"; do
    matches+=( $p )
  done
  if (( ${#matches[@]} == 0 )); then
    printf -v "$__var" '%s' ""
  else
    printf -v "$__var" '%s' "${matches[0]}"
  fi
}

unpack_to_tdir () {
  local tf="$1"
  local top
  top="$(extract_topdir "$tf")"
  [[ -n "$top" ]] || { echo "ERROR: could not determine top dir from $tf" >&2; exit 1; }
  rm -rf "$TDIR/$top"
  tar -xf "$tf" -C "$TDIR"
  printf '%s\n' "$top"
}

run_make_install () {
  local name="$1"
  make -j"${JOBS}" 2>&1 | tee "$TDIR/${name}-make.log"
  make install      2>&1 | tee "$TDIR/${name}-install.log"
}

# ---------------------------------------------------------------
# Download tarballs (saved into $TDIR)
# ---------------------------------------------------------------
wget_if_missing "https://www.ffmpeg.org/releases/ffmpeg-${MAIN_VER}.tar.xz"
wget_if_missing "https://github.com/FFmpeg/nv-codec-headers/releases/download/n12.2.72.0/nv-codec-headers-12.2.72.0.tar.gz"
wget_if_missing "https://anduin.linuxfromscratch.org/BLFS/x264/x264-20240812.tar.xz"
wget_if_missing "https://bitbucket.org/multicoreware/x265_git/downloads/x265_3.6.tar.gz"
wget_if_missing "https://downloads.sourceforge.net/opencore-amr/fdk-aac-2.0.3.tar.gz"
wget_if_missing "https://downloads.sourceforge.net/lame/lame-3.100.tar.gz"
wget_if_missing "https://downloads.xiph.org/releases/opus/opus-1.5.2.tar.gz"
wget_if_missing "https://github.com/webmproject/libvpx/archive/v1.14.1/libvpx-1.14.1.tar.gz"
wget_if_missing "https://downloads.xiph.org/releases/ogg/libogg-1.3.5.tar.xz"
wget_if_missing "https://downloads.xiph.org/releases/vorbis/libvorbis-1.3.7.tar.xz"
wget_if_missing "https://downloads.xiph.org/releases/theora/libtheora-1.1.1.tar.xz"
wget_if_missing "https://github.com/libass/libass/releases/download/0.17.3/libass-0.17.3.tar.xz"
wget_if_missing "https://downloads.xiph.org/releases/speex/speex-1.2.1.tar.gz"
wget_if_missing "https://downloads.xiph.org/releases/speex/speexdsp-1.2.1.tar.gz"
wget_if_missing "https://downloads.sourceforge.net/freetype/freetype-2.13.3.tar.xz"

# ---------------------------------------------------------------
# Build x264
# ---------------------------------------------------------------
echo "==============================================================="
echo "Build x264"
TF=""
pick_tarball TF "$TDIR"/x264-*.tar.xz "$TDIR"/x264-*.tar.gz "$TDIR"/x264-*.tar.bz2 "$TDIR"/x264-*.tgz
[[ -n "$TF" ]] || { echo "ERROR: x264 tarball not found in $TDIR" >&2; ls -lah "$TDIR" >&2; exit 1; }
echo "Using: $TF"
PKGDIR="$(unpack_to_tdir "$TF")"
cd "$TDIR/$PKGDIR"
./configure --prefix="$IDIR" --enable-static --enable-shared 2>&1 | tee "$TDIR/x264-config.log"
run_make_install "x264"
cd "$TDIR"

# ---------------------------------------------------------------
# Build x265
# ---------------------------------------------------------------
echo "==============================================================="
echo "Build x265"
TF=""
pick_tarball TF "$TDIR"/x265_*.tar.xz "$TDIR"/x265_*.tar.gz "$TDIR"/x265-*.tar.xz "$TDIR"/x265-*.tar.gz
[[ -n "$TF" ]] || { echo "ERROR: x265 tarball not found in $TDIR" >&2; exit 1; }
echo "Using: $TF"
PKGDIR="$(unpack_to_tdir "$TF")"
cd "$TDIR/$PKGDIR"
mkdir -p build/linux
cd build/linux
cmake -G "Unix Makefiles" \
  -DCMAKE_INSTALL_PREFIX="$IDIR" \
  -DENABLE_SHARED=ON \
  ../../source 2>&1 | tee "$TDIR/x265-config.log"
make -j"${JOBS}" 2>&1 | tee "$TDIR/x265-make.log"
make install      2>&1 | tee "$TDIR/x265-install.log"
cd "$TDIR"

# ---------------------------------------------------------------
# Build fdk-aac
# ---------------------------------------------------------------
echo "==============================================================="
echo "Build fdk-aac"
TF=""
pick_tarball TF "$TDIR"/fdk-aac-*.tar.gz "$TDIR"/fdk-aac-*.tar.xz
[[ -n "$TF" ]] || { echo "ERROR: fdk-aac tarball not found in $TDIR" >&2; exit 1; }
PKGDIR="$(unpack_to_tdir "$TF")"
cd "$TDIR/$PKGDIR"
./configure --prefix="$IDIR" --enable-static --enable-shared 2>&1 | tee "$TDIR/fdk-aac-config.log"
run_make_install "fdk-aac"
cd "$TDIR"

# ---------------------------------------------------------------
# Build freetype
# ---------------------------------------------------------------
echo "==============================================================="
echo "Build freetype"
TF=""
pick_tarball TF "$TDIR"/freetype-*.tar.xz "$TDIR"/freetype-*.tar.gz
[[ -n "$TF" ]] || { echo "ERROR: freetype tarball not found in $TDIR" >&2; exit 1; }
PKGDIR="$(unpack_to_tdir "$TF")"
cd "$TDIR/$PKGDIR"
./configure --prefix="$IDIR" --enable-static --enable-shared 2>&1 | tee "$TDIR/freetype-config.log"
run_make_install "freetype"
cd "$TDIR"

# ---------------------------------------------------------------
# Build libass
# ---------------------------------------------------------------
echo "==============================================================="
echo "Build libass"
TF=""
pick_tarball TF "$TDIR"/libass-*.tar.xz "$TDIR"/libass-*.tar.gz
[[ -n "$TF" ]] || { echo "ERROR: libass tarball not found in $TDIR" >&2; exit 1; }
PKGDIR="$(unpack_to_tdir "$TF")"
cd "$TDIR/$PKGDIR"
./configure --prefix="$IDIR" --enable-static --enable-shared 2>&1 | tee "$TDIR/libass-config.log"
run_make_install "libass"
cd "$TDIR"

# ---------------------------------------------------------------
# Build lame
# ---------------------------------------------------------------
echo "==============================================================="
echo "Build lame"
TF=""
pick_tarball TF "$TDIR"/lame-*.tar.gz "$TDIR"/lame-*.tar.xz
[[ -n "$TF" ]] || { echo "ERROR: lame tarball not found in $TDIR" >&2; exit 1; }
PKGDIR="$(unpack_to_tdir "$TF")"
cd "$TDIR/$PKGDIR"
./configure --prefix="$IDIR" --enable-nasm --enable-static --enable-shared 2>&1 | tee "$TDIR/lame-config.log"
run_make_install "lame"
cd "$TDIR"

# ---------------------------------------------------------------
# Build opus
# ---------------------------------------------------------------
echo "==============================================================="
echo "Build opus"
TF=""
pick_tarball TF "$TDIR"/opus-*.tar.gz "$TDIR"/opus-*.tar.xz
[[ -n "$TF" ]] || { echo "ERROR: opus tarball not found in $TDIR" >&2; exit 1; }
PKGDIR="$(unpack_to_tdir "$TF")"
cd "$TDIR/$PKGDIR"
./configure --prefix="$IDIR" --docdir="$DOCDIR" --enable-static --enable-shared 2>&1 | tee "$TDIR/opus-config.log"
run_make_install "opus"
cd "$TDIR"

# ---------------------------------------------------------------
# Build libogg
# ---------------------------------------------------------------
echo "==============================================================="
echo "Build libogg"
TF=""
pick_tarball TF "$TDIR"/libogg-*.tar.xz "$TDIR"/libogg-*.tar.gz
[[ -n "$TF" ]] || { echo "ERROR: libogg tarball not found in $TDIR" >&2; exit 1; }
PKGDIR="$(unpack_to_tdir "$TF")"
cd "$TDIR/$PKGDIR"
./configure --prefix="$IDIR" --enable-static --enable-shared 2>&1 | tee "$TDIR/libogg-config.log"
run_make_install "libogg"
cd "$TDIR"

# ---------------------------------------------------------------
# Build speex (not speexdsp)
# ---------------------------------------------------------------
echo "==============================================================="
echo "Build speex"
speex_candidates=("$TDIR"/speex-*.tar.gz "$TDIR"/speex-*.tar.xz)
TF=""
for f in "${speex_candidates[@]}"; do
  [[ "$f" == *speexdsp* ]] && continue
  TF="$f"
  break
done
[[ -n "$TF" ]] || { echo "ERROR: speex tarball not found in $TDIR" >&2; exit 1; }
PKGDIR="$(unpack_to_tdir "$TF")"
cd "$TDIR/$PKGDIR"
./configure --prefix="$IDIR" --enable-static --enable-shared 2>&1 | tee "$TDIR/speex-config.log"
run_make_install "speex"
cd "$TDIR"

# ---------------------------------------------------------------
# Build speexdsp
# ---------------------------------------------------------------
echo "==============================================================="
echo "Build speexdsp"
TF=""
pick_tarball TF "$TDIR"/speexdsp-*.tar.gz "$TDIR"/speexdsp-*.tar.xz
[[ -n "$TF" ]] || { echo "ERROR: speexdsp tarball not found in $TDIR" >&2; exit 1; }
PKGDIR="$(unpack_to_tdir "$TF")"
cd "$TDIR/$PKGDIR"
./configure --prefix="$IDIR" --enable-static --enable-shared 2>&1 | tee "$TDIR/speexdsp-config.log"
run_make_install "speexdsp"
cd "$TDIR"

# ---------------------------------------------------------------
# Build libvorbis
# ---------------------------------------------------------------
echo "==============================================================="
echo "Build libvorbis"
TF=""
pick_tarball TF "$TDIR"/libvorbis-*.tar.xz "$TDIR"/libvorbis-*.tar.gz
[[ -n "$TF" ]] || { echo "ERROR: libvorbis tarball not found in $TDIR" >&2; exit 1; }
PKGDIR="$(unpack_to_tdir "$TF")"
cd "$TDIR/$PKGDIR"
./configure --prefix="$IDIR" --enable-static --enable-shared --with-ogg="$IDIR" 2>&1 | tee "$TDIR/libvorbis-config.log"
run_make_install "libvorbis"
cd "$TDIR"

# ---------------------------------------------------------------
# Build libvpx
# ---------------------------------------------------------------
echo "==============================================================="
echo "Build libvpx"
TF=""
pick_tarball TF "$TDIR"/libvpx-*.tar.gz "$TDIR"/libvpx-*.tar.xz
[[ -n "$TF" ]] || { echo "ERROR: libvpx tarball not found in $TDIR" >&2; exit 1; }
PKGDIR="$(unpack_to_tdir "$TF")"
cd "$TDIR/$PKGDIR"
./configure --prefix="$IDIR" --disable-examples --enable-static --enable-shared 2>&1 | tee "$TDIR/libvpx-config.log"
run_make_install "libvpx"
cd "$TDIR"

# ---------------------------------------------------------------
# Build libtheora
# ---------------------------------------------------------------
echo "==============================================================="
echo "Build libtheora"
TF=""
pick_tarball TF "$TDIR"/libtheora-*.tar.xz "$TDIR"/libtheora-*.tar.gz
[[ -n "$TF" ]] || { echo "ERROR: libtheora tarball not found in $TDIR" >&2; exit 1; }
PKGDIR="$(unpack_to_tdir "$TF")"
cd "$TDIR/$PKGDIR"
sed -i 's/png_<math><mrow><mi>s</mi><mi>i</mi><mi>z</mi><mi>e</mi><mi>o</mi><mi>f</mi></mrow></math>/\1/g' examples/png2theora.c || true
./configure --prefix="$IDIR" \
  --with-ogg="$IDIR" \
  --enable-static --enable-shared \
  --disable-examples \
  2>&1 | tee "$TDIR/libtheora-config.log"
run_make_install "libtheora"
cd "$TDIR"

# ---------------------------------------------------------------
# Build nv-codec-headers
# ---------------------------------------------------------------
echo "==============================================================="
echo "Build nv-codec-headers"
TF=""
pick_tarball TF "$TDIR"/nv-codec-headers-*.tar.gz "$TDIR"/nv-codec-headers-*.tar.xz
[[ -n "$TF" ]] || { echo "ERROR: nv-codec-headers tarball not found in $TDIR" >&2; exit 1; }
PKGDIR="$(unpack_to_tdir "$TF")"
cd "$TDIR/$PKGDIR"
make -j"${JOBS}" PREFIX="$IDIR" 2>&1 | tee "$TDIR/nv-codec-headers-make.log"
make install PREFIX="$IDIR"      2>&1 | tee "$TDIR/nv-codec-headers-install.log"
cd "$TDIR"

# ---------------------------------------------------------------
# Build FFmpeg 8.1 with NVENC/NVDEC
# ---------------------------------------------------------------
echo "==============================================================="
echo "Build FFmpeg ${MAIN_VER} (NVENC/NVDEC)"
TF="$TDIR/ffmpeg-${MAIN_VER}.tar.xz"
[[ -e "$TF" ]] || { echo "ERROR: $TF not found" >&2; exit 1; }
PKGDIR="ffmpeg-${MAIN_VER}"
rm -rf "$TDIR/$PKGDIR"
tar -xf "$TF" -C "$TDIR"
cd "$TDIR/$PKGDIR"

CUDA_NVCC_FLAG=()
if command -v nvcc &>/dev/null; then
  CUDA_NVCC_FLAG+=(--enable-cuda-nvcc)
fi

./configure --prefix="$IDIR" \
  --extra-cflags="-I$IDIR/include ${CUDA_HOME:+-I$CUDA_HOME/include}" \
  --extra-ldflags="-L$IDIR/lib ${CUDA_HOME:+-L$CUDA_HOME/lib64}" \
  --enable-gpl \
  --enable-version3 \
  --enable-nonfree \
  --enable-shared \
  --disable-debug \
  --enable-libass \
  --enable-libfdk-aac \
  --enable-libfreetype \
  --enable-libmp3lame \
  --enable-libopus \
  --enable-libtheora \
  --enable-libvorbis \
  --enable-libvpx \
  --enable-libx264 \
  --enable-libx265 \
  --enable-openssl \
  --enable-nvenc \
  --enable-nvdec \
  --enable-ffnvcodec \
  "${CUDA_NVCC_FLAG[@]}" \
  --docdir="$DOCDIR/ffmpeg" \
  2>&1 | tee "$TDIR/ffmpeg-config.log"

make -j"${JOBS}" 2>&1 | tee "$TDIR/ffmpeg-make.log"
make install      2>&1 | tee "$TDIR/ffmpeg-install.log"

if [[ -f tools/qt-faststart.c ]]; then
  gcc tools/qt-faststart.c -o tools/qt-faststart 2>&1 | tee -a "$TDIR/ffmpeg-make.log"
  install -v -m755 tools/qt-faststart "$IDIR/bin/"
fi

cd "$TDIR"

echo "==============================================================="
echo "Done!"
echo "Workspace: $TDIR"
echo "Verify:"
echo "  $IDIR/bin/ffmpeg -version"
echo "  $IDIR/bin/ffmpeg -encoders | grep -E 'nvenc|nvdec' || true"
echo "==============================================================="