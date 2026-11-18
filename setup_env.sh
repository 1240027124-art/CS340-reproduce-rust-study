#!/bin/bash
set -e

echo "===== Install system dependencies ====="
sudo apt update
sudo apt install -y build-essential curl git python3 python3-pip python3-dev

echo "===== Install Rust toolchain ====="
# rustup non-interactive install
curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh -s -- -y
# load rust env
source "$HOME/.cargo/env"

echo "===== Verify installation ====="
rustc --version
cargo --version
python3 --version

echo "===== Environment setup finished ====="
echo "Please source ~/.bashrc or reopen terminal to activate rust environment."
