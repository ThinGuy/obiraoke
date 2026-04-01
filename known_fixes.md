# Known Fixes

Living record of snap packaging gotchas for the obiraoke project.


## 1. Files in snap/local/ are not staged into $SNAP

Files placed under snap/local/ are available at build time but are not
automatically included in the final snap. The wrapper script lived at
snap/local/wrapper and was referenced as command: snap/local/wrapper, which
would fail at runtime because the file does not exist inside the snap.

Resolution: add a separate part using the dump plugin that copies
snap/local/wrapper into $SNAP/bin/wrapper, and set command: bin/wrapper.


## 2. PYTHONPATH must target Python 3.12 site-packages on core24

core24 ships Python 3.12. The original PYTHONPATH pointed at the
dist-packages directories used by core22 and older bases
($SNAP/lib/python3/dist-packages and $SNAP/usr/lib/python3/dist-packages).
Packages installed by the python plugin on core24 land in
$SNAP/lib/python3.12/site-packages, so the old path found nothing.

Resolution: set PYTHONPATH to $SNAP/lib/python3.12/site-packages.


## 3. Snap summary must be Ubuntu-focused

The original summary said "Linux, macOS, and Windows". A snap is an Ubuntu
packaging format; mentioning other operating systems in the summary is
misleading and does not match the distribution channel.

Resolution: replace the summary with Ubuntu-focused wording.
