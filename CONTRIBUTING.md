# Contributing to Website RAG MCP Service

Thank you for your interest in contributing! This document provides guidelines for contributing to the project.

## How to Contribute

### Reporting Bugs

If you find a bug, please create an issue with:
- Clear description of the problem
- Steps to reproduce
- Expected vs actual behavior
- Environment details (OS, Docker version, etc.)
- Relevant logs

### Suggesting Enhancements

Feature requests are welcome! Please include:
- Use case description
- Proposed solution
- Alternative solutions considered
- Impact on existing functionality

### Pull Requests

1. **Fork the repository**
2. **Create a feature branch**: `git checkout -b feature/your-feature-name`
3. **Make your changes**
4. **Test thoroughly**
5. **Commit with clear messages**: `git commit -m "Add feature: description"`
6. **Push to your fork**: `git push origin feature/your-feature-name`
7. **Open a Pull Request**

## Development Setup

### Local Development

```bash
# Clone your fork
git clone https://github.com/YOUR_USERNAME/website-to-mcp.git
cd website-to-mcp

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Start Qdrant
docker run -p 6333:6333 qdrant/qdrant

# Update config for local development
# Set vector_store.host to "localhost" in config.yaml

# Run ingestion
python app/ingest.py

# Start API server
uvicorn app.api.main:app --reload
```

### Testing with Docker

```bash
# Build and start services
docker compose up -d

# Run ingestion
docker compose run --rm ingest

# Test the API
./test.sh
```

## Code Style

### Python
- Follow PEP 8
- Use type hints where possible
- Add docstrings to functions and classes
- Keep functions focused and single-purpose
- Maximum line length: 100 characters

### Example
```python
from typing import List, Dict

def process_chunks(chunks: List[Dict]) -> List[Dict]:
    """
    Process text chunks for embedding.
    
    Args:
        chunks: List of text chunks with metadata
        
    Returns:
        Processed chunks ready for embedding
    """
    # Implementation
    pass
```

## Testing Guidelines

### Before Submitting PR
- [ ] Code runs without errors
- [ ] All existing functionality still works
- [ ] New features are documented
- [ ] Configuration examples updated if needed
- [ ] README updated if user-facing changes
- [ ] Docker builds successfully
- [ ] API endpoints tested manually

### Test Checklist
```bash
# Syntax check
python -m py_compile app/**/*.py

# Docker build
docker compose build

# Integration test
docker compose up -d
docker compose run --rm ingest
./test.sh

# Cleanup
docker compose down
```

## Project Structure

```
website-to-mcp/
├── app/
│   ├── api/              # FastAPI server
│   ├── crawler/          # Web crawling
│   ├── chunker/          # Text chunking
│   ├── embedder/         # Embedding & vector store
│   └── ingest.py         # Ingestion pipeline
├── config.yaml           # Configuration
├── docker-compose.yml    # Docker orchestration
├── Dockerfile            # Container definition
└── requirements.txt      # Python dependencies
```

## Areas for Contribution

### High Priority
- [ ] Add unit tests
- [ ] Add integration tests
- [ ] Implement authentication
- [ ] Add rate limiting
- [ ] Support for more content types (PDF, Markdown)
- [ ] Incremental updates (re-crawl changed pages only)
- [ ] Better error handling and retry logic

### Medium Priority
- [ ] Web UI for configuration and testing
- [ ] Monitoring and metrics (Prometheus)
- [ ] Advanced chunking strategies
- [ ] Multi-language support
- [ ] Configurable embedding models
- [ ] Batch query endpoint

### Nice to Have
- [ ] Automatic sitemap detection
- [ ] Support for authenticated sites
- [ ] Custom extractors for specific doc platforms
- [ ] Result caching
- [ ] A/B testing different chunking strategies
- [ ] Documentation quality scoring

## Commit Message Guidelines

Use conventional commits format:

```
type(scope): subject

body (optional)

footer (optional)
```

Types:
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code style changes (formatting)
- `refactor`: Code refactoring
- `test`: Adding or updating tests
- `chore`: Maintenance tasks

Examples:
```
feat(crawler): add support for PDF extraction
fix(api): handle empty query gracefully
docs(readme): add troubleshooting section
refactor(chunker): optimize chunk splitting algorithm
```

## Documentation

### Update Documentation When:
- Adding new features
- Changing API endpoints
- Modifying configuration options
- Changing deployment steps
- Adding dependencies

### Documentation Files
- `README.md`: User-facing documentation
- `ARCHITECTURE.md`: Technical architecture
- `EXAMPLES.md`: Usage examples
- Inline code comments for complex logic

## Review Process

1. **Automated Checks**: CI pipeline (if configured)
2. **Code Review**: Maintainer reviews code
3. **Testing**: Reviewer tests functionality
4. **Feedback**: Suggested changes or approval
5. **Merge**: PR merged to main branch

## Questions?

- Open an issue for questions
- Tag with `question` label
- Maintainers will respond ASAP

## Code of Conduct

- Be respectful and inclusive
- Provide constructive feedback
- Focus on the code, not the person
- Welcome newcomers
- Help others learn

## Recognition

Contributors will be:
- Listed in README acknowledgments
- Credited in release notes
- Thanked in commit messages

Thank you for contributing to Website RAG MCP Service!
