#!/usr/bin/env python
# -*- mode: python -*-
#
# Copyright (C) 2006 - 2008 Imendio AB
#
# Build setup for using the frameworks for GLib, Cairo, GTK+ etc.
#

_gtk_osx_prompt_prefix = "FW"

# Source and installation locations.
#
_root = os.path.expanduser("~/Source/gtk-fw")
checkoutroot = os.path.join(_root, "source")
prefix = os.path.join(_root, "inst")

_sdkdir = setup_sdk_10_4()

# Skip those for now.
#
skip.append("gst-plugins-ugly")
skip.append("gst-plugins-bad")
skip.append("gst-ffmpeg")
skip.append("faad")

# Skip everything that is included in our frameworks.
#
skip.append("gettext")
skip.append("pkg-config")
skip.append("glib")
skip.append("pango")
skip.append("atk")
skip.append("cairo")
skip.append("gtk+")
skip.append("ige-mac-integration")
skip.append("gtk-engines")
skip.append("hicolor-icon-theme")
skip.append("gnome-icon-theme")
skip.append("gettext")
skip.append("intltool")
skip.append("libpng")
skip.append("libtiff")
skip.append("libjpeg")
skip.append("libglade")
skip.append("loudmouth")
skip.append("WebKit")

# Not needed.
#
skip.append("waf")
skip.append("pyxml")
skip.append("automake-1.4")
skip.append("automake-1.7")
skip.append("automake-1.8")
skip.append("tango-icon-theme")
skip.append("tango-icon-theme-extras")

# Setup jhbuild to point to frameworks.
#
environ_prepend("JHB_PREPEND_FRAMEWORKS", "/Library/Frameworks/GLib.framework", ":")
environ_prepend("JHB_PREPEND_FRAMEWORKS", "/Library/Frameworks/Cairo.framework", ":")
environ_prepend("JHB_PREPEND_FRAMEWORKS", "/Library/Frameworks/Gtk.framework", ":")
environ_prepend("JHB_PREPEND_FRAMEWORKS", "/Library/Frameworks/Libglade.framework", ":")
environ_prepend(
    "JHB_PREPEND_FRAMEWORKS", "/Library/Frameworks/Loudmouth.framework", ":"
)
environ_prepend(
    "JHB_PREPEND_FRAMEWORKS", "/Library/Frameworks/WebKitGtk.framework", ":"
)
