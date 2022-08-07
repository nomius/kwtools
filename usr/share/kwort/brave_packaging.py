#!/usr/bin/env python3

import urllib.request
import json 
from zipfile import ZipFile, ZipInfo
import tarfile
import os
import sys

releases_api = 'https://api.github.com/repos/brave/brave-browser/releases?per_page=100'
filename_prefix = "brave-browser-"
filename_suffix = "-linux-amd64.zip"
package_internal_payload_path = 'usr/lib/brave-linux-x64'
package_internal_bin_path = "usr/bin"
package_name_prefix = "brave"
package_name_build = "1"
package_compression_type = "xz"


def get_download_link():
    try:
        req = urllib.request.Request(url=releases_api, method='GET')
        res = urllib.request.urlopen(req, timeout=5)
        brave_releases = json.load(res)
    except Exception as exception:
        print(exception)
        return None

    for release in brave_releases:
        if release["name"].startswith("Release"):
            for asset in release["assets"]:
                if asset["name"] == filename_prefix + release["tag_name"].removeprefix("v") + filename_suffix:
                    # I take advantage of the fact that the top release is always the newest one
                    return { "link" : asset["browser_download_url"], "version" : release["tag_name"].removeprefix("v"), "filename" : asset["name"] }
    return None


def make_tarfile(output_filename, source_dir):
    with tarfile.open(output_filename, "w:" + package_compression_type) as tar:
        tar.add(source_dir, arcname=os.path.basename(source_dir))


class MyZipFile(ZipFile):
    def _extract_member(self, member, targetpath, pwd):
        if not isinstance(member, ZipInfo):
            member = self.getinfo(member)

        targetpath = super()._extract_member(member, targetpath, pwd)

        attr = member.external_attr >> 16
        if attr != 0:
            os.chmod(targetpath, attr)
        return targetpath


release = get_download_link()
if release:
    try:

        urllib.request.urlretrieve(release["link"], release["filename"])
        print("Downloaded: " + release["link"] + " as: " + release["filename"])
    except Exception as exception:
        print("Error downloading package: " + exception)
        sys.exit(1)
else:
    sys.exit(1)


try:
    os.makedirs("temp/" + package_internal_payload_path)
    current_pwd = os.getcwd()
    os.chdir("temp/" + package_internal_payload_path)
    print("Created direcory structure in temp directory")
except Exception as exception:
    print("Error creating directory structure: " + exception)
    sys.exit(1)

try:
    with MyZipFile(current_pwd + "/" + release["filename"]) as zfp:
        zfp.extractall()
    print("File decompression in new structure complete")
except Exception as exception:
    print("Error decompressing package: " + exception)
    sys.exit(1)

os.chdir(current_pwd)

if package_internal_bin_path:
    try:
        os.makedirs("temp/" + package_internal_bin_path)
        os.symlink("/" + package_internal_payload_path + "/brave", "temp/" + package_internal_bin_path + "/brave")
        print("Symbolic link: /" + package_internal_bin_path + " -> /" + package_internal_payload_path + "/brave created")
    except Exception as exception:
        print("Error creating symbolic link: " + exception)
        sys.exit(1)

try:
    os.chdir("temp")
    tar = make_tarfile("../" + package_name_prefix + "#" + release["version"] +  "#x86_64#" + package_name_build + ".tar." + package_compression_type, ".")
    print(package_name_prefix + release["version"] +  "#x86_64#" + package_name_build + "tar." + package_compression_type + " created.")
except Exception as exception:
    print("Error creating package: " + exception)
    sys.exit(1)
