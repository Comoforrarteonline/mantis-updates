# mantis-updates

Update-server estático para MantIS Replay. Sirve `releases.json` firmado HMAC vía GitHub Pages (branch `gh-pages`) para que todos los clientes MantIS Replay puedan consultar las versiones disponibles.

## URL pública

```
https://<owner>.github.io/mantis-updates/releases.json
```

## Flujo

1. **Tú** taggeas una versión en el repo `mantis-replay` (`git tag v1.1.0 && git push --tags`).
2. El workflow `release.yml` construye imágenes en GHCR, genera un entry para `releases.json` firmado con HMAC-SHA256, y lo mergea en este repo (branch `gh-pages`).
3. Todos los clientes MantIS Replay con `UPDATE_SERVER_URL=https://<owner>.github.io/mantis-updates/releases.json` hacen poll cada hora y reciben el banner cuando hay versión nueva.
4. El admin ejecuta `tools/updater/updater.sh` en su host → `docker compose pull` descarga de GHCR → health-check → rollback si falla.

## Estructura

- **main** (este branch): herramientas + documentación
  - `schema/releases.schema.json` — JSON schema de `releases.json`
  - `scripts/sign_release.py` — script de firma local (utilitario)
  - `.github/workflows/validate.yml` — valida PRs contra schema
- **gh-pages** (orphan): contenido servido
  - `releases.json`
  - `.nojekyll`

## Firma HMAC

Cada entry del array `releases` lleva un campo `signature` = HMAC-SHA256 del resto del objeto serializado canónicamente (claves ordenadas, sin whitespace). La clave de firma vive en el secret `UPDATE_SIGNING_KEY` del repo `mantis-replay`. Los clientes la configuran en su env var `UPDATE_SIGNING_KEY` para validar.

**Sin clave en el cliente** → cualquier release se acepta (modo dev/single-host).
**Con clave** → firmas inválidas se descartan y se loggean.

## Setup inicial

Desde local, tras crear el repo vacío en GitHub:

```bash
# 1. Clonar y preparar main
git clone git@github.com:<owner>/mantis-updates.git
cd mantis-updates
cp -r /ruta/a/mantis-updates-seed/* .
cp -r /ruta/a/mantis-updates-seed/.github .
git add .
git commit -m "chore: initial scaffold"
git push

# 2. Crear branch gh-pages como orphan con releases.json inicial
git checkout --orphan gh-pages
git rm -rf .
echo '{"releases": []}' > releases.json
touch .nojekyll
git add releases.json .nojekyll
git commit -m "chore: initial gh-pages"
git push -u origin gh-pages

# 3. Settings → Pages → Source: branch gh-pages, / root. Save.
```

## Secrets a configurar en el repo `mantis-replay`

| Secret | Cómo generar |
|--------|--------------|
| `UPDATE_SIGNING_KEY` | `openssl rand -hex 32` |
| `MANTIS_UPDATES_TOKEN` | Fine-grained PAT con scope `contents: write` sobre `mantis-updates` |
