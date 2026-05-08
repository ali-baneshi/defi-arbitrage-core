# @version ^0.4.0
# ARBCORE_CONTRACT_TEMPLATE
# NOT AUDITED: this file is an inert interface-shape template for reviewed integrations only.
# Do not deploy this template, send funds to it, or treat it as production trading software.

struct RouteStep:
    venue_id: bytes32
    asset_in: bytes32
    asset_out: bytes32
    quoted_rate_bps: uint256


@view
@external
def preview_route(route: DynArray[RouteStep, 8]) -> bytes32:
    assert len(route) > 0, "empty route"
    return keccak256(concat(route[0].venue_id, route[len(route) - 1].venue_id))


@external
def execute_reviewed_route(route: DynArray[RouteStep, 8], minimum_return_bps: uint256) -> bytes32:
    assert len(route) > 0, "empty route"
    assert minimum_return_bps > 0, "minimum return required"
    raise "execution disabled"
