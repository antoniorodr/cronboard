# Maintainer: Antonio Rodriguez <kontakt@antoniorodriguez.no>

pkgname=cronboard
pkgver=0.3.0
pkgrel=1
pkgdesc="A terminal-based dashboard for managing cron jobs"
arch=('x86_64')
url="https://github.com/antoniorodr/Cronboard"
license=('MIT')
depends=('python>=3.13', 'python-bcrypt' 'python-cron-descriptor' 'python-croniter' 'python-paramiko' 'python-pytest' 'python-python-crontab' 'python-textual' 'python-textual-autocomplete' 'python-textual-dev' 'python-tomlkit')
makedepends=('git' 'python-build' 'python-installer' 'python-wheel' 'python-setuptools')
source=("$pkgname-$pkgver.tar.gz::$url/archive/v${pkgver}.tar.gz")
sha256sums=('5c888a0209c525c9a520d067891d61f082fb992876a34bf56bf66e049240fc08')

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
