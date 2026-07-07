# Intro + Setup

## Install/setup:

* [Python](https://www.python.org/downloads/)
* [VS Code](https://code.visualstudio.com/download?_exp_download=d53503e735)
* [VS Code extensions](https://marketplace.visualstudio.com/vscode): [Python](https://marketplace.visualstudio.com/items?itemName=ms-python.python), [Pylance](https://marketplace.visualstudio.com/items?itemName=ms-python.vscode-pylance), [Jupyter](https://marketplace.visualstudio.com/items?itemName=ms-toolsai.jupyter)
* [Git](https://git-scm.com/install/)
* [GitHub account](https://github.com/login)
* [UV package manager](https://docs.astral.sh/uv/getting-started/installation/#standalone-installer)
* [Grok cloud API](https://console.groq.com/login)
* [Qdrant cloud/vector database](https://qdrant.tech/)


### Verify required installations

```bash
python --version
uv --version
git --version
code --version
```

### Git Setup

Verify installation:

```bash
git --version
```

Configure Git identity:

```bash
git config --global user.name "Your Name"
git config --global user.email "your@email.com"
```

Verify:

```bash
git config --global --list
```

### Grok Cloud API

1. Create a Grok cloud account.
2. Generate an API key.
3. Save the key securely.

### Qdrant Setup

1. Create a free Qdrant cluster.
2. Copy:
- Qdrant API key
- Cluster endpoint
3. Store them securely.

### .env file

Create a .env file to store secrets such as:

```dotenv
GROK_API_KEY=your_key
QDRANT_URL=your_url
QDRANT_API_KEY=your_key
```