//! Desktop DeepSeek credential lifecycle.
//!
//! This outward adapter shares the CLI's stable Keychain identity. Language
//! review use-cases receive a validated value object and never handle raw
//! secrets.

use crate::credential_store::{self, ApiCredentialStatus};
use silan_viking_app::{
    DeepSeekApiKey, DeepSeekCredentialVerifier, DeepSeekLanguageAuditor, DEEPSEEK_KEYCHAIN_ACCOUNT,
    DEEPSEEK_KEYCHAIN_SERVICE,
};
use std::env;

const PROVIDER: &str = "deepseek";
const ENVIRONMENT_VARIABLE: &str = "DEEPSEEK_API_KEY";

pub(crate) struct DesktopDeepSeekCredentials;

impl DesktopDeepSeekCredentials {
    pub(crate) fn status() -> Result<ApiCredentialStatus, String> {
        let secret = configured_secret()?;
        Ok(status_from_secret(secret.as_deref()))
    }

    pub(crate) fn load_key() -> Result<DeepSeekApiKey, String> {
        let secret = configured_secret()?.ok_or_else(|| {
            "DeepSeek is not configured. Open Workspace settings → AI connection to add an API key."
                .to_owned()
        })?;
        DeepSeekApiKey::parse(secret).map_err(|error| {
            format!(
                "{error}. Open Workspace settings → AI connection to replace the stored API key."
            )
        })
    }

    pub(crate) fn verify_and_store(secret: String) -> Result<ApiCredentialStatus, String> {
        let key = DeepSeekApiKey::parse(secret).map_err(|error| error.to_string())?;
        let verification = DeepSeekCredentialVerifier::default()
            .verify(&key)
            .map_err(|error| error.to_string())?;
        credential_store::store_secret(
            "DeepSeek",
            DEEPSEEK_KEYCHAIN_SERVICE,
            DEEPSEEK_KEYCHAIN_ACCOUNT,
            key.expose_secret(),
        )?;
        Ok(ready_status(verification.request_id))
    }

    pub(crate) fn verify_stored() -> Result<ApiCredentialStatus, String> {
        let key = Self::load_key()?;
        let verification = DeepSeekCredentialVerifier::default()
            .verify(&key)
            .map_err(|error| error.to_string())?;
        Ok(ready_status(verification.request_id))
    }

    pub(crate) fn remove() -> Result<ApiCredentialStatus, String> {
        credential_store::remove_secret(
            "DeepSeek",
            DEEPSEEK_KEYCHAIN_SERVICE,
            DEEPSEEK_KEYCHAIN_ACCOUNT,
        )?;
        Self::status()
    }
}

fn configured_secret() -> Result<Option<String>, String> {
    match env::var(ENVIRONMENT_VARIABLE) {
        Ok(secret) => Ok(Some(secret)),
        Err(env::VarError::NotPresent) => credential_store::load_secret(
            "DeepSeek",
            DEEPSEEK_KEYCHAIN_SERVICE,
            DEEPSEEK_KEYCHAIN_ACCOUNT,
        ),
        Err(error) => Err(format!("Could not read {ENVIRONMENT_VARIABLE}: {error}")),
    }
}

fn status_from_secret(secret: Option<&str>) -> ApiCredentialStatus {
    match secret {
        None => missing_status(),
        Some(secret) => match DeepSeekApiKey::parse(secret.to_owned()) {
            Ok(_) => ready_status(None),
            Err(error) => ApiCredentialStatus::invalid(PROVIDER, active_model(), error.to_string()),
        },
    }
}

fn missing_status() -> ApiCredentialStatus {
    ApiCredentialStatus::missing(PROVIDER, active_model())
}

fn ready_status(request_id: Option<String>) -> ApiCredentialStatus {
    ApiCredentialStatus::ready(PROVIDER, active_model(), request_id)
}

fn active_model() -> String {
    DeepSeekLanguageAuditor::from_environment()
        .model()
        .to_owned()
}

#[cfg(test)]
mod tests {
    use super::*;
    use crate::credential_store::ApiCredentialState;

    #[test]
    fn credential_status_is_an_explicit_state_machine() {
        assert_eq!(status_from_secret(None).state, ApiCredentialState::Missing);
        assert_eq!(
            status_from_secret(Some("deepseek-test-secret")).state,
            ApiCredentialState::Ready
        );
        assert_eq!(
            status_from_secret(Some("invalid secret")).state,
            ApiCredentialState::Invalid
        );
    }
}
