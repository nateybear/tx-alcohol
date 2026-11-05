# Building

This project uses the [Astral](https://astral.sh/) ecosystem of Python tools (uv, ruff, and ty), so make sure you have them installed.

On first download, run `uv sync` to bootstrap your environment and load all of the necessary packages

The build system is Snakemake, and you can view the `Snakefile` to see the build tasks

In VSCode, it is configured as the default build task, so you can hit Cmd+Shift+B to build the project. (Note: there are API keys and routing files that are not checked into GitHub, so you will need to get those from me first to build.)

# Output

Right now, the project is to use density-based clustering on drive times to create markets of restaurants that people would reasonable drive between. See, e.g., this snapshot of restaurants in Houston where markets tend to be defined along highways rather than Euclidean distance:

<img width="654" height="470" alt="Screenshot 2026-11-05 at 9 42 42 AM" src="https://github.com/user-attachments/assets/3a6cfe88-e77e-474d-af8f-c6fd01113cb6" />
