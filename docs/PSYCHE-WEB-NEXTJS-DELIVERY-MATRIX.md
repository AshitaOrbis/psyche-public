# `psyche-web` Dependency Delivery Matrix for `tier-3-nextjs`

## Summary Matrix

| Option | Dependency Spec | Pros | Cons | Risk | Recommendation |
| --- | --- | --- | --- | --- | --- |
| A. Link dependency | `link:../../../psyche/web` | Best local iteration speed, hot reload, matches Astro pattern | Breaks in isolated CI/Vercel builds, vulnerable to Syncthing timing issues, easy to drift into a non-reproducible install | High | Local dev only. Do not make this the committed production dependency. |
| B. Published npm package | `psyche-web@x.y.z` or `@scope/psyche-web@x.y.z` | CI-safe, Vercel-compatible, repo-independent, reproducible lockfile | Requires version bump + publish step, slower local iteration | Low | Default for production and CI. |
| C. Vendored tarball | `./vendor/psyche-web/psyche-web-x.y.z.tgz` | Works without registry/network, CI-safe if tarball is committed, repo-independent | Manual pack/update step, can go stale, no live cross-machine updates | Medium | Fallback when publishing is unavailable. |

## Shared Assumptions

- Source package lives at `../../../psyche/web`.
- Current package name is `psyche-web` in [`web/package.json`](../web/package.json).
- The package exports TypeScript source subpaths: `types`, `registry`, `tiers`, `scoring`, `init-lite`, `init-standard`.
- Because those exports point at `.ts` source, Next.js must transpile the package.
- Known `tier-3-nextjs` consumers from the review digest:
  - `src/app/psyche/assess/page.tsx`
  - `src/components/psyche/InstrumentRunner.tsx`
  - `src/components/psyche/PsycheProgress.tsx`
  - `src/components/psyche/PsycheResults.tsx`
- Keep `src/lib/psyche/api.ts` local to `tier-3-nextjs`. Only the shared assessment library moves to `psyche-web`.

## Shared Next.js Wiring

### `next.config.ts`

Use the installed package name in `transpilePackages`. If you publish under a scope, use the scoped name there too.

```ts
import type { NextConfig } from 'next';

const nextConfig: NextConfig = {
  transpilePackages: ['psyche-web'],
};

export default nextConfig;
```

### Import updates in `tier-3-nextjs`

Replace the duplicated local imports with package subpath imports:

```ts
import type { InstrumentResult, ItemResponse, Tier } from 'psyche-web/types';
import { getInstrumentsForTier } from 'psyche-web/tiers';
import { getInstrument, getAllInstruments } from 'psyche-web/registry';
import 'psyche-web/init-standard';
```

Known file-level replacements:

- `src/app/psyche/assess/page.tsx`
  - `@/lib/psyche/types` -> `psyche-web/types`
  - `@/lib/psyche/tiers` -> `psyche-web/tiers`
  - `@/lib/psyche/registry` -> `psyche-web/registry`
  - `@/lib/psyche/init-standard` -> `psyche-web/init-standard`
  - Keep `@/lib/psyche/api`
- `src/components/psyche/InstrumentRunner.tsx`
  - `@/lib/psyche/types` -> `psyche-web/types`
- `src/components/psyche/PsycheProgress.tsx`
  - `@/lib/psyche/types` -> `psyche-web/types`
- `src/components/psyche/PsycheResults.tsx`
  - `@/lib/psyche/types` -> `psyche-web/types`

Search/replace commands from the `tier-3-nextjs` repo root:

```bash
rg -l "@/lib/psyche/types" src | xargs perl -0pi -e "s#@/lib/psyche/types#psyche-web/types#g"
rg -l "@/lib/psyche/tiers" src | xargs perl -0pi -e "s#@/lib/psyche/tiers#psyche-web/tiers#g"
rg -l "@/lib/psyche/registry" src | xargs perl -0pi -e "s#@/lib/psyche/registry#psyche-web/registry#g"
rg -l "@/lib/psyche/init-standard" src | xargs perl -0pi -e "s#@/lib/psyche/init-standard#psyche-web/init-standard#g"
```

Verification after the import swap:

```bash
rg -n "@/lib/psyche/(types|tiers|registry|init-standard)" src
```

That command should return no matches.

## Option A: Link Dependency

### Implementation

Use this only as a local developer override. Do not rely on it for committed CI/Vercel installs.

Add the dependency in `tier-3-nextjs`:

```bash
pnpm add link:../../../psyche/web
```

Apply the shared `next.config.ts` and import updates above.

Recommended operating model:

1. Keep the committed dependency on Option B.
2. Apply Option A locally only while iterating.
3. Do not commit the `link:` spec to the main branch.

### Test locally

From `tier-3-nextjs`:

```bash
pnpm install
pnpm dev
pnpm build
```

Minimum smoke checks:

1. Open `/psyche/assess`.
2. Confirm instruments register and the first assessment page renders.
3. Change a file under `../../../psyche/web/src/instruments/` and confirm Next.js reflects the change.
4. Run the repo's tests if present:

```bash
pnpm test
```

### Test in CI

Option A itself should not be the CI path. The CI proof is that the committed repo still uses Option B and passes from a clean checkout:

```bash
CI=1 pnpm install --frozen-lockfile
CI=1 pnpm build
```

If your CI has lint/test stages, run those too:

```bash
CI=1 pnpm lint
CI=1 pnpm test
```

### Potential Failure Modes

- Vercel or other isolated CI runners cannot resolve `../../../psyche/web`.
- The symlink exists locally but points outside the checked-out repo on another machine.
- Syncthing copies partial changes into `psyche/web`, causing transient type/build failures.
- Lockfile churn from developers accidentally committing the `link:` spec.
- The local package shape changes underneath a running Next.js dev server and causes stale module state.

### Recovery Procedure

Switch back to the committed CI-safe dependency and reinstall:

```bash
git restore package.json pnpm-lock.yaml
pnpm install
pnpm build
```

If the branch intentionally committed the link experiment, revert that commit instead of restoring tracked files manually:

```bash
git revert <integration-commit-sha>
pnpm install
pnpm build
```

If Syncthing caused a half-synced state:

```bash
rm -rf node_modules
pnpm install
pnpm build
```

## Option B: Published npm Package

### Implementation

This is the production default.

Before first publish, harden the package in `../../../psyche/web`:

1. Change `"private": true` to `false`.
2. Publish under a real package identity. Prefer a scoped name such as `@ashitaorbis/psyche-web`.
3. Add a `files` allow-list so the package does not ship `dist/`, `public/`, `tests/`, or `tsconfig.tsbuildinfo` by accident.

Publish flow from `../../../psyche/web`:

```bash
pnpm version patch
npm publish
```

Add the dependency in `tier-3-nextjs`:

```bash
pnpm add @ashitaorbis/psyche-web@<version>
```

If you keep the unscoped name in a private registry, use:

```bash
pnpm add psyche-web@<version>
```

Update `next.config.ts`:

```ts
const nextConfig = {
  transpilePackages: ['@ashitaorbis/psyche-web'],
};

export default nextConfig;
```

Update imports to match the published package name:

```bash
rg -l "@/lib/psyche/types" src | xargs perl -0pi -e "s#@/lib/psyche/types#@ashitaorbis/psyche-web/types#g"
rg -l "@/lib/psyche/tiers" src | xargs perl -0pi -e "s#@/lib/psyche/tiers#@ashitaorbis/psyche-web/tiers#g"
rg -l "@/lib/psyche/registry" src | xargs perl -0pi -e "s#@/lib/psyche/registry#@ashitaorbis/psyche-web/registry#g"
rg -l "@/lib/psyche/init-standard" src | xargs perl -0pi -e "s#@/lib/psyche/init-standard#@ashitaorbis/psyche-web/init-standard#g"
```

### Test locally

From `tier-3-nextjs`:

```bash
pnpm install
pnpm dev
pnpm build
pnpm test
```

Also verify the published artifact before rollout:

```bash
pnpm view @ashitaorbis/psyche-web versions
```

### Test in CI

This should be the normal CI path:

```bash
CI=1 pnpm install --frozen-lockfile
CI=1 pnpm build
CI=1 pnpm test
```

If you want a Vercel-equivalent smoke build locally:

```bash
rm -rf node_modules
CI=1 pnpm install --frozen-lockfile
CI=1 pnpm build
```

### Potential Failure Modes

- `npm publish` fails because the package is still marked `private`.
- The published version is missing source files or subpath exports.
- CI gets `401`/`403`/`404` from the registry.
- A code change lands in `psyche/web` but the version was not bumped/published, so `tier-3-nextjs` installs stale code.
- `transpilePackages` uses the wrong package name after scoping.

### Recovery Procedure

If the published version is bad:

1. Publish a fixed patch version.
2. Update `tier-3-nextjs` to the new version.
3. Re-run CI from a clean install.

Commands:

```bash
cd ../../../psyche/web
pnpm version patch
npm publish

cd -  # back to tier-3-nextjs
pnpm add @ashitaorbis/psyche-web@<fixed-version>
pnpm install
pnpm build
```

If registry publishing is blocked, fall back to Option C immediately:

```bash
mkdir -p vendor/psyche-web
cd ../../../psyche/web
npm pack
mv psyche-web-*.tgz /path/to/tier-3-nextjs/vendor/psyche-web/
cd /path/to/tier-3-nextjs
pnpm add ./vendor/psyche-web/psyche-web-<version>.tgz
pnpm build
```

If the `tier-3-nextjs` integration commit itself must be rolled back:

```bash
git revert <integration-commit-sha>
pnpm install
pnpm build
```

## Option C: Vendored / Packed Tarball

### Implementation

Pack the local package from `../../../psyche/web`:

```bash
cd ../../../psyche/web
npm pack
```

Vendor the tarball into `tier-3-nextjs`:

```bash
mkdir -p vendor/psyche-web
mv ../../../psyche/web/psyche-web-*.tgz vendor/psyche-web/
pnpm add ./vendor/psyche-web/psyche-web-<version>.tgz
```

Apply the shared `next.config.ts` and import updates above.

### Test locally

From `tier-3-nextjs`:

```bash
pnpm install
pnpm dev
pnpm build
pnpm test
```

Tarball freshness check:

```bash
tar -tzf vendor/psyche-web/psyche-web-<version>.tgz | rg "src/instruments|src/scoring|package.json"
```

### Test in CI

This is CI-safe if the tarball is checked into the repo:

```bash
CI=1 pnpm install --frozen-lockfile
CI=1 pnpm build
CI=1 pnpm test
```

Also verify CI can run with networking disabled or registry unavailable, if your runner supports that constraint.

### Potential Failure Modes

- The tarball was not regenerated after a `psyche/web` change.
- The tarball file name changes but `package.json` still points at the old one.
- The tarball is not committed, so CI cannot resolve the path.
- Developers assume tarball installs are live-linked and forget to repack.

### Recovery Procedure

Regenerate the tarball and reinstall:

```bash
rm -f vendor/psyche-web/psyche-web-*.tgz
cd ../../../psyche/web
npm pack
mv psyche-web-*.tgz /path/to/tier-3-nextjs/vendor/psyche-web/

cd /path/to/tier-3-nextjs
pnpm add ./vendor/psyche-web/psyche-web-<new-version>.tgz
pnpm install
pnpm build
```

If the tarball path integration itself needs to be undone:

```bash
git revert <integration-commit-sha>
pnpm install
pnpm build
```

## Recommended Decision

- Use Option B as the committed dependency for `tier-3-nextjs`.
- Use Option A only as a temporary local override when you need same-minute iteration against `../../../psyche/web`.
- Use Option C when you need a registry-free, CI-safe fallback.

## Practical Rollout Order

1. Harden `psyche-web` for packaging: remove `private`, choose final package name, add a `files` allow-list.
2. Integrate `tier-3-nextjs` against Option B.
3. Keep the old `src/lib/psyche/*` copy around until one clean CI/Vercel deploy passes.
4. Delete the duplicate local `types` / `registry` / `tiers` / `init*` / `instruments` tree only after the new path is stable.
