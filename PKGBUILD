# Maintainer: Antonio Rodriguez <kontakt@antoniorodriguez.no>

pkgname=cronboard
pkgver=0.1.2
pkgrel=1
pkgdesc="A terminal-based dashboard for managing cron jobs"
arch=('x86_64')
url="https://github.com/antoniorodr/Cronboard"
license=('MIT')
depends=('python>=3.13', 'python-bcrypt' 'python-cron-descriptor' 'python-croniter' 'python-dt-croniter' 'python-paramiko' 'python-pytest' 'python-crontab' 'python-textual' 'python-textual-autocomplete' 'python-textual-dev')
makedepends=('git' 'python-build' 'python-installer' 'python-wheel' 'python-setuptools')
source=("$pkgname-$pkgver.tar.gz::$url/archive/v${pkgver}.tar.gz")
sha256sums=('8172c91638f557226ab015c6ea013ccd0b14b38264bab68b0a8a4eca2ac4c58e')

build() {
  cd $pkgname-$pkgver || exit
  msg2 "Building package..."
  python -m build --wheel --no-isolation
}

package() {
  cd $pkgname-$pkgver || exit
  msg2 "Installing package..."
  python -m installer --destdir="$pkgdir" dist/*.whl
}
