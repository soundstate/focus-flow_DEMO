"""Tests for sessions router — verify no route path starts with /sessions/."""

import ast
import os
import pytest


def _extract_route_paths(filepath):
    """Parse a router file and extract all route decorator path arguments.

    This avoids importing the module (which has heavy dependencies) and
    instead uses static analysis to read the decorator string arguments.
    """
    with open(filepath, "r") as f:
        tree = ast.parse(f.read(), filename=filepath)

    paths = []
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) or isinstance(node, ast.AsyncFunctionDef):
            for decorator in node.decorator_list:
                # Decorators look like: @router.post("/sessions/")
                if isinstance(decorator, ast.Call):
                    func = decorator.func
                    # Match router.<method>(...) pattern
                    if (isinstance(func, ast.Attribute) and
                            isinstance(func.value, ast.Name) and
                            func.value.id == "router"):
                        # First positional arg is the path string
                        if decorator.args and isinstance(decorator.args[0], ast.Constant):
                            paths.append(decorator.args[0].value)
    return paths


# Path to the sessions router source
_ROUTER_FILE = os.path.normpath(
    os.path.join(os.path.dirname(__file__), "..", "routers", "sessions.py")
)


class TestSessionRouterPaths:
    """Verify the sessions router does not double-prefix routes."""

    def test_no_route_starts_with_sessions_prefix(self):
        """Routes on this router should NOT begin with '/sessions' because
        the router is already mounted at '/api/v1/sessions' in main.py.
        Having '/sessions/...' in the route decorator would create
        '/api/v1/sessions/sessions/...' paths.
        """
        paths = _extract_route_paths(_ROUTER_FILE)

        # Sanity: we should have found some routes
        assert len(paths) > 0, "No route paths found — is the parser working?"

        bad_routes = [p for p in paths if p.startswith("/sessions")]

        assert bad_routes == [], (
            f"These route paths still carry the /sessions prefix which will "
            f"cause double-prefixing: {bad_routes}"
        )
