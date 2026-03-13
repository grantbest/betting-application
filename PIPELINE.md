# BettingApp: CI Blueprint
## Strategy: Build & Publish

1. **Trigger:** Push to `main` or `dev`.
2. **Build:** GitHub Action builds Docker images for `engine` and `frontend`.
3. **Publish:** Push images to GitHub Container Registry (GHCR).
   - `ghcr.io/grantbest/betting-application/engine:main`
   - `ghcr.io/grantbest/betting-application/frontend:main`
4. **Notify:** Trigger the Homelab Control Plane to sync.
