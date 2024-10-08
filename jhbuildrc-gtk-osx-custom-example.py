# -*- mode: python -*-
#!/usr/bin/env python

# All of jhbuild is Python, so there are all sorts of interesting
# things you can do to customize your build with python commands. This
# file is treated like a python __init__ file, so you can do all sorts
# of interesting things in it.

# The URL for repositories can be overridden. This is how you'd set
# your developer access to an SVN repo. It doesn't work, of course,
# because gnome has migrated to git.
#
# repos["svn.gnome.org"] = "svn+ssh://myusername@svn.gnome.org/svn/"

# You can set the default setup here.
#
# _gtk_osx_default_build = "fw-10.4"
#
# or set things up with an environment variable:

_jhb = os.environ.get("JHB")
if _jhb is None:
    # The default setup...
    # checkoutroot = os.path.expanduser("~/Source/gtk")
    # prefix = "/opt/gtk"
    pass
elif _jhb == "FW":
    # The framework build...
    # checkoutroot = os.path.expanduser("~/Source/gtk-fw")
    # prefix = "/opt/gtk-fw"
    pass
# Do note, though, that jhbuildrc-gtk-osx also uses $JHB to find
# another customization file that is loaded after this one. You can,
# of course, define your own environment variables for passing in
# parameters.

# The moduleset can be overridden.
#
# moduleset = "gtk-osx"

# As can the default modules to build.
#
# modules = [ "meta-gtk-osx-core", "meta-gstreamer" ]

# You can skip modules.
#
# skip.append("libglade")
#
# or put them back:
#
# if "libglade" in skip:
# 	skip.remove("libglade")

# Set this to True/False if you want to force using or not building
# and using python as part of jhbuild. If not set, the script will use
# the system python when building on 10.5 or newer only.
#
# _gtk_osx_use_jhbuild_python = True


# In addition, you can override _exec_prefix (used to set $M4 and
# $LIBTOOLIZE); by default it's set to prefix. You might want to reset
# it if you want to bootstrap to one directory and build in another
# (or more likely, several others). Mind that this is fiddly and
# requires tweaking a bunch of things to get autoconf to consistently
# find the right m4 files. Not really recommended. Similarly, you can
# override tarballdir so that you need download tarballs only once for
# multiple builds. This works just as you'd expect and can save quite
# a bit of time if you're maintaining several trees.

# _exec_prefix = os.path.join(os.path.expanduser("~"), "Source", "bootstrap")
# tarballdir = os.path.join(os.path.expanduser("~"), "Source", "Download")

# .jhbuildrc has a master function, setup_sdk(target, sdk_version,
# [architectures]) which sets up the build environment. You *must*
# call it or one of the functions (setup_sdk_10_4(),
# setup_ppc_build(), or setup_universal_build()) in jhbuildrc-custom.
#
# Target can be "10.4", "10.5", or "10.6". It sets
# MACOS_DEPLOYMENT_TARGET and the -macosx-version-min CFLAG.
#
# Setup_sdk can be "10.4u", "10.5", "10.6" or "native". "Native" will
# not set -sysroot in CFLAGS, so headers and dylibs will come from
# /usr instead of /Developer/SDKs/MacOSX_sdk.10.foo. If you are
# building for distribution, you probably want to use the lowest SDK
# which will successfully build you modules. The exception is if you
# are building under Tiger, because
# a) You're already using the lowest compatible SDK
# b) Cups 1.2.12, which you must install to build Gtk+, installs new
# headers and libraries into /usr but not into
# /Developer/SDKs/MacOSX_sdk_10.4u.
#
# Architectures is a list (pass the arguments in brackets) which can
# include the values "ppc", "i386", "x86_64", and _default_arch. That
# last one is a variable and doesn't get quotes. Don't pass multiple
# arguments directly to setup_sdk, though, because that would build
# universal and several packages need special handling to build
# universal. Use setup_universal_build instead. Do note, though, that
# while setup_universal_build will build successfully, the result will
# usually crash because of endianness problems with icon caches. Help
# is welcome to fix this. The special argument _default_arch is a
# variable set by jhbuildrc depending on what platform you're on. It
# doesn't set the -arch CFLAG at all, so your architecture will be
# whatever you get that way. Note that on Snow Leopard, if you are
# building on a 64-bit processor (Xeon, Core2duo, or one of the Core
# iFoo procesors), the architecure is x86_64 by default; otherwise
# it's i386, which is 32-bit. Be sure to read
# http://sourceforge.net/apps/trac/gtk-osx/wiki/SnowLeopard.
#
#  Set up a particular target and SDK: For default operation, set the
# architecture and SDK for the native machine:
_target = None
if _osx_version.startswith("8"):
    _target = "10.4"
elif _osx_version.startswith("9"):
    _target = "10.5"
elif _osx_version.startswith("10"):
    _target = "10.6"
elif _osx_version.startswith("11"):
    _target = "10.7"

setup_sdk(target=_target, sdk_version="native", architectures=[_default_arch])
#
# setup_sdk(target="10.4", sdk_version="10.4u", architectures=["i386"])
#
# or set up to cross-compile a ppc build from an intel machine:
#
# setup_ppc_build()
#
# or a universal build:
#
# setup_universal_build(target="10.5", sdk_version="10.5",
#                        architectures=["ppc", "i386"])


# Modify the arguments passed to configure:
#
# autogenargs["libglade"] = "--enable-static"
#
# or simply  add to them:
#
# append_autogenargs("libglade", "--enable-static")
#
# Note that in either case the args will be added *after* the args in
# the module's autogenargs attribute.
#
# Tell Git to use a different module and branch (not tag!):
#
# branches["gtk-engines"] = ("gtk-css-engine", "bzr")
#
# Or just switch branches
#
# branches["gtk+"] = (None, "gtk-2-18")
#
# Tarballs take a whole URL for branches:
#
# branches["python"] = "http://www.python.org/ftp/python/2.6.4/Python-2.6.4.tar.bz2"
#
# Note that if the module has hash, md5sum, or size attributes and the
# branch download doesn't match, jhbuild will error out. Open a shell,
# untar the tarball yourself, quit the shell, and select "ignore
# error". Don't try this with modules that need patches unless you're
# sure that the updated version doesn't need them.
#
# Set an environment variable:
#
# os.environ["CC"] = "/usr/bin/gcc-4.0"


# And more...
