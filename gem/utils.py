def provider_login_url(USE_OIDC_AUTHENTICATION):
    if USE_OIDC_AUTHENTICATION:
        return 'oidc_authentication_init'
    return 'molo.profiles:auth_login'
