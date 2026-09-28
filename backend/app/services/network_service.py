"""
Hook point for actually granting the customer network access once payment clears.

Wire this to whatever sits at your network edge — Mikrotik RouterOS API,
a RADIUS server, a captive-portal voucher system, whatever you land on.
For now it just logs the voucher so you can verify the payment flow
end-to-end before plugging in real hardware.
"""
import logging

logger = logging.getLogger(__name__)


def provision_connection(order):
    logger.info(
        "Provisioning connection for order %s: voucher=%s speed=%sMbps expires=%s",
        order.id,
        order.voucher_code,
        order.plan.speed_mbps,
        order.expires_at,
    )
    # TODO: replace with a real call once you've picked your network setup, e.g.:
    #   mikrotik_client.create_hotspot_user(username=order.voucher_code, profile=f"{order.plan.speed_mbps}M")
    # or
    #   radius_client.add_user(order.voucher_code, profile=f"{order.plan.speed_mbps}mbps")
    return True
