"""Path safety utilities for preventing path traversal attacks."""

from __future__ import annotations

import tempfile
from pathlib import Path

from arbcore.errors import SnapshotError


def _resolve_safe_path(
    path: str | Path,
    allowed_roots: list[str | Path] | None = None,
    *,
    allow_symlinks: bool = False,
    base_name_only: bool = False,
) -> Path:
    """
    Resolve a path safely, ensuring it's within allowed boundaries.

    Args:
        path: The path to validate and resolve
        allowed_roots: List of root directories that the path must be within.
                      If None, defaults to [current working directory, system temp directory]
        allow_symlinks: Whether to allow symlinks (default: False for security)
        base_name_only: If True, only the basename is used, resolved against the first allowed root

    Returns:
        The resolved absolute Path that is guaranteed to be within one of the allowed roots

    Raises:
        SnapshotError: If the path is not safe (outside all allowed roots,
        is a symlink when not allowed, etc.)
    """
    if allowed_roots is None:
        # Default to current working directory and system temp directory
        allowed_roots = [Path.cwd(), Path(tempfile.gettempdir())]
    
    # Convert all allowed roots to resolved absolute paths
    allowed_root_paths = []
    for root in allowed_roots:
        try:
            allowed_root_paths.append(Path(root).resolve())
        except (OSError, RuntimeError):
            # If we can't resolve a root, skip it
            continue
    
    if not allowed_root_paths:
        # Fallback to just current working directory if we couldn't resolve any roots
        allowed_root_paths = [Path.cwd().resolve()]
    
    if base_name_only:
        # Only use the basename, resolved against the first allowed root
        path_obj = allowed_root_paths[0] / Path(path).name
    else:
        path_obj = Path(path)
    
    # Resolve to absolute path, following symlinks
    try:
        resolved_path = path_obj.resolve()
    except (OSError, RuntimeError) as exc:
        raise SnapshotError(f"cannot resolve path {path}: {exc}") from exc
    
    # Check for symlinks if not allowed
    if not allow_symlinks and path_obj.is_symlink():
        raise SnapshotError(f"symlinks are not allowed: {path}")
    
    # Also check if any parent component is a symlink (more thorough)
    # This prevents attacks like: allowed/../../symlink_to_etc/passwd
    # where the symlink is deeper in the path
    if not allow_symlinks:
        parts = Path(path).parts
        for i in range(len(parts)):
            partial_path = Path(*parts[:i+1])
            if partial_path.exists() and partial_path.is_symlink():
                raise SnapshotError(f"symlinks are not allowed in path: {path}")
    
    # Ensure the resolved path is within at least one of the allowed roots
    for allowed_root in allowed_root_paths:
        try:
            resolved_path.relative_to(allowed_root)
            # If we get here, the path is within this allowed root
            return resolved_path
        except ValueError:
            # This root doesn't contain the path, try the next one
            continue
    
    # If we got here, the path is not within any allowed root
    allowed_roots_str = ", ".join(str(root) for root in allowed_root_paths)
    raise SnapshotError(
        f"path {path} resolves to {resolved_path} which is outside allowed "
        f"directories: {allowed_roots_str}"
    )