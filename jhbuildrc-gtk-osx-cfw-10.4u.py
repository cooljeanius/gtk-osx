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
    "libglade",
    "loudmouth",
    # "meta-gstreamer",
    "WebKit",
]
# moduleset = "gtk-osx-universal" Use the primary moduleset

alwaysautogen = False

# Source and installation locations.
#
_root = os.path.expanduser("~/Source/create-gtk-fw")
checkoutroot = os.path.join(_root, "source")
prefix = os.path.join(_root, "inst")

_sdkdir = setup_sdk_10_4()

# Needed to get the various sublibraries to find and use the same
# symbols.
#
environ_append("LDFLAGS", "-Wl,-flat_namespace")

# Need to point some modules to the right place so we don't pick up
# things from /usr/lib.
#
# append_autogenargs("gettext", "--with-libiconv-prefix=" + _sdkdir + "/usr")

# For unknown reasons, iconv is not picked up correctly without this
# (possibly due to using -flat_namespace....).
#
# append_autogenargs('glib', ' --with-libiconv=gnu')

# environ_append('CC', '/usr/bin/gcc-4.0')
# environ_append('CPP', '/usr/bin/cpp-4.0')
# environ_append('CXX', '/usr/bin/g++-4.0')

_cflags = "-O2 -isysroot " + _sdkdir + " -mmacosx-version-min=10.4"
_cxxflags = _cflags
_cppflags = "-I" + prefix + "/include -isysroot " + _sdkdir
_ldflags = (
    "-L" + prefix + "/lib -Wl,-syslibroot," + _sdkdir + " -mmacosx-version-min=10.4"
)

environ_append("CFLAGS", _cflags + " -arch ppc -arch i386")
environ_append("CXXFLAGS", _cxxflags + " -arch ppc -arch i386")
environ_append("CPPFLAGS", _cppflags)
environ_append("LDFLAGS", _ldflags + " -arch ppc -arch i386")
environ_append("FFLAGS", "-O2")

autogenargs += " --disable-dependency-tracking"

_ppc_args = (
    "CFLAGS='"
    + _cflags
    + " -arch ppc' CXXFLAGS='"
    + _cxxflags
    + " -arch ppc' LDFLAGS='"
    + _ldflags
    + " -arch ppc -headerpad_max_install_names' --host=powerpc-apple-darwin "
)

_i386_args = (
    "CFLAGS='"
    + _cflags
    + " -arch i386' CXXFLAGS='"
    + _cxxflags
    + " -arch i386' LDFLAGS='"
    + _ldflags
    + ",-arch i386,-headerpad_max_install_names' --host=i386-apple-darwin "
)

_genmarshal = (
    "/Library/Frameworks/GLib.framework/Versions/2/Resources/dev/bin/glib-genmarshal"
)

append_autogenargs(
    "glib-ppc",
    _ppc_args
    + " glib_cv_uscore=no ac_cv_func_posix_getgrgid_r=yes glib_cv_stack_grows=no ac_cv_func_posix_getpwuid_r=yes ac_cv_c_bigendian=yes GLIB_GENMARSHAL="
    + _genmarshal,
)

append_autogenargs(
    "glib-i386",
    _i386_args
    + " glib_cv_uscore=no ac_cv_func_posix_getgrgid_r=yes glib_cv_stack_grows=no ac_cv_func_posix_getpwuid_r=yes ac_cv_c_bigendian=no GLIB_GENMARSHAL="
    + _genmarshal,
)

_update_icon_cache = "/Library/Frameworks/Gtk.framework/Versions/2/Resources/dev/bin/gtk-update-icon-cache"
# _pixbuf_csource = "/Library/Frameworks/Gtk.framework/Versions/2/Resources/dev/bin/gdk-pixbuf-csource"
_pixbuf_csource = (
    checkoutroot
    + "/gtk-u/ppc/gdk-pixbuf/gdk-pixbuf-csource GDK_PIXBUF_MODULE_FILE="
    + checkoutroot
    + "/gtk-u/ppc/gdk-pixbuf/gdk-pixbuf.loaders "
)

append_autogenargs(
    "gtk-ppc",
    _ppc_args
    + " --with-gdktarget=quartz --without-libjasper --disable-glibtest gio_can_sniff='yes' GTK_UPDATE_ICON_CACHE="
    + _update_icon_cache
    + " GDK_PIXBUF_CSOURCE="
    + _pixbuf_csource,
)
append_autogenargs(
    "gtk-i386",
    _i386_args
    + " --with-gdktarget=quartz --without-libjasper --disable-glibtest gio_can_sniff='yes' GTK_UPDATE_ICON_CACHE="
    + _update_icon_cache
    + " GDK_PIXBUF_CSOURCE="
    + _pixbuf_csource,
)


# Replace trunk with tags/branches for some modules.
#
# set_branch("glib", "tags/GLIB_2_18_2")
# set_branch("gtk+", "tags/GTK_2_14_4")
# set_branch("atk", "tags/ATK_1_24_0")
# set_branch("pango", "tags/PANGO_1_22_2")
# set_branch("libglade", "tags/LIBGLADE_2_6_2")
# set_branch("gtk-engines", "tags/GTK_ENGINES_2_16_1")
# set_branch("intltool", "tags/INTLTOOL_0_40_4")
# set_branch("gnome-icon-theme", "tags/GNOME_ICON_THEME_2_24_0")
# Try if this is new enough: set_branch("gtk-doc", "tags/GTK_DOC_1_10")

# Python modules.
#
# set_branch("pygobject", "tags/PYGOBJECT_2_14_2")
# set_branch("pygtk", "tags/PYGTK_2_12_1")

# Skip those for now.
#
skip.append("gst-plugins-ugly")
skip.append("gst-plugins-bad")
skip.append("gst-ffmpeg")
skip.append("faad")

# We build those as frameworks instead.
#
# skip.append("gettext")
# skip.append("glib")
# skip.append("pango")
# skip.append("atk")
# skip.append("cairo")
# skip.append("gtk+")
# skip.append("ige-mac-integration")
# skip.append("gtk-engines")
# skip.append("libglade")
# skip.append("loudmouth")
# skip.append("gnome-icon-theme")
# skip.append("WebKit")

# Not needed.
#
skip.append("waf")
skip.append("pyxml")
skip.append("automake-1.4")
skip.append("automake-1.8")
skip.append("tango-icon-theme")
skip.append("tango-icon-theme-extras")
