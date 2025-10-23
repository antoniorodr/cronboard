# Contributing

Thank you for your interest in contributing! Whether it's a bug report, new feature, or fixing a typo — we appreciate it.

All participation is governed by our [Code of Conduct](CODE_OF_CONDUCT.md).

Before contributing, please read through this document to understand how to get started and the `project explanation` file for context about the project. This file is located at [docs/project_explanation.md](docs/project_explanation.md).

## Ways to Contribute

- 🛠️ Make changes to code or docs (via PR)
- 🐞 Report bugs
- 💡 Suggest features
- 💬 Join discussions

## Development Setup

1. Fork the project and clone your fork:

    ```bash
    git clone https://github.com/antoniorodr/cronboard
    cd cronboard
    ```

2. Create a feature branch:

    ```bash
    git checkout -b my-feature
    ```

3. Set up the environment with [uv](https://github.com/astral-sh/uv):

    ```bash
    uv venv
    source .venv/bin/activate
    uv sync
    ```

4. (Optional) Uninstall Homebrew version of CronBoard:

    ```bash
    brew uninstall cronboard
    ```

5. Install the CLI locally in editable mode:

    ```bash
    uv tool install . -e
    ```

6. Run the tool:

    ```bash
    cronboard --help
    ```

7. (Optional) Uninstall local version when you are done:

    ```bash
    uv tool uninstall cronboard
    ```

## Testing

This project uses [pytest](https://docs.pytest.org/en/stable/) and [pytest-asyncio](https://pytest-asyncio.readthedocs.io/en/stable/) for testing. To run the tests:

```bash
pytest
```

To install this tool, run:

```bash
uv pip install pytest
uv pip install pytest-asyncio
```

or

```bash
pip install pytest
pip install pytest-asyncio
```

## Commit Style

Follow [Conventional Commits](https://www.conventionalcommits.org/) if possible:

```
feat: add export to JSON
fix: handle missing config
docs: improve usage section
```

## Submitting Pull Requests

1. Push your feature branch:

    ```bash
    git push origin my-feature
    ```

2. Open a pull request via GitHub’s web interface.

Refer to [GitHub’s PR Guide](https://docs.github.com/en/pull-requests/collaborating-with-pull-requests/proposing-changes-to-your-work-with-pull-requests/creating-a-pull-request) if you need help.

## Submitting Issues

Use GitHub Issues to report bugs or suggest features.
Use Discussions for open-ended ideas or proposals.

## License

All contributions will be licensed under the same license as the project.
