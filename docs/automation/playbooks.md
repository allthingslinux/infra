# Ansible Playbooks

This document contains automatically generated documentation for all Ansible playbooks.

## ATL Infrastructure Management - Domain-Based Deployment

**File**: `playbooks/site.yml`
**Hosts**: `localhost`

### Tasks

- Display deployment banner
- Display infrastructure overview

## Phase 1: Bootstrap Core Infrastructure

**File**: `playbooks/site.yml`
**Hosts**: `undefined`

## Phase 2: Load Domain Configuration and Deploy All Enabled Domains

**File**: `playbooks/site.yml`
**Hosts**: `localhost`

### Tasks

- Load domains configuration
- Filter enabled domains
- Display deployment plan

## Phase 3a: Deploy Control Server (atl_services)

**File**: `playbooks/site.yml`
**Hosts**: `localhost`

### Tasks

- Deploy atl_services domain

## Phase 3b: Deploy Tools Server (atl_tools)

**File**: `playbooks/site.yml`
**Hosts**: `localhost`

### Tasks

- Deploy atl_tools domain

## Phase 3c: Deploy Development Server (atl_dev)

**File**: `playbooks/site.yml`
**Hosts**: `localhost`

### Tasks

- Deploy atl_dev domain

## Phase 3d: Deploy Chat Server (atl_chat)

**File**: `playbooks/site.yml`
**Hosts**: `localhost`

### Tasks

- Deploy atl_chat domain

## Phase 3e: Deploy Wiki Server (atl_wiki)

**File**: `playbooks/site.yml`
**Hosts**: `localhost`

### Tasks

- Deploy atl_wiki domain

## Phase 5: Deploy Shared Database Cluster

**File**: `playbooks/site.yml`
**Hosts**: `undefined`

## Phase 6: Configure Staff Management

**File**: `playbooks/site.yml`
**Hosts**: `undefined`

## Phase 7: Apply Security Hardening

**File**: `playbooks/site.yml`
**Hosts**: `undefined`

## Phase 8: Configure Backup Systems

**File**: `playbooks/site.yml`
**Hosts**: `undefined`

## Phase 9: Final Configuration

**File**: `playbooks/site.yml`
**Hosts**: `all`

### Tasks

- Update all reverse proxy configurations
- Configure cross-service communication
- Verify all services are accessible
- Configure monitoring for all services

## Infrastructure Deployment Summary

**File**: `playbooks/site.yml`
**Hosts**: `all`

### Tasks

- Collect service status
- Check system resources
- Display deployment summary

## Load and Process Domain Configuration

**File**: `playbooks/dynamic-deploy.yml`
**Hosts**: `localhost`

### Tasks

- Load domains configuration
- Filter enabled domains
- Display enabled domains

## Deploy Enabled Domains

**File**: `playbooks/dynamic-deploy.yml`
**Hosts**: `localhost`

### Tasks

- Create deployment manifest
- Display deployment instructions
- Note about manual deployment

## Post-Deployment Verification

**File**: `playbooks/dynamic-deploy.yml`
**Hosts**: `localhost`

### Tasks

- Display deployment summary
