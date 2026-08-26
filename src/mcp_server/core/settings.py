from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import HttpUrl


class Settings(BaseSettings):
    """
    Cleaned up from the original scaffold (see huggingface-experiments/
    mcp-server for the pre-cleanup version):
    - Removed RETRIEVAL_TLS_CA_CERT/CLIENT_CERT/CLIENT_KEY - mTLS deferred
      to the later deployment pass, alongside Docker/k8s, not needed for
      a first working pipeline. rag-mcp-service doesn't verify client
      certs at all, so these would only ever cause a FileNotFoundError.
    - Removed AUTH0_LANGCHAIN_CLIENT_DOMAIN - declared in the original but
      never actually read anywhere (the JWKS/issuer properties used
      AUTH0_DOMAIN instead) - genuinely dead.
    - Removed AUTH0_LANGCHAIN_CLIENT_AUDIENCE and the jwks/issuer
      properties - these were only for verifying INBOUND connections to
      this MCP server (JWTVerifier in main.py), which is deferred along
      with mTLS for the same reason: not needed to prove the pipeline
      works locally first.
    - Removed the duplicate RETRIEVAL_TIMEOUT/retrieval_timeout pair and
      the typo'd, unused retrieval_retires - kept one correctly-named
      field for each real concept.
    """

    # Server settings
    ENV: str = "development"
    PORT: int = 8002

    # RAG Microservice (rag-mcp-service) settings
    RETRIEVAL_BASE_URL: HttpUrl
    RETRIEVAL_TIMEOUT: float = 30.0
    RETRIEVAL_RETRIES: int = 3

    # Auth0 M2M settings - used to fetch OUR OWN token to call
    # rag-mcp-service, which enforces require_scope("search:knowledge").
    # Not related to whoever connects TO this MCP server (that's the
    # inbound auth deferred above).
    AUTH0_DOMAIN: str
    AUTH0_AUDIENCE: str
    AUTH0_CLIENT_ID: str
    AUTH0_CLIENT_SECRET: str

    @property
    def auth0_token_url(self) -> str:
        return f"https://{self.AUTH0_DOMAIN}/oauth/token"

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


settings = Settings()