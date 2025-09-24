EasySSH – Software Design Document
1. Overview

EasySSH is a tool designed to simplify and centralize the management of SSH credentials, devices, and connections. It combines a web dashboard, a CLI tool, and a backend service to provide a seamless user experience for authentication, vault-based storage of SSH credentials, and secure sharing of SSH access.

The design is inspired by Tailscale in terms of CLI usability and browser-based authentication.

2. Tech Stack
2.1 Backend

Framework: FastAPI

Database: PostgreSQL with SQLModel ORM

Authentication:

Native email/password login (for web)

Single Sign-On (SSO) support

CLI authentication handled via browser-based approval flow

API Specification: OpenAPI

2.2 Frontend

Framework: React

UI Library: shadcn/ui (for modern, consistent UI components)

Integration: OpenAPI SDK for typed API calls

Authentication: SSO and email/password

2.3 CLI Tool

Implementation: Single-file Python script

Distribution:

pip install easyssh (user-level installation only, no root required)

Bash bootstrapper (https://example.sh/<token> | bash) that internally runs pip install easyssh

Dependencies: Minimal, using standard library + requests

Compatibility: Linux, macOS, and Windows (as long as Python is available)

Privileges: Functional without root access

3. User Flow

Login to Web Portal

User signs in using SSO or email/password.

Dashboard Access

User is presented with a dashboard.

Installation script for the CLI is provided:

https://example.sh/<token> | bash


CLI Authentication

User runs:

easyssh auth login


This opens a browser for approval. CLI polls server for completion.

Check Authentication Status

Confirm login status with:

easyssh auth status


Vault Creation

When a new device connects, it automatically creates its own vault, named by device username + hostname.

Device Sync

User runs easyssh sync.

All SSH configurations and private/public keys from ~/.ssh are uploaded to the server.

For MVP, no file selection is supported (though the CLI may show a one-time confirmation).

Vault & Device Management

Dashboard shows vaults and connected devices, including:

Device name

OS name

Current user

Last sync timestamp

SSH Connections

User connects to servers from stored vaults directly via the CLI.

If connecting from another vault, the vault ID must be specified.

Sharing Credentials

Vault items or entire vaults can be shared with shareable links.

The recipient executes:

<shareable-link> | bash


For MVP, revocation is not yet implemented, but links have expiration support.

4. Dashboard Features
4.1 Core Sections

Install New Device

Vault

Devices

Contact (Enterprise inquiry)

4.2 Vault Structure

Vaults may be organized with tags (e.g., OS, hostname).

Sub-vaults are not separate entities, only categorization metadata.

Each device has its own default vault.

4.3 Device Compatibility

Supported platforms:

Linux

macOS

Windows (with Python installed)

5. Frontend Pages

Login Page (email/password or SSO)

Registration Page

Dashboard

Vault Page (view and manage credentials/keys)

Devices Page (list and manage devices)

Contact Page (enterprise contact only, static)

6. Functional Requirements
6.1 Vault Management

Create, rename, and delete vaults

Tag vaults with metadata (OS, hostname, etc.)

List connected devices per vault

Share vaults or individual items

6.2 Device Management

Auto-create vault for each new device

List devices with metadata

Kick devices from vaults

Track last sync timestamp

6.3 Vault Items

Types:

SSH Keys (private/public pairs)

SSH Credentials (host, username, port, parameters)

Add, update, and delete vault items

Keys can be generated or uploaded

6.4 Sharing SSH Access

Generate shareable links for vaults or items

Expiration settings (by time or single-use)

Executed as <link> | bash to bootstrap access

MVP: revocation not available yet, but DB supports disabling later

7. Modals

Login Modal: Email, password, or SSO

Registration Modal: First name, last name, email, password

Vault Rename Modal: New name input

Vault Item Update Modal: Modify SSH credentials or keys

Key Management Modals:

Generate private/public key pair

Add existing private/public keys

8. Security Considerations (MVP + Future)
8.1 MVP-Level Security

All traffic must use HTTPS (TLS 1.2+ with HSTS)

JWT/OAuth tokens with short TTLs for auth sessions

Access control restricted to owner or explicitly shared users

Database fields for private keys marked as encryption-ready, but stored in plaintext initially

Shareable links must have at least an expiration time (no eternal links)

CLI must handle keys securely:

Write to temp file with chmod 600

Delete temp files after use

Avoid passing keys in process command line

8.2 Planned Future Enhancements

Client-side encryption of private keys before sync (zero-knowledge model)

Server-side KMS integration as optional fallback for enterprise users

Full revocation support for shareable links and vault items

Audit logging improvements (alerting, anomaly detection)

Granular sync options (selective file uploads)

9. Dashboard Notes

Vaults are device-driven by default: each new device creates its own vault on first sync.

Vaults can be further organized with tags.

In the vault view, SSH items can be managed, shared, or renamed.

Shareable links will log metadata such as IP and user agent for each hit.

10. Device Notes

Devices automatically register with their hostname + username combination.

Device data shown in dashboard includes:

Name (hostname)

OS name

Current user

Last sync timestamp

Devices can be kicked out from dashboard or CLI.

11. Installation
11.1 Via Pip
pip install --user easyssh

11.2 Via Script
https://example.sh/<token> | bash


Internally runs pip install --user easyssh.

Does not require root access.

12. Future Considerations

Encryption and revocation are deferred for now but must be addressed before production scale rollout.

Enterprise requirements (audit logs, compliance, enterprise contact workflow) will shape the roadmap.

Windows/macOS parity must be validated thoroughly.