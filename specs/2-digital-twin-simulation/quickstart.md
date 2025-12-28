# Quickstart: The Digital Twin (Gazebo & Unity) Documentation

## Prerequisites
- Node.js (version 18 or higher) - already installed from Module 1
- npm or yarn package manager - already installed from Module 1
- Git for version control - already installed

## Setup Instructions

### 1. Navigate to the existing Docusaurus project
```bash
cd frontend_book
```

### 2. Verify dependencies are installed
```bash
npm install
```

### 3. Create the digital twin module directory
```bash
mkdir -p docs/digital-twin-simulation
```

### 4. Create the three chapter files:
- `docs/digital-twin-simulation/chapter-1-digital-twins.md`
- `docs/digital-twin-simulation/chapter-2-environment-building.md`
- `docs/digital-twin-simulation/chapter-3-sensor-simulation.md`

### 5. Create module introduction
- `docs/digital-twin-simulation/intro.md`

### 6. Update the sidebar configuration in `sidebars.ts` to include the new module

### 7. Start the development server
```bash
npm start
```

## Content Creation Workflow

1. Write content for each chapter following the conceptual approach
2. Use Docusaurus markdown features for better documentation experience
3. Add navigation links between chapters
4. Test locally with `npm start`
5. Build for production with `npm run build`

## Deployment to GitHub Pages

1. The existing docusaurus.config.ts is already configured for GitHub Pages deployment
2. Build the site: `npm run build`
3. Deploy using GitHub Actions or manual process to GitHub Pages