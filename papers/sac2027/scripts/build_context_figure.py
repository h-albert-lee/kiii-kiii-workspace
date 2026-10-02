"""Backward-compatible entry point for the shared SAC figure style."""
from build_publication_figures import style, load, context

if __name__ == "__main__":
    style()
    _, lookup, _, paired = load()
    context(lookup, paired)
