# -*- mode: python -*-
#!/usr/bin/env python
moduleset = os.path.join(
    os.environ["HOME"], "gtk-osx-build/modulesets-stable/gtk-osx.modules"
)
modules = [
    "meta-gtk-osx-bootstrap",
    "meta-gtk-osx-core",
    "meta-gtk-osx-freetype",
    "meta-gstreamer",
    "meta-gtk-osx-gtkmm",
    "meta-gtk-osx-python",
    "meta-gtk-osx-themes",
    "meta-gtk-osx-random",
]
build_policy = "updated-deps"
# Pass --ignore-system to build python
