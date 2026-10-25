# CLAUDE.md — Frontend

Rules for AI coding agents working in `frontend/`. Project rules: [../CLAUDE.md](../CLAUDE.md).

## Sources of truth

- Stack, pages, rendering and UI rules: [docs/frontend/DESIGN.md](../docs/frontend/DESIGN.md).
- Folders and files: [docs/frontend/STRUCTURE.md](../docs/frontend/STRUCTURE.md).
- Types, form validation and browser storage: [docs/frontend/SCHEMAS.md](../docs/frontend/SCHEMAS.md).
- Page behavior and texts: [docs/features/](../docs/features/).

## Package manager

- pnpm is the only package manager. Do not use npm or yarn and do not commit `package-lock.json`.
- Install dependencies with `pnpm install` and add packages with `pnpm add`.

## Clean code

- A file has at most 200 lines. If a change does not fit, stop and propose to the Engineer how to split the file before writing it.
- Names of variables, functions, classes, components and files describe their purpose. Single letter and abbreviated names such as `a`, `b`, `c1`, `tmp`, `data2` are not allowed.
- No dead code, unused imports, unused variables, debug output (`console.log`) or commented out code.

## Code rules

- Read the Next.js guide in `node_modules/next/dist/docs/` before using a Next.js API.
- Route files in `app/` only compose components from `features/<page>/`.
- Page texts are static strings in the JSX, without text constants or translation keys.
- No multiline conditional blocks inside the returned JSX (`{condition ? (<...>) : null}`, `{condition && (<...>)}`). Build the block in a memoized variable before `return` and render only the variable:

  ```tsx
  const listingFormJSX = useMemo(() => {
    if (!generated) {
      return null;
    }
    return <form>...</form>;
  }, [generated]);

  return <div>{listingFormJSX}</div>;
  ```

  The variable name ends with `JSX`. The `useMemo` dependency list contains every value the block reads. A nested condition inside such a block is also moved to its own variable. Where hooks are not available (Server Components, components shared with Server Components, render callbacks such as `Controller.render`), the block goes to a plain `const` before `return`.
- API calls and operations on entities live in `services/<Entity>Service.ts` and go through `utils/apiClient.ts`. Services return `Api.Response` and do not throw: [SCHEMAS.md](../docs/frontend/SCHEMAS.md#response). Features and stores call services. API types are global namespaces `Entity` and `Api` in `types/*.d.ts` and are used without imports: [SCHEMAS.md](../docs/frontend/SCHEMAS.md#types).
- Tests are placed in the `__test__/` folder of their module, test data in `mocks/`: [STRUCTURE.md](../docs/frontend/STRUCTURE.md#tests). Run with `pnpm test`.
- Zod schemas live in `schemas/`. Types of the API data are inferred from them.
- Before finishing a change, run `pnpm lint`, `pnpm typecheck`, `pnpm test` and `pnpm build`.
