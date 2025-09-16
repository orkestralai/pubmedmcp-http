# Contributing to PubMed MCP HTTP-Vercel

Thank you for your interest in contributing to the PubMed MCP HTTP-streamable server! This document provides guidelines and information for contributors.

## 🚀 Getting Started

### Prerequisites

- Python 3.12+
- [uv](https://github.com/astral-sh/uv) package manager
- Git
- A GitHub account

### Development Setup

1. **Fork the repository** on GitHub
2. **Clone your fork**:
   ```bash
   git clone https://github.com/your-username/pubmedmcp-http-vercel.git
   cd pubmedmcp-http-vercel
   ```

3. **Install dependencies**:
   ```bash
   uv sync
   ```

4. **Run locally**:
   ```bash
   uv run pubmedmcp --port 3000 --log-level DEBUG
   ```

## 🛠️ Development Guidelines

### Code Style

- Follow PEP 8 Python style guidelines
- Use type hints where appropriate
- Write clear, descriptive docstrings
- Keep functions focused and small

### Testing

Before submitting changes:

1. **Test locally**:
   ```bash
   # Test the server
   uv run pubmedmcp --port 3000
   
   # Test with curl
   curl -X GET http://127.0.0.1:3000/mcp \
     -H "Mcp-Session-Id: test-session-123"
   ```

2. **Test on Vercel** (optional):
   ```bash
   # Install Vercel CLI
   npm i -g vercel
   
   # Deploy to preview
   vercel
   ```

### Pull Request Process

1. **Create a feature branch**:
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **Make your changes**:
   - Write clear, focused commits
   - Update documentation if needed
   - Add tests if applicable

3. **Test your changes**:
   - Ensure the server runs without errors
   - Test the MCP protocol functionality
   - Verify Vercel deployment works

4. **Submit a pull request**:
   - Provide a clear description of changes
   - Reference any related issues
   - Include test results if applicable

## 📝 Types of Contributions

### Bug Reports

When reporting bugs, please include:

- Python version
- Operating system
- Steps to reproduce
- Expected vs actual behavior
- Error messages or logs

### Feature Requests

For new features, please:

- Check existing issues first
- Describe the use case clearly
- Explain how it fits the project's goals
- Consider implementation complexity

### Code Contributions

We welcome contributions in these areas:

- **Bug fixes**: Fix issues in existing code
- **Performance improvements**: Optimize API calls or response handling
- **New features**: Add new MCP tools or capabilities
- **Documentation**: Improve README, code comments, or examples
- **Testing**: Add test cases or improve testing

## 🔧 Project Structure

```
pubmedmcp-http-vercel/
├── api/
│   └── index.py             # Vercel serverless function handler
├── src/pubmedmcp/
│   ├── __init__.py          # Package initialization
│   ├── __main__.py          # CLI entry point
│   └── server.py            # HTTP-streamable MCP server
├── scripts/
│   └── bump_version.py      # Version management script
├── pyproject.toml           # Project configuration
├── requirements.txt         # Python dependencies for Vercel
├── vercel.json             # Vercel deployment configuration
└── README.md               # Main documentation
```

## 🐛 Issue Guidelines

### Before Creating an Issue

1. Search existing issues to avoid duplicates
2. Check if it's already been fixed in the latest version
3. Gather relevant information (logs, system info, etc.)

### Issue Templates

Use the appropriate template:
- **Bug Report**: For unexpected behavior or errors
- **Feature Request**: For new functionality ideas
- **Question**: For help or clarification

## 📋 Release Process

Releases are managed through the version bump script:

```bash
# Patch release (bug fixes)
python scripts/bump_version.py patch

# Minor release (new features)
python scripts/bump_version.py minor

# Major release (breaking changes)
python scripts/bump_version.py major

# With GitHub release
python scripts/bump_version.py patch --release
```

## 🤝 Community Guidelines

### Code of Conduct

- Be respectful and inclusive
- Focus on constructive feedback
- Help others learn and grow
- Follow the golden rule

### Communication

- Use clear, descriptive commit messages
- Provide context in pull requests
- Ask questions when unsure
- Be patient with responses

## 📚 Resources

- [Model Context Protocol (MCP)](https://modelcontextprotocol.io/)
- [PubMed API Documentation](https://www.ncbi.nlm.nih.gov/books/NBK25501/)
- [Vercel Documentation](https://vercel.com/docs)
- [Python Type Hints](https://docs.python.org/3/library/typing.html)

## ❓ Questions?

If you have questions about contributing:

1. Check the [Issues](https://github.com/your-username/pubmedmcp-http-vercel/issues) page
2. Create a new issue with the "Question" label
3. Join discussions in existing issues

Thank you for contributing to PubMed MCP HTTP-Vercel! 🎉
