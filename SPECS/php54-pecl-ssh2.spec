%define _default_patch_fuzz 2 \n\n
%global php_apiver  %((echo 0; php -i 2>/dev/null | sed -n 's/^PHP API => //p') | tail -1)
%global php_extdir  %(php-config --extension-dir 2>/dev/null || echo "undefined")
%global php_version %(php-config --version 2>/dev/null || echo 0)
%{!?__pecl:     %{expand: %%global __pecl     %{_bindir}/pecl}}

%define pecl_name ssh2
%define real_name php-pecl-ssh2
%define php_base php54

Name:           %{php_base}-pecl-ssh2
Version:        0.11.3
Release:        2.ius%{?dist}
Summary:        Bindings for the libssh2 library

License:        PHP
Group:          Development/Languages
URL:            http://pecl.php.net/package/ssh2
Source0:        http://pecl.php.net/get/ssh2-%{version}.tgz
Source1:        PHP-LICENSE-3.01
Source2:        php-pecl-ssh2-0.10-README

Patch0:         ssh2-php53.patch

BuildRoot:      %{_tmppath}/%{real_name}-%{version}-%{release}-root-%(%{__id_u} -n)

BuildRequires:  libssh2-devel %{php_base}-devel %{php_base}-pear
Requires(post): %{__pecl}
Requires(postun): %{__pecl}
Provides:       php-pecl(ssh2) = %{version}

%if %{?php_zend_api:1}0
Requires:       %{php_base}(zend-abi) = %{php_zend_api}
Requires:       %{php_base}(api) = %{php_core_api}
%else
# for EL-5
Requires:       %{php_base}-api = %{php_apiver}
%endif

# RPM 4.8
%{?filter_provides_in: %filter_provides_in %{php_extdir}/.*\.so$}
%{?filter_setup}
# RPM 4.9
%global __provides_exclude_from %{?__provides_exclude_from:%__provides_exclude_from|}%{php_extdir}/.*\\.so$


%description
Bindings to the functions of libssh2 which implements the SSH2 protocol.
libssh2 is available from http://www.sourceforge.net/projects/libssh2

%prep
%setup -c -q 

# http://pecl.php.net/bugs/bug.php?id=24390
sed -i -e '/PHP_SSH2_VERSION/s/0.11.3-dev/0.11.3/' %{pecl_name}-%{version}/php_ssh2.h

extver=$(sed -n '/#define PHP_SSH2_VERSION/{s/.* "//;s/".*$//;p}' %{pecl_name}-%{version}/php_ssh2.h)
if test "x${extver}" != "x%{version}"; then
   : Error: Upstream PDO ABI version is now ${extver}, expecting %{version}.
   : Update the pdover macro and rebuild.
   exit 1
fi

mv package.xml %{pecl_name}-%{version}/%{pecl_name}.xml

%{__install} -m 644 -c %{SOURCE1} LICENSE
%{__install} -m 644 -c %{SOURCE2} README


%build
cd %{pecl_name}-%{version}
phpize
%configure
%{__make} %{?_smp_mflags}

%install
cd %{pecl_name}-%{version}
%{__rm} -rf %{buildroot}
%{__make} install INSTALL_ROOT=%{buildroot}

# Install XML package description
install -Dpm 644 %{pecl_name}.xml %{buildroot}%{pecl_xmldir}/%{real_name}.xml

# install config file
%{__install} -d %{buildroot}%{_sysconfdir}/php.d
%{__cat} > %{buildroot}%{_sysconfdir}/php.d/ssh2.ini << 'EOF'
; Enable ssh2 extension module
extension=ssh2.so
EOF

%check
# simple module load test
cd %{pecl_name}-%{version}
php --no-php-ini \
    --define extension_dir=modules \
    --define extension=%{pecl_name}.so \
    --modules | grep %{pecl_name}


%if 0%{?pecl_install:1}
%post
%{pecl_install} %{pecl_xmldir}/%{real_name}.xml >/dev/null || :
%endif


%if 0%{?pecl_uninstall:1}
%postun
if [ $1 -eq 0 ] ; then
    %{pecl_uninstall} %{pecl_name} >/dev/null || :
fi
%endif


%clean
%{__rm} -rf %{buildroot}


%files
%defattr(-,root,root,-)
%doc LICENSE README
%config(noreplace) %{_sysconfdir}/php.d/ssh2.ini
%{php_extdir}/ssh2.so
%{pecl_xmldir}/%{real_name}.xml


%changelog
* Thu May 02 2013 Ben Harper <ben.harper@rackspace.com> - 0.11.3-2.ius
- porting from github.com/mmckinst/php54-pecl-ssh2

* Thu Feb 14 2013 Mark McKinstry <mmckinst@nexcess.net> - 0.11.3-1
- build RPM off of Fedora 18 0.11.3-2
