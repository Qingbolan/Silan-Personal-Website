//! Desktop OpenAI credential lifecycle.
//!
//! This outward adapter is the sole owner of macOS Keychain access. OpenAI
//! use-cases receive a validated value object and never handle raw secrets.

use crate::credential_store::{self, ApiCredentialStatus};
use silan_viking_app::{
    OpenAiApiKey, OpenAiCredentialVerifier, OpenAiMarkdownTranslator, OPENAI_KEYCHAIN_ACCOUNT,
    OPENAI_KEYCHAIN_SERVICE,
};

pub(crate) struct DesktopOpenAiCredentials;

impl DesktopOpenAiCredentials {
    pub(crate) fn status() -> Result<ApiCredentialStatus, String> {
        let secret = load_secret()?;
        Ok(status_from_secret(secret.as_deref()))
    }

    pub(crate) fn load_key() -> Result<OpenAiApiKey, String> {
        let secret = load_secret()?.ok_or_else(|| {
            "OpenAI is not configured. Open Workspace settings → OpenAI to add an API key."
                .to_owned()
        })?;
        OpenAiApiKey::parse(secret).map_err(|error| {
            format!("{error}. Open Workspace settings → OpenAI to replace the stored API key.")
        })
    }

    pub(crate) fn verify_and_store(secret: String) -> Result<ApiCredentialStatus, String> {
        let key = OpenAiApiKey::parse(secret).map_err(|error| error.to_string())?;
        let verification = OpenAiCredentialVerifier::default()
            .verify(&key)
            .map_err(|error| error.to_string())?;
        store_secret(key.expose_secret())?;
        Ok(ready_status(verification.request_id))
    }

    pub(crate) fn verify_stored() -> Result<ApiCredentialStatus, String> {
        let key = Self::load_key()?;
        let verification = OpenAiCredentialVerifier::default()
            .verify(&key)
            .map_err(|error| error.to_string())?;
        Ok(ready_status(verification.request_id))
    }

    pub(crate) fn remove() -> Result<ApiCredentialStatus, String> {
        remove_secret()?;
        Ok(missing_status())
    }
}

fn status_from_secret(secret: Option<&str>) -> ApiCredentialStatus {
    match secret {
        None => missing_status(),
        Some(secret) => match OpenAiApiKey::parse(secret.to_owned()) {
            Ok(_) => ready_status(None),
            Err(error) => ApiCredentialStatus::invalid(
                "openai",
                active_translation_model(),
                error.to_string(),
            ),
        },
    }
}

fn missing_status() -> ApiCredentialStatus {
    ApiCredentialStatus::missing("openai", active_translation_model())
}

fn ready_status(request_id: Option<String>) -> ApiCredentialStatus {
    ApiCredentialStatus::ready("openai", active_translation_model(), request_id)
}

fn active_translation_model() -> String {
    OpenAiMarkdownTranslator::from_environment()
        .model()
        .to_owned()
}

fn load_secret() -> Result<Option<String>, String> {
    credential_store::load_secret("OpenAI", OPENAI_KEYCHAIN_SERVICE, OPENAI_KEYCHAIN_ACCOUNT)
}

fn store_secret(secret: &str) -> Result<(), String> {
    credential_store::store_secret(
        "OpenAI",
        OPENAI_KEYCHAIN_SERVICE,
        OPENAI_KEYCHAIN_ACCOUNT,
        secret,
    )
}

fn remove_secret() -> Result<(), String> {
    credential_store::remove_secret("OpenAI", OPENAI_KEYCHAIN_SERVICE, OPENAI_KEYCHAIN_ACCOUNT)
}

#[cfg(test)]
mod tests {
    use super::*;
    use crate::credential_store::ApiCredentialState;

    #[test]
    fn credential_status_is_an_explicit_state_machine() {
        assert_eq!(status_from_secret(None).state, ApiCredentialState::Missing);
        assert_eq!(
            status_from_secret(Some("sk-test-secret")).state,
            ApiCredentialState::Ready
        );
        assert_eq!(
            status_from_secret(Some("invalid")).state,
            ApiCredentialState::Invalid
        );
    }

    #[test]
    #[ignore = "requires a configured macOS Keychain item and OpenAI network access"]
    fn live_desktop_keychain_credential_reaches_openai() {
        let status = DesktopOpenAiCredentials::verify_stored().expect("configured key must verify");
        assert_eq!(status.state, ApiCredentialState::Ready);
        assert!(status.request_id.is_some());
    }
}
