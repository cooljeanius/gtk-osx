#!/usr/bin/env python
# -*- mode: python -*-
#
# Copyright (C) 2006, 2007, 2008 Imendio AB
# Copyright 2009, 2010, 2011 John Ralls, Fremont, CA
#
# Default setup for building GTK+ on Mac OS X. Note that you should
# normally never need to edit this file. Any custom settings should be
# done in ~/.jhbuildrc-custom.
#
# Specific builds can be set up by creating files named
# ~/.jhbuildrc-<build>. When setting the environment variable JHB to
# such a name, the corresponding rc file will be read (e.g.:
# JHB=mybuild jhbuild shell).
#
# Use .jhbuildrc-custom to override the moduleset, modules to build,
# the source checkout location, installation prefix, or svn usernames
# etc.
#
# Please email richard@imendio.com if you have suggestions for
# improving this setup, or have any patches that you would like to get
# included.

import sys
import errno
import re


# Register an extra command to get the checkout dir for a module.
#
import jhbuild


class _cmd_get_srcdir(jhbuild.commands.Command):
    doc = 'Display information about one or more modules'

    from jhbuild.errors import FatalError

    name = 'gtk-osx-get-srcdir'
    usage_args = 'module'

    def run(self, config, options, args):
        module_set = jhbuild.moduleset.load(config)

        if args:
            modname = args[0]
            try:
                module = module_set.get_module(modname, ignore_case=True)
            except KeyError:
                raise FatalError(_('unknown module %s') % modname)
            print module.get_srcdir(None)
        else:
            raise FatalError('no module specified')


jhbuild.commands.register_command(_cmd_get_srcdir)


class _getenv(jhbuild.commands.Command):
    doc = "Retrieve an environment variable set within jhbuild"

    name = "gtk-osx-getenv"
    usage_args = 'envvar'

    def run(self, config, options, args):
     #       module_set = jhbuild.moduleset.load(config)

        if not args:
            raise FatalError("No environment variable")

        var = args[0]
        if not os.environ.has_key(var):
            raise FatalError("variable " + var +
                             " not defined in jhbuild environment")
        print os.environ[var]


jhbuild.commands.register_command(_getenv)


# Find out what we're building on
_default_arch = ""
_osx_version = 0.0


def osx_ver():
    global _default_arch, _osx_version
    vstring = os.popen("uname -r").read().strip()
    mstring = os.popen("machine").read().strip()
    exp = re.compile(r'(\d+\.\d+)\.\d+')
    vernum = exp.match(vstring)
    _osx_version = float(vernum.group(1)) - 4.0

    x64bit = os.popen(
        "sysctl hw.cpu64bit_capable").read().strip().endswith("1")
    if x64bit and _osx_version >= 6.0:
        _default_arch = "x86_64"
    elif mstring.startswith("ppc"):
        _default_arch = "ppc"
    else:
        _default_arch = "i386"


def xcode_ver():
    ver = ver = os.popen("xcodebuild -version").read().strip()
    exp = re.compile(r'Xcode (\d+\.\d+)')
    vernum = exp.match(ver)
    if vernum:
        return float(vernum.group(1))
    else:
        return 3.0


osx_ver()
_xcodeversion = xcode_ver()
_xcodepath = None
if _xcodeversion >= 4.3:
    _xcodepath = "/Applications/Xcode.app/Contents"
# For XCode4 we need to disable ppc when building perl:
if _xcodeversion >= 4.0:
    os.environ["ARCHFLAGS"] = "-arch i386 -arch x86_64"

# print "Default Architecture %s\n" % _default_arch
# Some utitily functions used here and in custom files:
#


def environ_append(key, value, separator=' '):
    old_value = os.environ.get(key)
    if old_value is not None:
        value = old_value + separator + value
    os.environ[key] = value


def environ_prepend(key, value, separator=' '):
    old_value = os.environ.get(key)
    if old_value is not None:
        value = value + separator + old_value
    os.environ[key] = value


def parse_custom_argument(key):
    for i, arg in enumerate(sys.argv[:-1]):
        if arg == key:
            return sys.argv[i+1]
    return None


def append_autogenargs(module, args):
    old_value = module_autogenargs.get(module, autogenargs)
    module_autogenargs[module] = old_value + " " + args


def remove_autogenargs(module, args):
    arg_string = module_autogenargs.get(module, autogenargs)
    module_autogenargs[module] = arg_string.replace(args, "")

# Call either setup_debug or setup_release in your .jhbuildrc-custom
# or other customization file to get the compilation flags.


def setup_debug():
    global autogenargs
# The enable-debug option generally turns on ASSERTS, which can slow
# down code and in the case of WebKit, breaks it on OSX because of
# threading problems. It's better to set it for individual packages
# with append_autogenargs().

#    autogenargs = autogenargs + " --enable-debug=yes"

# Gtk+ crashes in gdk_window_quartz_raise() -- in a call to [NSWindow
# orderFront:] if gcc is passed -O0 for 64-bit compilation. The old
# stabs+ debug format also doesn't work. See Snow Leopard in the Wiki
# for more information about debugging.
    environ_prepend('CFLAGS', "-O0 -ggdb3")
    environ_prepend('CXXFLAGS', "-O0 -ggdb3")
    environ_prepend('OBJCFLAGS', "-O0 -ggdb3")


def setup_release():
    environ_prepend('CFLAGS', "-O2")
    environ_prepend('CXXFLAGS', "-O2")
    environ_prepend('OBJCFLAGS', "-O2")

# Set up the environment for building against particular SDK.
#

# These first two are just utility functions.


def make_sdk_name(sdk_version):
    return "MacOSX" + sdk_version + ".sdk"


def get_sdkdir(sdk_name):
    platformpath = None
    sdkpath = "Developer/SDKs"
    if _xcodeversion >= 4.3:
        platformpath = "Developer/Platforms/MacOSX.platform"
    if _xcodepath and platformpath:
        sdkdir = os.path.join(_xcodepath, platformpath, sdkpath, sdk_name)
    else:
        sdkdir = os.path.join("/", sdkpath, sdk_name)
    return sdkdir
#
# This is the workhorse of the setup. Call this function with the
# target OSX version (10.4, 10.5, 10.6, or 10.7), the sdk version you want
# to use (10.4u, 10.5, 10.6 or 10.7), and a list of architectures. As you
# can see, the architectures defaults to a single build of i386 or
# ppc, depending on your machine. I386 is chosen for intel
# architectures as a default to ensure compatibility: 64-bit hasn't
# been tested much on 10.5 and not all dependent packages are ready
# for it (including ige-mac-integration).
#
# If you want to build more than one architecture, don't use setup_sdk
# directly: Use setup_universal (see below) instead.
#
# Notes on 64-bit compilation: This function does what's required for
# the packages that can be built for 64-bit; unfortunately, there are
# still some issues in the underlying code that the gtk+ devs are
# working on.
#
# There's also one Apple issue: /usr/lib/libiconv.dylib doesn't define
# a symbol that glib needs in the x86_64 image *only*, so if you're
# building a 64-bit image, either standalone or as part of a universal
# binary, you need to build gettext-fw before meta-gtk-osx-bootstrap.
#


def setup_sdk(target, sdk_version, architectures=[_default_arch]):

    os.environ["MACOSX_DEPLOYMENT_TARGET"] = target
    sdkdir = None

    if sdk_version != "native":
        sdkdir = get_sdkdir(make_sdk_name(sdk_version))
        # Seems like we need this since many libraries otherwise only look for
        # various dependencies (e.g. libiconv) in /usr/lib, hence pulling in
        # the wrong -L that doesn't have fat binaries on pre-10.5.
        #
        environ_prepend("LDFLAGS", "-L" + sdkdir + "/usr/lib")
        environ_prepend("CFLAGS", "-I" + sdkdir + "/usr/include")
        environ_prepend("CXXFLAGS", "-I" + sdkdir + "/usr/include")
        environ_prepend("OBJCFLAGS", "-I" + sdkdir + "/usr/include")
        environ_prepend("CPPFLAGS", "-I" + sdkdir + "/usr/include")

        # It looks like -isysroot is broken when building on 10.4, causing link
        # problems. But we don't really need to set it for 10.4 so just
        # skip that.
        #

# Apple Documentation says that "-syslibroot" is the arg to pass to the
# linker, but we are using the compiler to control the linker, and
# everything seems to be working correctly.
        if not _osx_version < 5.0:
            environ_append("CFLAGS", "-isysroot " + sdkdir)
            environ_append("CXXFLAGS", "-isysroot " + sdkdir)
            environ_append("OBJCFLAGS", "-isysroot " + sdkdir)
            environ_append("LDFLAGS", "-isysroot " + sdkdir)

            # To pick up cups-config from the right place.
            #
            os.environ["CUPS_CONFIG"] = os.path.join(sdkdir,
                                                     "usr/bin/cups-config")

    # Glib and autoconf-2.63 have issues with endianness
    #
    if architectures == ["i386"] or architectures == ["x86_64"]:
        append_autogenargs("glib", "ac_cv_c_bigendian=no")
    elif architectures == ["ppc"]:
        append_autogenargs("glib", "ac_cv_c_bigendian=yes")
        append_autogenargs("gmp", "CFLAGS=-force_cpusubtype_ALL $CFLAGS")

    # For unknown reasons, iconv is not picked up correctly without this
    #
        append_autogenargs('glib', ' --with-libiconv=gnu')

    # If we're building on Snow Leopard for 32-bit, we need to make
    # sure that Perl and Python are working in 32-bit mode.
    #
    if _osx_version >= 6.0 and architectures == ["i386"]:
        os.environ["VERSIONER_PERL_PREFER_32_BIT"] = "yes"
        os.environ["VERSIONER_PYTHON_PREFER_32_BIT"] = "yes"

    # SDK 10.4 doesn't support gcc4.2.
    if _xcodeversion == 3.0 or sdk_version == "10.4u":
        os.environ["CC"] = "/usr/bin/gcc-4.0"
        os.environ["CXX"] = "/usr/bin/g++-4.0"
    elif _osx_version >= 7.0 and _xcodeversion > 4.0:
        os.environ["CC"] = "/usr/bin/llvm-gcc-4.2"
        os.environ["CXX"] = "/usr/bin/llvm-g++-4.2"
    else:
        os.environ["CC"] = "/usr/bin/gcc-4.2"
        os.environ["CXX"] = "/usr/bin/g++-4.2"

    # Set the -arch flags for everything we're building.
    #
    for arch in architectures:
        environ_prepend("CFLAGS", "-arch " + arch)
        environ_prepend("CXXFLAGS", "-arch " + arch)
        environ_prepend("OBJCFLAGS", "-arch " + arch)
        environ_prepend("LDFLAGS", "-arch " + arch)
    # For intel, set glib's build parameter so that it builds the
    # correct atomic asm functions
    #
    if architectures == ["i386"]:
        append_autogenargs("glib", "--build=i486-apple-darwin")
        append_autogenargs("gmp", "ABI=32")
        append_autogenargs("libffi", "--build=i486-apple-darwin")
        append_autogenargs("liboil", "--host=i486-apple-darwin")
    elif architectures == ["x86_64"]:
        append_autogenargs("glib", "--build=x86_64-apple-darwin")
        append_autogenargs("gmp", "ABI=64")
        append_autogenargs("libffi", "--build=x86_64-apple-darwin")
        append_autogenargs("liboil", "--host=x86_64-apple-darwin")

    # Tiger has a somewhat messed-up resolv.h, so we need to explicitly
    # link libresolv:
    if _osx_version < 5.0 or sdk_version.startswith("10.4"):
        append_autogenargs("glib", 'LIBS="-lresolv"')

    # gettext-fw rebuilds gettext with an in-tree libiconv to get
    # around the Apple-provided one not defining _libiconv_init for
    # x86_64
    append_autogenargs("gettext-fw", "--with-libiconv-prefix=" + prefix)

    environ_append("CFLAGS", "-mmacosx-version-min=" + target)
    environ_append("CXXFLAGS", "-mmacosx-version-min=" + target)
    environ_append("OBJCFLAGS", "-mmacosx-version-min=" + target)
    environ_append("LDFLAGS", "-mmacosx-version-min=" + target)

    # Overcome Python's obnoxious misconfiguration of portable builds
    if len(architectures) == 1:
        os.environ["BUILDCFLAGS"] = os.environ["CFLAGS"]
    # Glib wants to use posix_memalign if it's available, but it's only
    # available after 10.6, and there's no weak linking support for it:
    if ((target == "10.4" or target == "10.5")
        and (sdk_version == "10.6" or sdk_version == "10.7"
             or sdk_version == "native"
             and (_osx_version >= 6.0))):
        append_autogenargs("glib", "ac_cv_compliant_posix_memalign=no")

    append_autogenargs("gnutls", "--disable-guile")

    # Guile doesn't handle optimization well with llvm-gcc
    if _osx_version >= 7.0 and _xcodeversion > 4.0:
        append_autogenargs("guile", 'CFLAGS="$CFLAGS -O1"')

    return sdkdir
# This is a convenience function for older .jhbuildrc-customs.


def setup_sdk_10_4():
    print "*** Using setup_sdk_10_4() is deprecated. Use setup_sdk instead. ***"
    if _default_arch == "x86_64":
        return setup_sdk("10.4", "10.4u", ["i386"])
    return setup_sdk("10.4", "10.4u")

# For cross-compiling on an intel system. The need to build tool
# packages universal for cross-compilation means that it will take
# longer than necessary on a ppc machine, so just call
# setup_sdk("10.4", "10.4", ["ppc"]) and all will be well (or with "10.5"
# instead of "10.4" if you're building Tiger-incompatable versions).


def setup_ppc_build():
    print "Setup PPC"
    _sdkdir = setup_sdk(target="10.4", sdk_version="10.5",
                        architectures=["ppc"])

    if _sdkdir == None:
        raise Exception(
            "Cross-compiling without specifying an SDK is not supported")

    _cflags = '-isysroot ' + _sdkdir + ' -mmacosx-version-min=10.4'
    _cxxflags = _cflags
    _cppflags = '-I' + prefix + '/include -isysroot ' + _sdkdir
    _ldflags = '-L' + prefix + '/lib -Wl,-syslibroot,' + \
        _sdkdir + ' -mmacosx-version-min=10.4'

    environ_append('CFLAGS', '-arch ppc')
    environ_append('CXXFLAGS', '-arch ppc')
    environ_append('OBJCFLAGS', '-arch ppc')
    environ_append('LDFLAGS', '-arch ppc')

    _ppc_args = "CFLAGS='" + _cflags + " -arch ppc' CXXFLAGS='" + _cxxflags + \
        " -arch ppc' LDFLAGS='" + _ldflags + \
        " -arch ppc' --build=powerpc-apple-darwin NM=nm"

    _univ_args = "CFLAGS='" + _cflags + " -arch ppc -arch i386' CXXFLAGS='" + \
        _cxxflags + " -arch ppc -arch i386' LDFLAGS='" + \
        _ldflags + " -arch ppc -arch i386'"

# Some packages need to be build universal so that they'll work in a
# cross-compiled environment:
    append_autogenargs("gettext", _univ_args)
    append_autogenargs("intltool", _univ_args)
    append_autogenargs("expat", _univ_args)
    append_autogenargs("gtk-doc", _univ_args)
# Others need to be told explicitly that they're being cross-compiled:
    append_autogenargs(
        "glib", _ppc_args + " glib_cv_uscore=no ac_cv_func_posix_getgrgid_r=yes glib_cv_stack_grows=no ac_cv_func_posix_getpwuid_r=yes ac_cv_c_bigendian=yes")

    append_autogenargs(
        "gtk", _ppc_args + " --with-gdktarget=quartz --without-libjasper --disable-glibtest gio_can_sniff='yes'")

    append_autogenargs("libgcrypt", _ppc_args)
    append_autogenargs("gnome-keyring", _ppc_args)
    append_autogenargs("WebKit", _ppc_args)
    append_autogenargs("OpenSP", _ppc_args)
    append_autogenargs("libdbi", _ppc_args)
    append_autogenargs("libdbi-drivers", _ppc_args)


# This is the function to call to build universal binaries. By default
# it will build a ppc/i386/x86_64 universal binary for 10.5 and
# 10.6. Arguments are the same as for setup_sdk, but with different
# names. See the notes on 64-bit compilation at setup_sdk as well.
def setup_universal_build(target="10.5", sdk_version="10.5",
                          architectures=['ppc', 'i386', 'x86_64']):
    # No point in attempting the impossible
    if _osx_version < 5.0:
        target = "10.4"
        sdk_version = "10.4u"
        architectures = ["ppc", "i386"]

    global autogenargs
    _sdkdir = setup_sdk(target, sdk_version, architectures)
    if _sdkdir == None:
        raise Exception(
            "Cross-compiling without specifying an SDK is not supported")
    _s = " "
    os.environ["ARCH"] = _s.join(architectures)
# some dancing around to build only the architectures specified for
# lipoing together:
    if ('ppc' not in architectures):
        skip.append("glib-ppc")
        skip.append("gtk+-ppc")
        skip.append("glibmm-ppc")
    if ('i386' not in architectures):
        skip.append("glib-i386")
        skip.append("gtk+-i386")
        skip.append("glibmm-i386")
    if ('x86_64' not in architectures):
        skip.append("glib-x86_64")
        skip.append("gtk+-x86_64")
        skip.append("glibmm-x86_64")

    _cflags = '-O1 -ggdb3 -isysroot ' + _sdkdir + ' -mmacosx-version-min=' + target
    _cxxflags = _cflags
    _cppflags = '-I' + prefix + '/include -isysroot ' + _sdkdir
    _ldflags = '-L' + prefix + '/lib -Wl,-syslibroot,' + \
        _sdkdir + ' -mmacosx-version-min=' + target

    autogenargs += " --disable-dependency-tracking"

# The rest of the routine prepares and builds the packages that need
# to be compiled separately and lipoed together.

    _ppc_args = "--build=powerpc-apple-darwin CFLAGS='" + _cflags + " -arch ppc' CXXFLAGS='" + \
        _cxxflags + " -arch ppc' LDFLAGS='" + _ldflags + " -arch ppc' NM=nm"

    _i386_args = "--build=i686-apple-darwin CFLAGS='" + _cflags + " -arch i386' CXXFLAGS='" + \
        _cxxflags + " -arch i386' LDFLAGS='" + _ldflags + " -arch i386'"

    _x86_64_args = "--build=x86_64-apple-darwin CFLAGS='" + _cflags + " -arch x86_64' CXXFLAGS='" + \
        _cxxflags + " -arch x86_64' LDFLAGS='" + _ldflags + " -arch x86_64'"

    append_autogenargs("glib-ppc", _ppc_args +
                       " glib_cv_uscore=no ac_cv_func_posix_getgrgid_r=yes glib_cv_stack_grows=no ac_cv_func_posix_getpwuid_r=yes ac_cv_c_bigendian=yes")

    append_autogenargs("glib-i386", _i386_args +
                       " glib_cv_uscore=no ac_cv_func_posix_getgrgid_r=yes glib_cv_stack_grows=no ac_cv_func_posix_getpwuid_r=yes ac_cv_c_bigendian=no")

    append_autogenargs("glib-x86_64", "--with-libiconv=gnu " + _x86_64_args +
                       " glib_cv_uscore=no ac_cv_func_posix_getgrgid_r=yes glib_cv_stack_grows=no ac_cv_func_posix_getpwuid_r=yes ac_cv_c_bigendian=no")

    append_autogenargs("gtk-ppc", _ppc_args +
                       " --with-gdktarget=quartz --without-libjasper --disable-glibtest gio_can_sniff='yes'")

    append_autogenargs("gtk-i386", _i386_args + "  gio_can_sniff='yes'")

    append_autogenargs("gtk-x86_64", _x86_64_args +
                       " --with-gdktarget=quartz --without-libjasper --disable-glibtest gio_can_sniff='yes'")

    skip.append("glibmm")
    append_autogenargs("glibmm_ppc", _ppc_args)
    append_autogenargs("glibmm_i386", _i386_args)
    append_autogenargs("glibmm_x86_64", _x86_64_args)

###### End Setup Universal Build #######
###### End Function Definitions  #######


##### The following configuration can be overridden in custom files ######

# Moduleset to use. You can override this in .jhbuildrc-custom or on
# the command line.
#
moduleset = 'http://git.gnome.org/browse/gtk-osx/plain/modulesets-stable/gtk-osx.modules'
use_local_modulesets = True

# A list of the modules to build. You can override this in
# .jhbuildrc-custom or on the command line.
#
modules = ['meta-gtk-osx-bootstrap', 'meta-gtk-osx-core']

# A list of modules to skip.
#
skip.append('gmp')
skip.append('guile')

# Source and installation locations.
#
_root = os.path.expanduser("~/gtk")
checkoutroot = os.path.join(_root, "source")
prefix = os.path.join(_root, "inst")
_exec_prefix = None
tarballdir = None
# Extra arguments to pass to all autogen.sh scripts.
#
autogenargs = ''
alwaysautogen = True

# Use the included install-check program if available. It won't update
# timestamps if the header hasn't changed, which speeds up builds.
#
_path = os.path.expanduser('~/.local/bin/install-check')
if os.path.exists(_path):
    os.environ['INSTALL'] = _path

_gtk_osx_prompt_prefix = "JH"

_gtk_osx_default_build = ""

if _osx_version < 4.0:
    print "Error: Mac OS X 10.4 or newer is required, exiting."
    raise SystemExit
elif _osx_version < 5.0:
    # Tiger, we want to use the python version from jhbuild.
    _host_tiger = True
else:
    # Leopard or newer.
    _host_tiger = False

###### Import Customizations ######

# Import optional user RC for further customization. You can override
# the prefix or default build setup for example, or CFLAGS or
# module_autogenargs, etc.
#
_userrc = os.path.join(os.environ['HOME'], '.jhbuildrc-custom')
if os.path.exists(_userrc):
    execfile(_userrc)

# Allow including different variants depending on the environment
# variable JHB. This can be used to have different setups for SDK
# builds, for example.
#
_build = os.environ.get('JHB', _gtk_osx_default_build)

###### Everything Below Uses (and Overrides) customizations! #######

# Check and warn if jhbuild is started from within jhbuild, since that
# will mess up environment variables, especially if different build
# setups are used.
#
_old_prefix = os.environ.get('JHBUILD_PREFIX', "")
_old_build = os.environ.get('JHBUILD_CONFIG', "")
_ran_recursively = _old_prefix != ""
if _ran_recursively:
    if _old_build != _build:
        print "Error: jhbuild is already running with a different build setup, exiting."
        raise SystemExit

    print "Warning: jhbuild is started from within a jhbuild session."

if _build != "":
    try:
        execfile(os.path.join(os.environ['HOME'], '.jhbuildrc-' + _build))
    except EnvironmentError, e:
        print "Couldn't find the file '.jhbuildrc-" + _build + "', exiting."
        raise SystemExit

# The following parameters were set to None at the top of the file;
# they're set here to their default values after processing the
# customizations, but tested to make sure that if they've been
# customized, it will stick.

# Default location for tarball download is into checkoutroot/pkgs. If
# you do multiple builds with different checkoutroots, you'll want to
# override this to somewhere common (~/.local/pkgs is one alternative)
if tarballdir == None:
    tarballdir = os.path.join(checkoutroot, 'pkgs')
# _exec_prefix is used to set $M4 and $LIBTOOLIZE. We set it here to
# prefix if it wasn't over-ridden in .jhbuildrc-custom
if _exec_prefix == None:
    _exec_prefix = prefix


os.environ['PREFIX'] = prefix  # Deprecated, please move to JHBUILD_PREFIX.
os.environ['JHBUILD_PREFIX'] = prefix
os.environ['JHBUILD_SOURCE'] = checkoutroot

# Some packages go off and find /usr/lib/gm4, which is broken Note the
# use of _exec_prefix here. By default it's prefix, but you can
# override it to somewhere else in jhbuildrc-custom if you like.
# os.environ["M4"] = _exec_prefix + "/bin/m4"
# os.environ['LIBTOOLIZE'] = _exec_prefix + '/bin/libtoolize'

if not _host_tiger:
    skip.append('make')
    skip.append('subversion')
    skip.append('bison')
    skip.append('flex')

# The option "headerpad_max_install_names" is there to leave some room for
# changing the library locations with install_name_tool. Note that GNU
# libtool seems to drop the option if we don't use -W here.
#
environ_append('LDFLAGS', '-Wl,-headerpad_max_install_names')

# Make sure we find our installed modules, and before other versions.
environ_prepend('LDFLAGS', '-L' + prefix + '/lib')
environ_prepend('CPPFLAGS', '-I' + prefix + '/include')

# Make sure that ltdl can find our libraries
addpath("LTDL_LIBRARY_PATH", prefix + "/lib")

# Add additional Python/Perl paths so that our modules can be found.
#
_version = 'python' + str(sys.version_info[0]) + '.' + str(sys.version_info[1])
prependpath('PYTHONPATH', os.path.join(
    prefix, 'lib',  _version, 'site-packages', 'gtk-2.0'))
prependpath('PYTHONPATH', os.path.join(prefix, 'lib',  _version))
prependpath('PERL5LIB', prefix + '/lib/perl5/vendor_perl')
prependpath('PERL5LIB', prefix + '/lib/perl5/site_perl')

# Point gtk-doc and other xsltproc users to our XML catalog.
#
os.environ['XML_CATALOG_FILES'] = prefix + '/etc/xml/catalog'

# Freetype has -ansi added by its configure, but uses c99 code
#
append_autogenargs("freetype", 'CFLAGS="$CFLAGS -std=c99"')

# GConf needs to be built static, overriding the generic autogenargs,
# but including it in the module puts it in front of where autogenargs
# puts --disable-static, so we need the override here.
#
append_autogenargs("gconf", "--enable-static")

# Support prepending frameworks to the setup so they are picked up
# instead of things from the prefix or /usr.
#
_frameworks = os.environ.get("JHB_PREPEND_FRAMEWORKS", "")
for _framework in _frameworks.split(":"):
    if _framework != "" and os.path.exists(_framework):
        # Use prependpath to ensure our paths are added in front of
        # the ones jhbuild sets up.
        if os.path.exists(_framework + "/Headers"):
            prependpath("C_INCLUDE_PATH", _framework + "/Headers")
            prependpath("CPLUS_INCLUDE_PATH", _framework + "/Headers")
        if os.path.exists(_framework + "/Resources/dev/bin"):
            prependpath("PATH", _framework + "/Resources/dev/bin")
        if os.path.exists(_framework + "/Resources/dev/lib/pkgconfig"):
            prependpath("PKG_CONFIG_PATH", _framework +
                        "/Resources/dev/lib/pkgconfig")
        if os.path.exists(_framework + "/Resources/dev/lib"):
            # FIXME: Need fix in jhbuild for this to work:
            # prependpath("LDFLAGS", "-L" + _framework + "/Resources/dev/lib")
            environ_prepend("LDFLAGS", "-L" + _framework +
                            "/Resources/dev/lib", " ")
        if os.path.exists(_framework + "/Resources/dev/share/aclocal"):
            prependpath("ACLOCAL_FLAGS", _framework +
                        "/Resources/dev/share/aclocal")


# We do some crude extra argument parsing just to add support for
# getting environment variables. Used in framework creation to pick up
# the jhbuild prefix.
#
# _value = parse_custom_argument("getenv")
# if _value:
#    print os.environ.get(_value, "")
#    raise SystemExit

if _build:
    if "shell" in sys.argv:
        print "Build setup: %s, prefix: %s" % (_build, prefix)
    os.environ["JHBUILD_CONFIG"] = _build
else:
    if "shell" in sys.argv:
        print "Prefix: %s" % (prefix)

if not _ran_recursively and _gtk_osx_prompt_prefix:
    os.environ["JHBUILD_PROMPT"] = "[" + _gtk_osx_prompt_prefix + "] "

# Unset this so we don't mess with the check for not starting
# recursively.
os.unsetenv("JHB")

if "shell" in sys.argv:
    print "Entered jhbuild shell, type 'exit' to return."
