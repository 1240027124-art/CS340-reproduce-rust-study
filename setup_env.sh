#!/bin/bash
set -e

NIGHTLY_VERSION="nightly-2026-11-19"

if ! command -v sudo &> /dev/null
then
    apt update
    apt install -y sudo
fi

echo "===== Install system dependencies ====="
sudo apt update
sudo apt install -y build-essential curl git python3 python3-pip python3-dev

echo "===== Install Rust toolchain (Pinned Version: $NIGHTLY_VERSION) ====="
if ! command -v rustup &> /dev/null; then
    curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh -s -- -y
    source "$HOME/.cargo/env"
else
    echo "rustup already installed."
fi

rustup toolchain install ${NIGHTLY_VERSION} --component miri

echo "===== Verify installation ====="
cargo +${NIGHTLY_VERSION} miri --version
echo "Miri is successfully installed and verified."

echo "===== Environment setup finished ====="
echo "Note: To run the experiments, always use the pinned nightly toolchain."
echo "e.g., cargo +${NIGHTLY_VERSION} miri run"
