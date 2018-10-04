pkg_name=txkarmabot
pkg_origin=schafezp
pkg_version="0.1.0"
pkg_maintainer="Zachary Schafer <PlusMinusKarmaBot@gmail.com>"
pkg_license=("Apache-2.0")
pkg_source="http://some_source_url/releases/${pkg_name}-${pkg_version}.tar.gz"
# pkg_filename="${pkg_name}-${pkg_version}.tar.gz"
# pkg_shasum="TODO"
# pkg_deps=(core/glibc)
pkg_build_deps=(core/python37)
# pkg_lib_dirs=(lib)
# pkg_include_dirs=(include)
# pkg_bin_dirs=(bin)
# pkg_pconfig_dirs=(lib/pconfig)
# pkg_svc_run="haproxy -f $pkg_svc_config_path/haproxy.conf"
# pkg_exports=(
#   [host]=srv.address
#   [port]=srv.port
#   [ssl-port]=srv.ssl.port
# )
# pkg_exposes=(port ssl-port)
# pkg_binds=(
#   [database]="port host"
# )
# pkg_binds_optional=(
#   [storage]="port host"
# )
# pkg_interpreters=(bin/bash)
# pkg_svc_user="hab"
# pkg_svc_group="$pkg_svc_user"
# pkg_description="Some description."
# pkg_upstream_url="http://example.com/project-name"

