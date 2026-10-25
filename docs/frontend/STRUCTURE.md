# Frontend Structure

Architecture and rendering rules: [DESIGN.md](DESIGN.md).

```
frontend/
  app/
  public/
  shared/
    config/
    features/
    ui/
    utils/
  stores/
  themes/
    theme.css
  types/
  utils/
  CLAUDE.md
  .env
```

- `app`: Next.js App Router routes. Route files only compose components from `shared/features`.
- `public`: static files.
- `shared/config`: application constants and settings.
- `shared/features`: feature modules, one folder per page.
- `shared/ui`: reusable UI components built on HeroUI.
- `shared/utils`: helpers used by feature modules.
- `stores`: Zustand stores.
- `themes`: HeroUI theme, CSS variables.
- `types`: shared TypeScript types.
- `utils`: general helpers (class names, text formatting).
- `CLAUDE.md`: rules for AI coding agents working in the Frontend.
- `.env`: environment variables.
