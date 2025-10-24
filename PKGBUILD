# Maintainer: Antonio Rodriguez <kontakt@antoniorodriguez.no>

pkgname=cronboard
pkgver=0.3.1
pkgrel=1
pkgdesc="A terminal-based dashboard for managing cron jobs"
arch=('x86_64')
url="https://github.com/antoniorodr/Cronboard"
license=('MIT')
depends=('python>=3.13', 'python-bcrypt' 'python-cron-descriptor' 'python-croniter' 'python-paramiko' 'python-pytest' 'python-python-crontab' 'python-textual' 'python-textual-autocomplete' 'python-textual-dev' 'python-tomlkit')
makedepends=('git' 'python-build' 'python-installer' 'python-wheel' 'python-setuptools')
source=("$pkgname-$pkgver.tar.gz::$url/archive/v${pkgver}.tar.gz")
sha256sums=('0c9a7c63d021054fe35065976306e3cece5e8bbc6c9cfbf8bc6354f947aa01eb')

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
