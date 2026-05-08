// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

/// ARBCORE_CONTRACT_TEMPLATE
/// NOT AUDITED: this file is an inert interface-shape template for reviewed integrations only.
/// Do not deploy this template, send funds to it, or treat it as production trading software.
contract FlashArbExecutor {
    error ExecutionDisabled();
    error EmptyRoute();

    struct RouteStep {
        bytes32 venueId;
        bytes32 assetIn;
        bytes32 assetOut;
        uint256 quotedRateBps;
    }

    function previewRoute(RouteStep[] calldata route) external pure returns (bytes32 routeHash) {
        if (route.length == 0) {
            revert EmptyRoute();
        }
        return keccak256(abi.encode(route.length, route[0].venueId, route[route.length - 1].venueId));
    }

    function executeReviewedRoute(RouteStep[] calldata route, uint256 minimumReturnBps) external pure returns (bytes32) {
        route;
        minimumReturnBps;
        revert ExecutionDisabled();
    }
}
