#!/usr/bin/env python
# -*- mode: python -*-
#
# Copyright (C) 2006 - 2008 Imendio AB
#
# Build setup for creating frameworks against the 10.4 SDK. This file
# should normally not need any editing.
#
# Copy it or symlink it into ~/.jhbuildrc-cfw-10.4
#

_gtk_osx_prompt_prefix = "*CFW*"

modules = [
    "meta-gtk-osx-bootstrap",
    "meta-gtk-osx-core",
    "meta-gtk-osx-themes",
    "meta-gtk-osx-gtkmm",
    "libglade",
    "loudmouth",
    # "meta-gstreamer",
    "WebKit",
]

# Source and installation locations.
#
_root = os.path.expanduser("~/Source/gtkfw")
checkoutroot = os.path.join(_root, "source")
prefix = os.path.join(_root, "inst")


# Skip those for now.
#
skip.append("gst-plugins-ugly")
skip.append("gst-plugins-bad")
skip.append("gst-ffmpeg")
skip.append("faad")

# We build those as frameworks instead.
#
skip.append("gettext")
skip.append("glib")
skip.append("pango")
skip.append("atk")
skip.append("cairo")
skip.append("gtk+")
skip.append("ige-mac-integration")
skip.append("gtk-quartz-engine")
skip.append("gtk-engines")
skip.append("libglade")
skip.append("loudmouth")
skip.append("gnome-icon-theme")
skip.append("WebKit")
skip.append("cairomm")
skip.append("glibmm")
skip.append("pangomm")
skip.append("gtkmm")

# Not needed.
#
skip.append("waf")
skip.append("pyxml")
skip.append("automake-1.4")
skip.append("automake-1.8")
skip.append("tango-icon-theme")
skip.append("tango-icon-theme-extras")
