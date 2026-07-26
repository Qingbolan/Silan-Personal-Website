//! Shared local API-credential persistence for Desktop provider adapters.

use serde::Serialize;

#[derive(Debug, Clone, Copy, PartialEq, Eq, Serialize)]
#[serde(rename_all = "snake_case")]
pub(crate) enum ApiCredentialState {
    Missing,
    Ready,
    Invalid,
}

#[derive(Debug, Clone, PartialEq, Eq, Serialize)]
pub(crate) struct ApiCredentialStatus {
    pub(crate) provider: String,
    pub(crate) state: ApiCredentialState,
    pub(crate) model: String,
    pub(crate) detail: Option<String>,
    pub(crate) request_id: Option<String>,
}

impl ApiCredentialStatus {
    pub(crate) fn missing(provider: &str, model: String) -> Self {
        Self {
            provider: provider.to_owned(),
            state: ApiCredentialState::Missing,
            model,
            detail: None,
            request_id: None,
        }
    }

    pub(crate) fn ready(provider: &str, model: String, request_id: Option<String>) -> Self {
        Self {
            provider: provider.to_owned(),
            state: ApiCredentialState::Ready,
            model,
            detail: None,
            request_id,
        }
    }

    pub(crate) fn invalid(provider: &str, model: String, detail: String) -> Self {
        Self {
            provider: provider.to_owned(),
            state: ApiCredentialState::Invalid,
            model,
            detail: Some(detail),
            request_id: None,
        }
    }
}

#[cfg(target_os = "macos")]
pub(crate) fn load_secret(
    provider: &str,
    service: &str,
    account: &str,
) -> Result<Option<String>, String> {
    match keychain_entry(service, account)?.get_password() {
        Ok(secret) => Ok(Some(secret)),
        Err(keyring::Error::NoEntry) => Ok(None),
        Err(error) => Err(format!(
            "Could not read {provider} API key from Keychain: {error}"
        )),
    }
}

#[cfg(target_os = "macos")]
pub(crate) fn store_secret(
    provider: &str,
    service: &str,
    account: &str,
    secret: &str,
) -> Result<(), String> {
    keychain_entry(service, account)?
        .set_password(secret)
        .map_err(|error| format!("Could not store {provider} API key in Keychain: {error}"))
}

#[cfg(target_os = "macos")]
pub(crate) fn remove_secret(provider: &str, service: &str, account: &str) -> Result<(), String> {
    match keychain_entry(service, account)?.delete_credential() {
        Ok(()) | Err(keyring::Error::NoEntry) => Ok(()),
        Err(error) => Err(format!(
            "Could not remove {provider} API key from Keychain: {error}"
        )),
    }
}

#[cfg(target_os = "macos")]
fn keychain_entry(service: &str, account: &str) -> Result<keyring::Entry, String> {
    keyring::Entry::new(service, account)
        .map_err(|error| format!("Could not access macOS Keychain: {error}"))
}

#[cfg(not(target_os = "macos"))]
pub(crate) fn load_secret(
    provider: &str,
    _service: &str,
    _account: &str,
) -> Result<Option<String>, String> {
    Err(format!(
        "{provider} credential storage currently requires macOS Keychain"
    ))
}

#[cfg(not(target_os = "macos"))]
pub(crate) fn store_secret(
    provider: &str,
    _service: &str,
    _account: &str,
    _secret: &str,
) -> Result<(), String> {
    Err(format!(
        "{provider} credential storage currently requires macOS Keychain"
    ))
}

#[cfg(not(target_os = "macos"))]
pub(crate) fn remove_secret(provider: &str, _service: &str, _account: &str) -> Result<(), String> {
    Err(format!(
        "{provider} credential storage currently requires macOS Keychain"
    ))
}
