# Ansible Playbooks & CI/CD Automation

This document contains automatically generated documentation for all Ansible playbooks and the CI/CD automation system.

## CI/CD Workflow Overview

The infrastructure project uses a streamlined CI/CD system with three main workflows that follow industry best practices:

### 1. CI Workflow (`.github/workflows/ci.yml`)

**Purpose**: Comprehensive quality assurance with optimized job dependencies

**Triggers**: Push to main/develop, Pull Requests, Manual dispatch

**Jobs**:

- **Quick Checks**: Fast path filtering to determine what needs testing
- **Python Quality**: Code linting and formatting with Ruff
- **Python Tests**: Test execution with pytest
- **Terraform Quality**: Infrastructure code validation and security scanning
- **Ansible Quality**: Playbook and role linting with ansible-lint
- **Documentation**: Build and validate documentation with MkDocs
- **Integration Tests**: Cross-component integration testing
- **Quality Gate**: Summary reporting and status aggregation

**Features**:

- Parallel job execution for efficiency
- Path-based filtering (only run relevant checks)
- Advanced caching with uv and Terraform providers
- Proper job dependencies and timeout limits
- Comprehensive error reporting

### 2. Security Workflow (`.github/workflows/security.yml`)

**Purpose**: Comprehensive security scanning without duplication

**Triggers**: Push/PR, Weekly schedule, Manual dispatch with full scan option

**Security Scans**:

- **Secrets Detection**: Gitleaks for credential scanning
- **Dependency Scanning**: OWASP audit and vulnerability assessment
- **Infrastructure Security**: Terraform security analysis with Trivy
- **Static Analysis**: Code security analysis with CodeQL
- **Container Security**: Docker image vulnerability scanning

**Features**:

- Matrix-based scanning strategies
- SARIF upload to GitHub Security tab
- Enhanced summary reporting
- Configurable scan depth (quick vs full)

### 3. PR Automation (`.github/workflows/pr-automation.yml`)

**Purpose**: Intelligent PR analysis and automation complementing path-based labeling

**Functions**:

- **Size Analysis**: Automatic PR size labeling (XS/S/M/L/XL)
- **Complexity Scoring**: Code complexity assessment
- **Security Impact Detection**: Identify security-sensitive changes
- **Conflict Detection**: Merge conflict identification
- **Status Management**: PR-specific status labels
- **Auto-assignment**: Intelligent reviewer assignment based on labels
- **PR Summaries**: Automated analysis comments

**Integration**: Works harmoniously with the GitHub Labeler for comprehensive PR classification

### 4. Labeler Workflow (`.github/workflows/labeler.yml`)

**Purpose**: Sophisticated path-based automatic labeling

**Features**:

- **Domain Classification**: Infrastructure, security, monitoring, etc.
- **Environment Detection**: Production, staging, development
- **Impact Assessment**: Major/minor change classification
- **Technology Tagging**: Terraform, Ansible, Docker, Python, etc.
- **Urgency Classification**: Emergency, maintenance priorities

**Label Categories**:

- Impact & Scope: `major`, `minor`
- Environments: `production`, `staging`, `development`
- Technical Domains: `infrastructure`, `security`, `monitoring`, `ci/cd`
- Services: `docker`, `gitops`, `services`
- Documentation: `docs`, `config`

## Lefthook Integration

The project uses an optimized lefthook configuration that complements CI workflows:

### Local Development Hooks

- **Commit Message Formatting**: Conventional commits validated by commitlint
- **Security Scanning**: Gitleaks for secrets detection
- **Code Quality**: Basic formatting and syntax checks
- **YAML Linting**: Ansible and configuration file validation
- **Shell Scripts**: Formatting and linting with shfmt/shellcheck
- **Python**: Fast linting and formatting with Ruff
- **Terraform**: Formatting, validation, and documentation
- **Project Structure**: Critical file validation

### Performance Optimization

- Light security checks for local development
- Heavy analysis deferred to CI workflows
- Quick feedback for common issues
- Complementary rather than duplicative checking

---

## Ansible Playbooks Documentation

## ATL Infrastructure Management - Domain-Based Deployment

**File**: `playbooks/site.yml`
**Hosts**: `
