#!/usr/bin/env bash

ARCH=x86_64
BUILD=1

if [ -z "${NEW_VERSION}" ]; then
	CURRENT_VERSION=$(google-chrome-stable --version 2>/dev/null | awk '{print $NF}')
	NEW_VERSION=$(curl http://dl.google.com/linux/chrome/deb/dists/stable/main/binary-amd64/Packages.gz 2>/dev/null | gzip -dc - | sed '/^Package: google-chrome-stable$/,/^$/{//!b};d' | grep Version | awk '{print $2}')

	if [ "${CURRENT_VERSION}" = "${NEW_VERSION}" ]; then
		read -n 1 -p "You're running the latest version, do you want to generate the package anyways? [y/n]: " ANSWER
		if [ "${ANSWER}" != "y" -a "${ANSWER}" = "Y" ]; then
			exit 0
		fi
	fi
	read -n 1 -p "You're about to package Google Chrome $NEW_VERSION. Do you want to continue? [y/N:] " opt
	echo
	if [ "${opt}" != 'y' -a "${opt}" != 'Y' ]; then
		exit 0
	fi
fi


tmp=$(mktemp -d)
pushd "${tmp}"
wget https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb
ar x google-chrome-stable_current_amd64.deb data.tar.xz
rm -f google-chrome-stable_current_amd64.deb
tar xpf data.tar.xz
rm -rf data.tar.xz etc usr/share/{doc,gnome-control-center,menu}
(cd usr/bin && rm -f google-chrome-stable)
(cd usr/bin && ln -s ../../opt/google/chrome/google-chrome google-chrome-stable)
(cd usr/bin && ln -s google-chrome-stable google-chrome)
(cd usr/bin && ln -s google-chrome-stable chrome)
makepkg -z google-chrome-stable#${NEW_VERSION}#${ARCH}#${BUILD}.tar.xz
popd
mv "${tmp}/google-chrome-stable#${NEW_VERSION}#${ARCH}#${BUILD}.tar.xz" .
rm -rf "${tmp}"
echo "Package google-chrome-stable#${NEW_VERSION}#${ARCH}#${BUILD}.tar.xz generated"
echo "NOTE: You need llvm and cups (or just libcups) to use chis package"
