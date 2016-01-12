cd "${INSTALLDIR}/${NAME}/gem/"
manage="${VENV}/bin/python ${INSTALLDIR}/${NAME}/gem/manage.py"

$manage migrate --settings=gem.settings.production

# process static files
$manage compress --settings=gem.settings.production
$manage collectstatic --noinput --settings=gem.settings.production

# compile i18n strings
$manage compilemessages --settings=gem.settings.production
