import base64
import time
from typing import Any

import requests


class EnhanceError(RuntimeError):
    pass


def _b64_data_uri_jpeg(jpg_bytes: bytes) -> str:
    b64 = base64.b64encode(jpg_bytes).decode("ascii")
    return f"data:image/jpeg;base64,{b64}"


def _replicate_headers(api_token: str) -> dict[str, str]:
    return {
        "Authorization": f"Bearer {api_token}",
        "Content-Type": "application/json",
        "Accept": "application/json",
    }


def _pick_output_url(output: Any) -> str:
    out_url = None
    if isinstance(output, str):
        out_url = output
    elif isinstance(output, list) and output:
        out_url = output[0]
    elif isinstance(output, dict):
        out_url = output.get("image") or output.get("output")

    if not out_url or not isinstance(out_url, str):
        raise EnhanceError("No pude obtener URL de salida")
    return out_url


def _schema_input_properties(openapi_schema: Any) -> dict[str, Any]:
    try:
        return (
            openapi_schema.get("components", {})
            .get("schemas", {})
            .get("Input", {})
            .get("properties", {})
        )
    except Exception:
        return {}


def _pick_input_keys(*, properties: dict[str, Any]) -> tuple[str, str | None]:
    keys = set(properties.keys())

    image_candidates = [
        "image",
        "input_image",
        "img",
        "input",
        "source",
    ]
    scale_candidates = [
        "scale",
        "upscale",
        "upscale_factor",
        "scale_factor",
        "factor",
        "resize",
    ]

    image_key = next((k for k in image_candidates if k in keys), None)
    scale_key = next((k for k in scale_candidates if k in keys), None)
    if not image_key:
        # Fallback: first property that looks like an image input
        for k in sorted(keys):
            spec = properties.get(k, {})
            if isinstance(spec, dict) and spec.get("format") == "uri":
                image_key = k
                break

    if not image_key:
        image_key = "image"

    return image_key, scale_key


def _build_replicate_input(
    *,
    jpg_bytes: bytes,
    scale: Any,
    openapi_schema: Any | None = None,
    image_key_override: str | None = None,
    scale_key_override: str | None = None,
    extra_input: dict[str, Any] | None = None,
) -> dict[str, Any]:
    props = _schema_input_properties(openapi_schema) if openapi_schema else {}
    image_key, scale_key = _pick_input_keys(properties=props)

    if image_key_override:
        image_key = image_key_override
    if scale_key_override:
        scale_key = scale_key_override

    payload: dict[str, Any] = {image_key: _b64_data_uri_jpeg(jpg_bytes)}
    if scale_key and scale is not None:
        payload[scale_key] = scale

    if extra_input:
        payload.update(extra_input)
    return payload


def _get_replicate_latest_version_id(*, api_token: str, model: str) -> str:
    """Resolve `owner/name` to its latest version id."""
    if "/" not in model:
        raise EnhanceError("model debe ser 'owner/name'")

    owner, name = model.split("/", 1)
    r = requests.get(
        f"https://api.replicate.com/v1/models/{owner}/{name}",
        headers=_replicate_headers(api_token),
        timeout=30,
    )
    if r.status_code >= 400:
        raise EnhanceError(f"Replicate model lookup error {r.status_code}: {r.text}")

    data: dict[str, Any] = r.json()
    latest = data.get("latest_version")
    if isinstance(latest, dict):
        ver_id = latest.get("id")
        if isinstance(ver_id, str) and ver_id:
            return ver_id

    raise EnhanceError("No pude resolver latest_version.id para el modelo")


def resolve_replicate_model_version_id(*, api_token: str, model: str) -> str:
    """Public wrapper to resolve latest version id for owner/name."""
    return _get_replicate_latest_version_id(api_token=api_token, model=model)


def run_replicate_prediction_http(
    *,
    api_token: str,
    model: str,
    input: dict[str, Any],
    model_version: str | None = None,
    timeout_s: int = 180,
    poll_interval_s: float = 1.5,
) -> tuple[str, Any]:
    """Run any Replicate model via HTTP and return (status, output)."""
    if not model_version:
        model_version = _get_replicate_latest_version_id(api_token=api_token, model=model)

    payload = {"version": model_version, "input": input}
    r = requests.post(
        "https://api.replicate.com/v1/predictions",
        headers=_replicate_headers(api_token),
        json=payload,
        timeout=30,
    )
    if r.status_code >= 400:
        raise EnhanceError(f"Replicate error {r.status_code}: {r.text}")

    data: dict[str, Any] = r.json()
    pred_id = data.get("id")
    if not pred_id:
        raise EnhanceError("Respuesta inesperada de Replicate (sin id)")

    deadline = time.time() + float(timeout_s)
    status = data.get("status")
    output = data.get("output")

    while status not in ("succeeded", "failed", "canceled"):
        if time.time() > deadline:
            raise EnhanceError("Timeout esperando respuesta de Replicate")
        time.sleep(float(poll_interval_s))

        rr = requests.get(
            f"https://api.replicate.com/v1/predictions/{pred_id}",
            headers=_replicate_headers(api_token),
            timeout=30,
        )
        if rr.status_code >= 400:
            raise EnhanceError(f"Replicate poll error {rr.status_code}: {rr.text}")
        data = rr.json()
        status = data.get("status")
        output = data.get("output")

    if status != "succeeded":
        err = data.get("error") or ""
        raise EnhanceError(f"Replicate no completo (status={status}). {err}")

    return status, output


def download_replicate_output_bytes(*, output: Any, timeout_s: int = 60) -> bytes:
    """Given a Replicate output (url/list/dict), download bytes."""
    out_url = _pick_output_url(output)
    img_r = requests.get(out_url, timeout=timeout_s)
    if img_r.status_code >= 400:
        raise EnhanceError(f"No pude descargar resultado: {img_r.status_code}")
    return img_r.content


def _get_replicate_version_schema(*, api_token: str, model: str, version_id: str) -> Any | None:
    if "/" not in model:
        return None

    owner, name = model.split("/", 1)
    r = requests.get(
        f"https://api.replicate.com/v1/models/{owner}/{name}/versions/{version_id}",
        headers=_replicate_headers(api_token),
        timeout=30,
    )
    if r.status_code >= 400:
        return None

    data: dict[str, Any] = r.json()
    schema = data.get("openapi_schema")
    return schema if schema else None


def enhance_quality_replicate(
    *,
    jpg_bytes: bytes,
    api_token: str,
    model_version: str | None = None,
    model: str | None = None,
    scale: Any = 2,
    timeout_s: int = 120,
    poll_interval_s: float = 1.5,
    image_key: str | None = None,
    scale_key: str | None = None,
    extra_input: dict[str, Any] | None = None,
) -> bytes:
    """Upscale/enhance a JPG using Replicate.

    Notes:
    - This expects `jpg_bytes` as input.
    - `model_version` is a Replicate model version id.
    """
    if isinstance(scale, int) and scale not in (1, 2, 3, 4):
        raise EnhanceError("scale int debe estar entre 1 y 4")

    if model and model.startswith("google/imagen"):
        raise EnhanceError(
            "google/imagen-* es un modelo de generacion (texto->imagen), no un upscaler. "
            "Usa un modelo de super-resolucion (ej. nightmareai/real-esrgan)"
        )

    if not model_version:
        if not model:
            raise EnhanceError("Debes pasar model_version o model")
        model_version = _get_replicate_latest_version_id(api_token=api_token, model=model)

    schema = _get_replicate_version_schema(api_token=api_token, model=model or "", version_id=model_version)

    payload = {
        "version": model_version,
        "input": _build_replicate_input(
            jpg_bytes=jpg_bytes,
            scale=scale,
            openapi_schema=schema,
            image_key_override=image_key,
            scale_key_override=scale_key,
            extra_input=extra_input,
        ),
    }

    r = requests.post(
        "https://api.replicate.com/v1/predictions",
        headers=_replicate_headers(api_token),
        json=payload,
        timeout=30,
    )
    if r.status_code >= 400:
        raise EnhanceError(f"Replicate error {r.status_code}: {r.text}")

    data: dict[str, Any] = r.json()
    pred_id = data.get("id")
    if not pred_id:
        raise EnhanceError("Respuesta inesperada de Replicate (sin id)")

    deadline = time.time() + float(timeout_s)
    status = data.get("status")
    output = data.get("output")

    while status not in ("succeeded", "failed", "canceled"):
        if time.time() > deadline:
            raise EnhanceError("Timeout esperando respuesta de Replicate")
        time.sleep(float(poll_interval_s))

        rr = requests.get(
            f"https://api.replicate.com/v1/predictions/{pred_id}",
            headers=_replicate_headers(api_token),
            timeout=30,
        )
        if rr.status_code >= 400:
            raise EnhanceError(f"Replicate poll error {rr.status_code}: {rr.text}")
        data = rr.json()
        status = data.get("status")
        output = data.get("output")

    if status != "succeeded":
        err = data.get("error") or ""
        raise EnhanceError(f"Replicate no completo (status={status}). {err}")

    out_url = _pick_output_url(output)

    img_r = requests.get(out_url, timeout=60)
    if img_r.status_code >= 400:
        raise EnhanceError(f"No pude descargar resultado: {img_r.status_code}")

    return img_r.content
