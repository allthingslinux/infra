# Infrastructure Diagrams

This page contains automatically generated diagrams of the infrastructure architecture.

## Terraform Graph

The following diagram is generated from the Terraform configuration and shows the relationships between all resources.

![Terraform Graph](../assets/infrastructure.svg)

## Infrastructure Overview

```mermaid
graph TB
    subgraph "External Services"
        CF[Cloudflare CDN/WAF]
        DNS[DNS Providers]
        GITHUB[GitHub]
    end

    subgraph "Production Infrastructure"
        LB[Load Balancer]
        WEB1[Web Server 1]
        WEB2[Web Server 2]
        DB[(Database Cluster)]
        REDIS[(Redis Cache)]
    end

    subgraph "Monitoring & Logs"
        MONITOR[Monitoring Stack]
        LOGS[Log Aggregation]
    end

    subgraph "Development"
        LOCAL[Local Development]
        STAGING[Staging Environment]
    end

    CF --> LB
    DNS --> CF
    LB --> WEB1
    LB --> WEB2
    WEB1 --> DB
    WEB2 --> DB
    WEB1 --> REDIS
    WEB2 --> REDIS

    MONITOR --> WEB1
    MONITOR --> WEB2
    LOGS --> WEB1
    LOGS --> WEB2

    GITHUB --> STAGING
    STAGING --> LB
    LOCAL --> STAGING
```

## Deployment Pipeline

```mermaid
graph LR
    DEV[Local Development] --> COMMIT[Git Commit]
    COMMIT --> PR[Pull Request]
    PR --> REVIEW[Code Review]
    REVIEW --> MERGE[Merge to Main]
    MERGE --> BUILD[CI Build]
    BUILD --> TEST[Automated Tests]
    TEST --> DEPLOY_STAGING[Deploy to Staging]
    DEPLOY_STAGING --> MANUAL_TEST[Manual Testing]
    MANUAL_TEST --> DEPLOY_PROD[Deploy to Production]
    DEPLOY_PROD --> MONITOR[Monitor & Verify]
```

## Network Architecture

```mermaid
graph TB
    subgraph "Internet"
        USER[Users]
    end

    subgraph "Cloudflare"
        CDN[CDN Cache]
        WAF[Web Application Firewall]
        DDOS[DDoS Protection]
    end

    subgraph "Hetzner Cloud"
        subgraph "Public Subnet"
            LB[Load Balancer<br/>10.0.1.10]
            BASTION[Bastion Host<br/>10.0.1.20]
        end

        subgraph "Private Subnet"
            WEB1[Web Server 1<br/>10.0.2.10]
            WEB2[Web Server 2<br/>10.0.2.11]
            DB[Database<br/>10.0.2.20]
            REDIS[Redis<br/>10.0.2.21]
        end
    end

    USER --> CDN
    CDN --> WAF
    WAF --> DDOS
    DDOS --> LB
    LB --> WEB1
    LB --> WEB2
    WEB1 --> DB
    WEB2 --> DB
    WEB1 --> REDIS
    WEB2 --> REDIS
    BASTION --> WEB1
    BASTION --> WEB2
```

## Service Dependencies

```mermaid
graph TD
    subgraph "Frontend Services"
        NGINX[Nginx Reverse Proxy]
        STATIC[Static File Server]
    end

    subgraph "Application Services"
        TUX[Tux Bot Service]
        API[API Service]
        AUTH[Authentication Service]
    end

    subgraph "Data Layer"
        POSTGRES[(PostgreSQL)]
        REDIS_CACHE[(Redis Cache)]
        FILES[File Storage]
    end

    subgraph "External APIs"
        DISCORD[Discord API]
        GITHUB_API[GitHub API]
    end

    NGINX --> TUX
    NGINX --> API
    NGINX --> STATIC

    TUX --> AUTH
    TUX --> POSTGRES
    TUX --> REDIS_CACHE
    TUX --> DISCORD

    API --> AUTH
    API --> POSTGRES
    API --> REDIS_CACHE
    API --> GITHUB_API

    AUTH --> POSTGRES

    STATIC --> FILES
```

## Ansible Automation Flow

```mermaid
graph TB
    CONTROL[Ansible Control Node] --> INVENTORY[Dynamic Inventory]
    INVENTORY --> STAGING[Staging Servers]
    INVENTORY --> PROD[Production Servers]

    subgraph "Playbooks"
        SITE[site.yml]
        BOOTSTRAP[bootstrap.yml]
        DEPLOY[dynamic-deploy.yml]
        SECURITY[hardening.yml]
    end

    subgraph "Roles"
        SYSTEM[System Role]
        DOCKER[Docker Role]
        TUX_ROLE[Tux Role]
    end

    CONTROL --> SITE
    SITE --> BOOTSTRAP
    SITE --> DEPLOY
    SITE --> SECURITY

    BOOTSTRAP --> SYSTEM
    DEPLOY --> DOCKER
    DEPLOY --> TUX_ROLE
    SECURITY --> SYSTEM
```

## Terraform Resource Dependencies

```mermaid
graph TB
    PROVIDER[Hetzner Provider] --> NETWORK[VPC Network]
    NETWORK --> SUBNET_PUB[Public Subnet]
    NETWORK --> SUBNET_PRIV[Private Subnet]

    SUBNET_PUB --> LB[Load Balancer]
    SUBNET_PRIV --> SERVERS[Server Instances]

    SERVERS --> VOLUMES[Storage Volumes]
    SERVERS --> FIREWALL[Firewall Rules]

    subgraph "DNS Management"
        CLOUDFLARE[Cloudflare Provider]
        DOMAINS[Domain Records]
    end

    CLOUDFLARE --> DOMAINS
    LB --> DOMAINS
```

## Monitoring Architecture

```mermaid
graph TB
    subgraph "Data Sources"
        APP_LOGS[Application Logs]
        SYS_LOGS[System Logs]
        METRICS[System Metrics]
        TRACES[Application Traces]
    end

    subgraph "Collection Layer"
        FLUENTD[Fluentd/Fluent Bit]
        PROMETHEUS[Prometheus]
        JAEGER[Jaeger]
    end

    subgraph "Storage Layer"
        ELASTIC[Elasticsearch]
        TSDB[Time Series DB]
        TRACE_DB[Trace Storage]
    end

    subgraph "Visualization"
        GRAFANA[Grafana]
        KIBANA[Kibana]
        JAEGER_UI[Jaeger UI]
    end

    subgraph "Alerting"
        ALERT_MGR[Alert Manager]
        SLACK[Slack Notifications]
        EMAIL[Email Alerts]
    end

    APP_LOGS --> FLUENTD
    SYS_LOGS --> FLUENTD
    METRICS --> PROMETHEUS
    TRACES --> JAEGER

    FLUENTD --> ELASTIC
    PROMETHEUS --> TSDB
    JAEGER --> TRACE_DB

    ELASTIC --> KIBANA
    TSDB --> GRAFANA
    TRACE_DB --> JAEGER_UI

    PROMETHEUS --> ALERT_MGR
    ALERT_MGR --> SLACK
    ALERT_MGR --> EMAIL
```

## Security Architecture

```mermaid
graph TB
    subgraph "External Security"
        CLOUDFLARE_SEC[Cloudflare Security]
        DDOS_PROT[DDoS Protection]
        WAF_RULES[WAF Rules]
    end

    subgraph "Network Security"
        VPC[VPC Isolation]
        SECURITY_GROUPS[Security Groups]
        NACL[Network ACLs]
    end

    subgraph "Host Security"
        HARDENING[OS Hardening]
        FIREWALL_HOST[Host Firewall]
        FAIL2BAN[Fail2ban]
    end

    subgraph "Application Security"
        TLS[TLS Encryption]
        AUTH_JWT[JWT Authentication]
        RBAC[Role-Based Access]
    end

    subgraph "Data Security"
        ENCRYPTION[Data Encryption]
        BACKUP_ENC[Encrypted Backups]
        SECRET_MGT[Secret Management]
    end

    CLOUDFLARE_SEC --> DDOS_PROT
    CLOUDFLARE_SEC --> WAF_RULES

    VPC --> SECURITY_GROUPS
    VPC --> NACL

    HARDENING --> FIREWALL_HOST
    HARDENING --> FAIL2BAN

    TLS --> AUTH_JWT
    AUTH_JWT --> RBAC

    ENCRYPTION --> BACKUP_ENC
    ENCRYPTION --> SECRET_MGT
```

## Backup and Recovery Flow

```mermaid
graph TD
    subgraph "Data Sources"
        DB_DATA[(Database Data)]
        CONFIG[Configuration Files]
        SECRETS[Secrets/Keys]
        USER_DATA[User Generated Content]
    end

    subgraph "Backup Process"
        SCHEDULE[Scheduled Backup]
        COMPRESS[Compression]
        ENCRYPT[Encryption]
        UPLOAD[Upload to Storage]
    end

    subgraph "Storage Locations"
        LOCAL[Local Backup]
        REMOTE[Remote Storage]
        ARCHIVE[Long-term Archive]
    end

    subgraph "Recovery Process"
        RESTORE[Restore from Backup]
        VERIFY[Verify Integrity]
        DEPLOY[Deploy to Target]
    end

    DB_DATA --> SCHEDULE
    CONFIG --> SCHEDULE
    SECRETS --> SCHEDULE
    USER_DATA --> SCHEDULE

    SCHEDULE --> COMPRESS
    COMPRESS --> ENCRYPT
    ENCRYPT --> UPLOAD

    UPLOAD --> LOCAL
    UPLOAD --> REMOTE
    REMOTE --> ARCHIVE

    LOCAL --> RESTORE
    REMOTE --> RESTORE
    RESTORE --> VERIFY
    VERIFY --> DEPLOY
```

## Related Documentation

- [Infrastructure Overview](overview.md)
- [Terraform Modules](terraform.md)
- [CLI Tools](../automation/cli-tools.md)
