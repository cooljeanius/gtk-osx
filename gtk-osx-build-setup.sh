#!/bin/sh
#
# Script that sets up jhbuild for GTK+ OS X building. Run this to
# checkout jhbuild and the required configuration.
#
# Copyright 2007, 2008, 2009 Imendio AB
#
# Run this whenever you want to update jhbuild or the jhbuild setup;
# it is safe to run it repeatedly. Note that it overwrites
# ~/.jhbuildrc however. Custom settings should be kept in
# ~/.jhbuildrc-custom.
#
# You need Mac OS X 10.4 or newer and Xcode 2.5 or newer. Make sure
# you have subversion (svn) installed, 10.5 has it by default.
#
# Quick HOWTO:
#
# sh gtk-osx-build-setup.sh
#
# jhbuild bootstrap
# jhbuild build meta-gtk-osx-bootstrap
# jhbuild build
#
# See http://live.gnome.org/GTK%2B/OSX/Build for more information.
#

SOURCE="${HOME}"/Source
BASEURL="http://git.gnome.org/browse/gtk-osx/plain/"

do_exit()
{
    echo "$1"
    exit 1
}

get_moduleset_from_git()
{
    curl -s "${BASEURL}/modulesets-stable/$1" -o "${SOURCE}/jhbuild/modulesets/$1" || \
	do_exit "Unable to download $1"
}

if test "$(which svn)" = ""; then
    do_exit "Svn (subversion) is not available, please install it and try again."
fi

if test "$(which git)" = ""; then
    do_exit "Git is not available, please install it and try again."
fi

mkdir -p "${SOURCE}" 2>/dev/null || do_exit "The directory ${SOURCE} could not be created. Check permissions and try again."

rm -f tmp-jhbuild-revision
curl -s "${BASEURL}"/jhbuild-revision -o tmp-jhbuild-revision || \
    do_exit "Unable to retrieve stable jhbuild revision"
JHBUILD_REVISION=$(cat tmp-jhbuild-revision 2>/dev/null)
if test "${JHBUILD_REVISION}" = ""; then
    do_exit "Could not find jhbuild revision to use."
fi

JHBUILD_REVISION_OPTION="origin refs/tags/${JHBUILD_REVISION}"

echo "Checking out jhbuild (${JHBUILD_REVISION}) from git..."
if ! test -d "${SOURCE}"/jhbuild; then
    cd "${SOURCE}" || exit 
    git clone git://git.gnome.org/jhbuild || do_exit "Failed to clone jhbuild."
    cd jhbuild || exit
    git checkout -b stable "${JHBUILD_REVISION}" || \
	do_exit "Checkout of stable branch failed";
    mv modulesets/bootstrap.modules modulesets/bootstrap.modules.dist;
else
    cd "${SOURCE}"/jhbuild || do_exit "Cannot cd to ${SOURCE}/jhbuild."
    if [ -f modulesets/bootstrap.modules.dist ]; then
	rm modulesets/bootstrap.modules
	mv modulesets/bootstrap.modules.dist modulesets/bootstrap.modules;
    fi
    git pull "${JHBUILD_REVISION_OPTION}" >/dev/null || \
	do_exit "Update of jhbuild failed";
    mv modulesets/bootstrap.modules modulesets/bootstrap.modules.dist;
fi

echo "Installing jhbuild..."
(cd "${SOURCE}"/jhbuild && make -f Makefile.plain DISABLE_GETTEXT=1 install >/dev/null) || do_exit "Jhbuild installation failed"

echo "Installing jhbuild configuration..."
curl -s "${BASEURL}"/jhbuildrc-gtk-osx -o "${HOME}"/.jhbuildrc || do_exit "Failed to get jhbuildrc"
curl -s "${BASEURL}"/jhbuildrc-gtk-osx-fw-10.4 -o "${HOME}"/.jhbuildrc-fw-10.4
curl -s "${BASEURL}"/jhbuildrc-gtk-osx-cfw-10.4 -o "${HOME}"/.jhbuildrc-cfw-10.4
curl -s "${BASEURL}"/jhbuildrc-gtk-osx-cfw-10.4u -o "${HOME}"/.jhbuildrc-cfw-10.4u
curl -s "${BASEURL}"/jhbuildrc-gtk-osx-fw-10.4-test -o "${HOME}"/.jhbuildrc-fw-10.4-test
if [ ! -f "${HOME}"/.jhbuildrc-custom ]; then
    curl -s "${BASEURL}"/jhbuildrc-gtk-osx-custom-example -o "${HOME}"/.jhbuildrc-custom || do_exit "Failed to get jhbuildrc-custom"
fi

echo "Installing gtk-osx moduleset files..."
MODULES="bootstrap.modules gtk-osx-bootstrap.modules gtk-osx.modules gtk-osx-gstreamer.modules gtk-osx-gtkmm.modules gtk-osx-python.modules gtk-osx-random.modules gtk-osx-themes.modules gtk-osx-unsupported.modules gtk-osx-universal.modules"

for m in ${MODULES}; do
    get_moduleset_from_git "${m}"
done

if test "$(echo "${PATH}" | grep "${HOME}"/.local/bin)" = ""; then
    echo "PATH does not contain ${HOME}/.local/bin, it is recommended that you add that."
    echo ""
fi

echo "Done."
