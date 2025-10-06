# Claude Code Preferences for Ignition Stack Builder

**Last Updated**: 2025-10-06
**User**: Australian-based developer
**Primary Location**: Adelaide, South Australia

---

## General Preferences

### Localization
- **Timezone**: Australia/Adelaide (ACDT/ACST)
- **Date Format**: DD/MM/YYYY (Australian standard)
- **Time Format**: 24-hour format (HH:mm)
- **Currency**: AUD (Australian Dollars)
- **Measurements**: Metric system

### Default Settings
- **Default Timezone in App**: `Australia/Adelaide`
- **Backup Timezones**: Australia/Sydney, Australia/Melbourne, Australia/Brisbane, Australia/Perth

---

## UI/UX Layout Preferences

### General Layout Principles
1. **Maximize space efficiency** - Use 2-column layouts where possible to avoid wasted horizontal space
2. **Keep section headers on single lines** - Headers should not wrap to multiple lines
3. **Full-width elements** - User lists, tables, and complex components should span full width (`grid-column: 1 / -1`)
4. **Consistent spacing** - Balanced padding and gaps throughout the interface

### Specific Component Preferences

#### Configuration Forms
- **Layout**: 2-column grid (`grid-template-columns: 1fr 1fr`)
- **Label width**: 160px with left alignment
- **Label styling**: Font-weight 500, left-aligned
- **Gap**: 0.75rem vertical, 1.5rem horizontal
- **Input padding**: 0.6rem 0.75rem
- **Full-width inputs**: `width: 100%`

#### Section Headers
- **Must span full width** using `grid-column: 1 / -1`
- **No text wrapping** - Use `white-space: nowrap`
- **Clear visual separation** with border-top
- **Accent color** for emphasis

#### Integration Settings
- **Inline with related service** - Integration settings (OAuth, MQTT, etc.) should appear within the service configuration, not in separate sections
- **Visual separation**: 2px solid border-top in accent color
- **Context-specific**: Show only relevant settings for the selected service

#### User Management (Keycloak, etc.)
- **Add User/Import CSV buttons**: Should be part of the OAuth/SSO Settings section, not in a separate column
- **User list layout**: 2-column grid for user fields
  - Row 1: Username | Password
  - Row 2: Email | First Name
  - Row 3: Last Name | Temp Checkbox
- **Expand vertically** within container borders, not horizontally
- **Full-width container**: User list should span full width of parent

#### Responsive Behavior
- **Desktop (>1024px)**: 2-column layouts
- **Tablet (768-1024px)**: Single column fallback for config grids
- **Mobile (<768px)**: All grids collapse to single column

---

## Code Style Preferences

### CSS
- Use CSS custom properties (variables) for theming
- Support both dark and light modes
- Maintain consistent spacing units (0.5rem increments)
- Use grid layouts over flexbox for forms
- Include responsive breakpoints

### React/JSX
- Functional components with hooks
- Clear, descriptive variable names
- Inline styles only when dynamic or one-off
- CSS classes for reusable styling
- Comments for complex logic sections

### File Organization
- Keep related functionality together
- Use clear file naming conventions
- Document major changes in status files

---

## Integration-Specific Preferences

### Keycloak/OAuth Configuration
- Realm name settings should be prominent
- User management (Add User, Import CSV) integrated within OAuth/SSO settings
- Clear indication of which services will be configured
- Support for CSV import with format: `username,password,email,firstName,lastName`

### MQTT Broker Configuration
- TLS/MQTTS toggle clearly visible
- Optional authentication fields (username/password)
- Port configuration for both standard and TLS
- List affected services that will use the broker

### Reverse Proxy Configuration
- Base domain input
- HTTPS/TLS toggle
- Let's Encrypt email (conditional on HTTPS)
- Show which services will be routed

### Database Integration
- Auto-registration toggle for Ignition
- Database selection dropdown
- Connection instructions in generated README

---

## Documentation Preferences

### Project Documentation
- Maintain comprehensive PROJECT_STATUS.md
- Keep CONTINUITY.md updated for onboarding
- Document test results in TEST_EXECUTION_RESULTS.md
- Update TEST_PLAN.md when adding new features

### Code Comments
- Explain "why" not "what" in comments
- Document non-obvious business logic
- Mark sections clearly (e.g., `{/* OAuth/SSO Settings */}`)
- Include TODO items when work is deferred

### Commit Messages
- Clear, descriptive commit messages
- Reference issue/task numbers when applicable
- Group related changes in single commits

---

## Testing Preferences

### Backend Testing
- Automated test scripts (bash-based)
- API endpoint testing with curl
- JSON validation with Python
- Clear pass/fail indicators (✓/✗)
- Detailed result logging

### Frontend Testing
- Manual testing checklist for major features
- Cross-browser compatibility (Chrome, Firefox, Edge)
- Responsive design testing at multiple breakpoints
- Dark/light mode verification

### Integration Testing
- End-to-end stack generation and deployment
- Verify generated docker-compose.yml files
- Test downloaded ZIPs deploy successfully
- Validate service URLs and access

---

## Workflow Preferences

### Development Process
1. Understand the requirement clearly
2. Plan the implementation (use TodoWrite for complex tasks)
3. Make focused, incremental changes
4. Test immediately after changes
5. Update documentation
6. Rebuild containers when needed

### Docker Development
- Use `docker-compose build --no-cache` for CSS/config changes
- Restart individual services when possible (`docker-compose restart frontend`)
- Check logs with `docker-compose logs -f <service>`
- Clean rebuilds for major changes

### Git Workflow
- Keep working directory clean
- Commit related changes together
- Don't commit test files or temporary changes
- Use descriptive commit messages

---

## Communication Preferences

### Response Style
- Direct and concise
- Technical accuracy over verbosity
- Provide examples when helpful
- Confirm understanding before proceeding with major changes

### Problem Solving
- Ask clarifying questions when requirements are unclear
- Propose solutions with rationale
- Explain trade-offs when multiple approaches exist
- Prioritize user experience and maintainability

---

## Tools & Technologies

### Primary Stack
- **Frontend**: React 18, Vite, Axios, CSS Variables
- **Backend**: FastAPI, Python, Pydantic, PyYAML
- **DevOps**: Docker, Docker Compose, Nginx
- **Testing**: Bash scripts, curl, Python JSON parsing

### Development Environment
- **Platform**: Linux (WSL2)
- **Container Runtime**: Docker
- **Version Control**: Git
- **Editor**: (User preference not specified)

---

## Anti-Patterns to Avoid

### Layout
- ❌ Single-column layouts with excessive whitespace
- ❌ Text wrapping in section headers
- ❌ Inconsistent spacing between similar elements
- ❌ Components breaking out of container bounds horizontally

### Code
- ❌ Excessive inline styles when CSS classes would work
- ❌ Hard-coded values that should be configurable
- ❌ Inconsistent naming conventions
- ❌ Undocumented complex logic

### Workflow
- ❌ Making changes without understanding the impact
- ❌ Skipping testing after modifications
- ❌ Leaving documentation outdated
- ❌ Creating unnecessary new files when editing existing ones works

---

## Future Considerations

### Phase 2 Development
- Apply integration settings in docker-compose generation
- Generate configuration files from settings
- Create setup/initialization scripts
- Enhanced OAuth/SSO auto-configuration

### Planned Features
- Stack templates for common use cases
- Configuration validation and health checks
- Import/export stack configurations
- Advanced networking options

---

**Note**: This preferences file should be referenced at the start of each session to ensure consistency with user expectations and established patterns.
