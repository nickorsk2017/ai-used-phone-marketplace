# EXEC — 2026-10-25-make-up-all

## v1
exec_version: 1

### Summary
- R1: `up-all` runs `$(MAKE) -j2 backend-dev frontend-dev`: one terminal, both servers in the same process group, Ctrl+C stops both. Listed in `help` and `.PHONY`.

### Changed files
- Makefile
