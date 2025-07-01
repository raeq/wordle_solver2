# CI/CD and Development Guide

## Continuous Integration/Continuous Deployment

This project uses GitHub Actions for automated CI/CD with comprehensive testing, code quality checks, security scanning, and automated releases.

### Workflows

#### 1. Main CI/CD Pipeline (`.github/workflows/ci-cd.yml`)
Runs on every push and pull request:

- **Multi-Python Testing**: Tests against Python 3.8-3.13
- **Code Quality**: Black, Ruff, isort, and MyPy checks
- **Security Scanning**: Bandit security analysis
- **Package Building**: Creates both wheel and source distributions
- **Automated Publishing**:
  - TestPyPI on main branch pushes
  - PyPI on tagged releases

#### 2. Code Quality Checks (`.github/workflows/code-quality.yml`)
- Pre-commit hook validation
- Documentation structure verification
- Link checking in README

#### 3. Dependency Management (`.github/workflows/dependencies.yml`)
- Weekly dependency updates via Dependabot
- Security audits with pip-audit
- Auto-merge for patch updates

#### 4. Release Automation (`.github/workflows/release.yml`)
- Automated release creation on version tags
- Changelog generation
- Asset uploads to GitHub Releases

### Local Development Commands

Use these Makefile commands to run the same checks locally that run in CI:

```bash
# Run all CI checks locally
make ci-local

# Individual checks
make test           # Run tests with coverage
make lint           # Code quality checks
make type-check     # MyPy type checking
make security       # Bandit security scan
make audit          # Dependency vulnerability scan
make pre-commit     # Run pre-commit hooks

# Development setup
make setup-dev      # Install development dependencies
make format         # Auto-format code
```

### Security

- **Bandit**: Static security analysis for Python code
- **pip-audit**: Dependency vulnerability scanning
- **Dependabot**: Automated dependency updates with security alerts
- **Pre-commit hooks**: Prevent insecure code from being committed

### Publishing Workflow

1. **Development**: Work on feature branches
2. **Pull Request**: Automated testing and quality checks
3. **Merge**: Updates TestPyPI automatically
4. **Release**: Tag version (e.g., `v1.1.0`) triggers PyPI release

### Setup Instructions for Contributors

1. **Clone and setup**:
   ```bash
   git clone https://github.com/subzero/second-wordle-solver.git
   cd second-wordle-solver
   make setup-dev
   ```

2. **Before committing**:
   ```bash
   make ci-local  # Run all checks
   ```

3. **Creating a release**:
   ```bash
   git tag v1.1.0
   git push origin v1.1.0
   ```

### GitHub Integration

- **Issue Templates**: Bug reports and feature requests
- **Pull Request Template**: Comprehensive checklist
- **Dependabot**: Automated dependency management
- **Branch Protection**: Requires CI checks to pass

### Environment Variables for CI

Set these secrets in your GitHub repository:

- `PYPI_API_TOKEN`: For publishing to PyPI
- `TESTPYPI_API_TOKEN`: For publishing to TestPyPI

### Monitoring and Maintenance

- **Weekly dependency updates** via Dependabot
- **Security scans** on every commit
- **Coverage reports** uploaded to Codecov
- **Build artifacts** retained for 30 days
