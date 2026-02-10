# Maintainer: Antonio Rodriguez <kontakt@antoniorodriguez.no>

pkgname=cronboard
pkgver=0.4.1
pkgrel=1
pkgdesc="A terminal-based dashboard for managing cron jobs"
arch=('x86_64')
url="https://github.com/antoniorodr/Cronboard"
license=('MIT')
depends=('python>=3.13', 'python-bcrypt' 'python-cron-descriptor' 'python-croniter' 'python-paramiko' 'python-pytest' 'python-python-crontab' 'python-textual' 'python-textual-autocomplete' 'python-textual-dev' 'python-tomlkit' 'cronie')
makedepends=('git' 'python-build' 'python-installer' 'python-wheel' 'python-setuptools')
source=(
	"cronboard-0.4.1.tar.gz::https://github.com/antoniorodr/cronboard/releases/download/v0.4.1/cronboard-0.4.1.tar.gz"
)
sha256sums=('c9cbbca83a5cece2038021967c7289100cdb896b4de249a789642dc84301e65b')

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
