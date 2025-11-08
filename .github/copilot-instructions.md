# GitHub Copilot Instructions

## Project Documentation

This project has comprehensive documentation organized hierarchically:

- **`/README.md`** - Top-level overview, project structure, and common workflows
- **`/infra/terraform/README.md`** - Infrastructure setup and Terraform operations
- **`/app/README.md`** - FastAPI application, endpoints, and build process
- **`/k8s/README.md`** - Kubernetes deployment and operations

## Instructions for AI Agents

### Before Making Changes

1. **Always read the relevant README first** based on what you're modifying:
   - Changing infrastructure? → Read `/infra/terraform/README.md`
   - Modifying app code? → Read `/app/README.md`
   - Updating K8s configs? → Read `/k8s/README.md`
   - Unclear scope? → Start with `/README.md`

2. **Understand the implications**:
   - What commands need to be run after the change?
   - Does this affect other parts of the system?
   - Are there deployment steps required?

### After Making Changes

1. **Update the relevant README**:
   - Document new features, endpoints, or resources
   - Update command examples if syntax changed
   - Add troubleshooting notes for known issues
   - Update workflow instructions if process changed

2. **Update related READMEs** if changes have cross-cutting concerns:
   - Infrastructure change affecting deployment? → Update both `/infra/terraform/README.md` and `/k8s/README.md`
   - New app endpoint? → Update `/app/README.md` and potentially `/README.md`

3. **Keep READMEs in sync**:
   - If you add a new configuration file, document it
   - If you change a workflow, update all references
   - Cross-reference related documentation

### Creating New Folders

**Only create a new README when creating a new subfolder** with substantial functionality:

1. Create the folder README with:
   - What the folder contains
   - Key files and their purposes
   - Common operations and commands
   - How it integrates with other parts

2. Update the parent README to:
   - Mention the new subfolder in the structure
   - Link to the new README
   - Explain when someone should consult it

### Documentation Standards

- **Be concise but complete** - Include what's needed, nothing more
- **Show commands, not just concepts** - Developers copy-paste
- **Explain when to run commands** - "After changing X, run Y"
- **Include troubleshooting** - Document common issues
- **Cross-reference** - Link to related documentation

### Example Workflow

```
1. User asks to add a new endpoint
2. Read /app/README.md to understand current structure
3. Modify app/main.py
4. Update /app/README.md:
   - Add endpoint to "What It Does" section
   - Add testing command example
   - Update deployment instructions if needed
5. Update /README.md if it's a significant user-facing feature
```

## Project-Specific Guidelines

### Terraform Changes
- Always document new resources in `/infra/terraform/README.md`
- Include commands to view/verify the resource after creation
- Note any DNS or external config required

### Application Changes
- Document new endpoints with their purpose and response format
- Update build/deploy commands if Docker or dependencies change
- Add testing examples for new functionality
- **Use GCP Cloud Build** for Docker image builds (no local Docker installed)

### Build & Deploy
- Use Cloud Build to build Docker images: `gcloud builds submit --tag IMAGE_URL`
- Version format: YYYY.MM.N (e.g., 2025.11.1)
- Never use local `docker build` commands

### Kubernetes Changes
- Document new manifests and their purpose
- Update deployment workflow if order or process changes
- Add troubleshooting for common issues with the new config
- **kubectl path**: Use `/opt/homebrew/share/google-cloud-sdk/bin/kubectl` (installed via gcloud)

### Configuration Changes
- Document what the config controls
- Show example values
- Explain when to change it and what commands to run afterward
