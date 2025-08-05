// All Things Linux Infrastructure Documentation JavaScript

document.addEventListener('DOMContentLoaded', function () {
    // Add copy button to code blocks
    addCopyButtons();

    // Initialize tooltips
    initializeTooltips();

    // Add status indicators
    addStatusIndicators();

    // Initialize interactive diagrams
    initializeDiagrams();

    // Add search enhancements
    enhanceSearch();
});

// Add copy buttons to code blocks
function addCopyButtons() {
    const codeBlocks = document.querySelectorAll('pre code');

    codeBlocks.forEach(function (codeBlock) {
        const pre = codeBlock.parentNode;
        const copyButton = document.createElement('button');

        copyButton.className = 'copy-button';
        copyButton.innerHTML = '📋 Copy';
        copyButton.style.cssText = `
            position: absolute;
            top: 8px;
            right: 8px;
            background: #3f51b5;
            color: white;
            border: none;
            padding: 4px 8px;
            border-radius: 4px;
            font-size: 12px;
            cursor: pointer;
            opacity: 0;
            transition: opacity 0.2s;
        `;

        pre.style.position = 'relative';
        pre.appendChild(copyButton);

        // Show button on hover
        pre.addEventListener('mouseenter', function () {
            copyButton.style.opacity = '1';
        });

        pre.addEventListener('mouseleave', function () {
            copyButton.style.opacity = '0';
        });

        // Copy functionality
        copyButton.addEventListener('click', function () {
            navigator.clipboard.writeText(codeBlock.textContent).then(function () {
                copyButton.innerHTML = '✅ Copied!';
                setTimeout(function () {
                    copyButton.innerHTML = '📋 Copy';
                }, 2000);
            });
        });
    });
}

// Initialize tooltips for technical terms
function initializeTooltips() {
    const tooltipTerms = {
        'Terraform': 'Infrastructure as Code tool for building, changing, and versioning infrastructure',
        'Ansible': 'Automation platform that configures systems, deploys software, and orchestrates tasks',
        'Docker': 'Platform for developing, shipping, and running applications in containers',
        'Kubernetes': 'Container orchestration platform for automating deployment and management',
        'Load Balancer': 'Distributes incoming network traffic across multiple backend servers',
        'SSL/TLS': 'Cryptographic protocols that provide secure communication over networks',
        'VPC': 'Virtual Private Cloud - isolated section of cloud infrastructure',
        'CI/CD': 'Continuous Integration/Continuous Deployment - automated development practices'
    };

    Object.keys(tooltipTerms).forEach(function (term) {
        const regex = new RegExp('\\b' + term + '\\b', 'gi');
        const content = document.querySelector('.md-content');

        if (content) {
            content.innerHTML = content.innerHTML.replace(regex, function (match) {
                return `<span class="tooltip" title="${tooltipTerms[term]}">${match}</span>`;
            });
        }
    });

    // Style tooltips
    const style = document.createElement('style');
    style.textContent = `
        .tooltip {
            position: relative;
            text-decoration: underline;
            text-decoration-style: dotted;
            cursor: help;
        }

        .tooltip:hover::after {
            content: attr(title);
            position: absolute;
            bottom: 100%;
            left: 50%;
            transform: translateX(-50%);
            background: #333;
            color: white;
            padding: 8px;
            border-radius: 4px;
            font-size: 12px;
            white-space: nowrap;
            z-index: 1000;
            margin-bottom: 4px;
        }

        .tooltip:hover::before {
            content: '';
            position: absolute;
            bottom: 100%;
            left: 50%;
            transform: translateX(-50%);
            border: 4px solid transparent;
            border-top-color: #333;
            z-index: 1000;
        }
    `;
    document.head.appendChild(style);
}

// Add live status indicators
function addStatusIndicators() {
    const statusContainer = document.querySelector('#status-indicators');
    if (!statusContainer) return;

    const services = [
        { name: 'API Gateway', status: 'operational', url: 'https://api.allthingslinux.org/health' },
        { name: 'Web Frontend', status: 'operational', url: 'https://allthingslinux.org' },
        { name: 'Database', status: 'operational', url: null },
        { name: 'Monitoring', status: 'operational', url: null }
    ];

    services.forEach(function (service) {
        const indicator = document.createElement('div');
        indicator.className = `status-indicator status-${service.status}`;
        indicator.innerHTML = `${service.name}: ${service.status.toUpperCase()}`;
        statusContainer.appendChild(indicator);

        // Check actual status if URL provided
        if (service.url) {
            checkServiceStatus(service.url, indicator);
        }
    });
}

// Check service status
function checkServiceStatus(url, indicator) {
    fetch(url, { method: 'HEAD', mode: 'no-cors' })
        .then(function () {
            indicator.className = 'status-indicator status-operational';
            indicator.innerHTML = indicator.innerHTML.replace(/:\s*\w+/, ': OPERATIONAL');
        })
        .catch(function () {
            indicator.className = 'status-indicator status-error';
            indicator.innerHTML = indicator.innerHTML.replace(/:\s*\w+/, ': ERROR');
        });
}

// Initialize interactive diagrams
function initializeDiagrams() {
    const diagrams = document.querySelectorAll('.architecture-diagram svg');

    diagrams.forEach(function (svg) {
        // Add zoom functionality
        svg.style.cursor = 'zoom-in';
        svg.addEventListener('click', function () {
            if (svg.style.transform === 'scale(1.5)') {
                svg.style.transform = 'scale(1)';
                svg.style.cursor = 'zoom-in';
            } else {
                svg.style.transform = 'scale(1.5)';
                svg.style.cursor = 'zoom-out';
            }
            svg.style.transition = 'transform 0.3s ease';
        });

        // Add hover effects to nodes
        const nodes = svg.querySelectorAll('g[id*="node"]');
        nodes.forEach(function (node) {
            node.addEventListener('mouseenter', function () {
                node.style.filter = 'brightness(1.2)';
            });

            node.addEventListener('mouseleave', function () {
                node.style.filter = 'brightness(1)';
            });
        });
    });
}

// Enhance search functionality
function enhanceSearch() {
    const searchInput = document.querySelector('.md-search__input');
    if (!searchInput) return;

    // Add search suggestions
    const searchTerms = [
        'deployment', 'terraform', 'ansible', 'docker', 'configuration',
        'network', 'security', 'monitoring', 'CLI tools', 'troubleshooting'
    ];

    let searchSuggestions = document.createElement('div');
    searchSuggestions.className = 'search-suggestions';
    searchSuggestions.style.cssText = `
        position: absolute;
        top: 100%;
        left: 0;
        right: 0;
        background: white;
        border: 1px solid #ddd;
        border-top: none;
        border-radius: 0 0 4px 4px;
        max-height: 200px;
        overflow-y: auto;
        z-index: 1000;
        display: none;
    `;

    searchInput.parentNode.style.position = 'relative';
    searchInput.parentNode.appendChild(searchSuggestions);

    searchInput.addEventListener('input', function () {
        const query = this.value.toLowerCase();
        if (query.length < 2) {
            searchSuggestions.style.display = 'none';
            return;
        }

        const matches = searchTerms.filter(term =>
            term.toLowerCase().includes(query)
        );

        if (matches.length > 0) {
            searchSuggestions.innerHTML = matches.map(term =>
                `<div class="search-suggestion" style="padding: 8px; cursor: pointer; border-bottom: 1px solid #eee;">${term}</div>`
            ).join('');
            searchSuggestions.style.display = 'block';

            // Add click handlers
            searchSuggestions.querySelectorAll('.search-suggestion').forEach(function (suggestion) {
                suggestion.addEventListener('click', function () {
                    searchInput.value = this.textContent;
                    searchSuggestions.style.display = 'none';
                    // Trigger search
                    searchInput.dispatchEvent(new Event('input'));
                });
            });
        } else {
            searchSuggestions.style.display = 'none';
        }
    });

    // Hide suggestions when clicking outside
    document.addEventListener('click', function (e) {
        if (!searchInput.parentNode.contains(e.target)) {
            searchSuggestions.style.display = 'none';
        }
    });
}

// Add keyboard shortcuts
document.addEventListener('keydown', function (e) {
    // Ctrl/Cmd + K to focus search
    if ((e.ctrlKey || e.metaKey) && e.key === 'k') {
        e.preventDefault();
        const searchInput = document.querySelector('.md-search__input');
        if (searchInput) {
            searchInput.focus();
        }
    }

    // Escape to close modals/overlays
    if (e.key === 'Escape') {
        const suggestions = document.querySelector('.search-suggestions');
        if (suggestions) {
            suggestions.style.display = 'none';
        }
    }
});

// Add theme toggle functionality
function addThemeToggle() {
    const themeToggle = document.createElement('button');
    themeToggle.innerHTML = '🌙';
    themeToggle.className = 'theme-toggle';
    themeToggle.style.cssText = `
        position: fixed;
        bottom: 20px;
        right: 20px;
        background: #3f51b5;
        color: white;
        border: none;
        border-radius: 50%;
        width: 48px;
        height: 48px;
        font-size: 20px;
        cursor: pointer;
        box-shadow: 0 2px 8px rgba(0,0,0,0.2);
        z-index: 1000;
        transition: all 0.3s ease;
    `;

    document.body.appendChild(themeToggle);

    themeToggle.addEventListener('click', function () {
        const currentScheme = document.documentElement.getAttribute('data-md-color-scheme');
        const newScheme = currentScheme === 'slate' ? 'default' : 'slate';

        document.documentElement.setAttribute('data-md-color-scheme', newScheme);
        themeToggle.innerHTML = newScheme === 'slate' ? '☀️' : '🌙';

        // Save preference
        localStorage.setItem('theme', newScheme);
    });

    // Load saved theme
    const savedTheme = localStorage.getItem('theme');
    if (savedTheme) {
        document.documentElement.setAttribute('data-md-color-scheme', savedTheme);
        themeToggle.innerHTML = savedTheme === 'slate' ? '☀️' : '🌙';
    }
}

// Initialize theme toggle
setTimeout(addThemeToggle, 1000);

// Analytics and performance tracking
function trackPageLoad() {
    const loadTime = performance.timing.loadEventEnd - performance.timing.navigationStart;
    console.log(`Page loaded in ${loadTime}ms`);

    // Track which sections are viewed
    const observer = new IntersectionObserver(function (entries) {
        entries.forEach(function (entry) {
            if (entry.isIntersecting) {
                const sectionName = entry.target.id || entry.target.tagName;
                console.log(`Viewing section: ${sectionName}`);
            }
        });
    });

    document.querySelectorAll('h2, h3').forEach(function (heading) {
        observer.observe(heading);
    });
}

// Initialize performance tracking
setTimeout(trackPageLoad, 2000);
