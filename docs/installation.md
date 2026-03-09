# Installation

Before installing Cronboard, make sure `cron` is available on your machine:

```bash
crontab -l
```

If this command returns an error saying `cron` is not installed, install it through your system's package manager first.

---

## Homebrew (macOS / Linux)

```bash
brew install cronboard
```

---

## uv

```bash
uv tool install git+https://github.com/antoniorodr/cronboard
```

---

## AUR (Arch Linux)

```bash
yay -S cronboard
```

---

## Nix

```bash
nix profile add github:antoniorodr/cronboard
```

---

## Manual (from source)

```bash
git clone https://github.com/antoniorodr/cronboard
cd cronboard
pip install .
```
