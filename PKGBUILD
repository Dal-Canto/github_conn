# Maintainer: Alessandro <gargoalexdc@gmail.com>
_pkgname=github_conn
pkgname=python-$_pkgname
pkgver=0.3.0
pkgrel=1
pkgdesc="Lightweight Python client for GitHub API with robust error handling, authentication, and pagination support"
arch=('any')
url="https://github.com/Dal-Canto/github_conn"
license=('MIT')
depends=('python' 'python-requests')
makedepends=('python-build' 'python-installer' 'python-hatchling' 'python-wheel')
# Indica ad Arch di usare i file locali presenti dentro il repository clonato
source=("$_pkgname-local::file://.")
sha256sums=('SKIP')

build() {
  cd "$srcdir/$_pkgname-local"
  python -m build --wheel --no-isolation
}

package() {
  cd "$srcdir/$_pkgname-local"
  python -m installer --destdir="$pkgdir" dist/*.whl
}
