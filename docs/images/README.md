# Documentation images

The GIFs in this directory illustrate Cronboard’s UI in the docs (overview, create job, remote connect, search, interface overview).

## Current placeholders

The included `.gif` files are minimal placeholders so the docs build and links work. For a finished docs site, replace them with real screen recordings of the TUI.

## Recording real GIFs

1. **Run Cronboard** and perform the flow you want to record (e.g. open app, press `c`, fill create form, save).
2. **Record the terminal** with one of:
   - [asciinema](https://asciinema.org/) then convert to GIF (e.g. [asciinema-to-gif](https://github.com/asciinema/asciinema/wiki/Gifcasting), or [agg](https://github.com/asciinema/agg)).
   - [terminalizer](https://github.com/terminalizer/terminalizer) (record and export GIF).
   - [ttygif](https://github.com/icholy/ttygif) or similar.
3. **Save as** the corresponding filename: `overview.gif`, `create-job.gif`, `interface-overview.gif`, `remote-connect.gif`, `search.gif`.
4. **Keep file size reasonable** (e.g. under 2–3 MB per GIF): short clips, lower resolution or frame rate, and compress (e.g. [gifsicle](https://www.lcdf.org/gifsicle/) `--optimize`).

Replace the placeholder files in this directory and run `zensical build --clean` to confirm the docs still build.
