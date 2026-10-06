"""Despacho central de vistas para CommunityLab."""

from . import connections, curation, dashboard, ingestion, observability, settings, storage, support

render_dashboard = dashboard.render_dashboard

ROUTES = {
    # Rutas estándar
    "dashboard": dashboard.render_dashboard,
    "live_channels": ingestion.render_live_channels,
    "batch_processing": ingestion.render_batch_processing,
    "pending_review": curation.render_pending_review,
    "approved_assets": curation.render_approved_assets,
    "faqs": curation.render_faqs,
    "cloud_explorer": storage.render_cloud_explorer,
    "par_links": storage.render_par_links,
    "bot_status": connections.render_bot_status,
    "webhooks_tunnel": connections.render_webhooks_tunnel,
    "flow_diagram": observability.render_flow_diagram,
    "live_logs": observability.render_live_logs,
    "settings": settings.render_settings,
    "support": support.render_support,
    # Alias amigables en español solicitados en la plantilla
    "fuentes-activas": ingestion.render_live_channels,
    "pendientes-revision": curation.render_pending_review,
    "almacenamiento-oci": storage.render_cloud_explorer,
    "estado-automatizaciones": connections.render_bot_status,
    "flujo-pipeline": observability.render_flow_diagram,
    "configuracion": settings.render_settings,
}


def render_view(view: str):
    handler = ROUTES.get(view, dashboard.render_dashboard)
    handler()
