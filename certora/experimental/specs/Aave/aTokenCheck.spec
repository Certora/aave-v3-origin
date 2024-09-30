import "./aToken.spec";
import "./PoolSummarizationForTokens.spec";
import "./IncentivesControllerForTokens.spec";

import "./tokenCheckBase.spec";

using ATokenInstance as aToken;
using Utilities as utils;

methods {
    // Note/Warning: Must _not summarize_ the super call to balanceOf! Only the top-level in AToken. Same with totalSupply. This will lead to 'empty' verification.
    
    // envfree declarations
    function utils.nop() external envfree;
    function aToken.scaledBalanceOf(address) external returns uint256 envfree;
    function aToken.scaledTotalSupply() external returns uint256 envfree;
    function aToken.allowance(address,address) external returns uint256 envfree;
    // note that balanceOf and totalSupply are not envfree because the calls to the pool are in fact not envfree.
}

function not_implemented() {
    assert false, "Not implemented";
}

function dont_care() {
    require false; // to be used for methods we don't model in the summary version anyway
}

definition initialize_method_sig() returns uint32 = sig:initialize(address,address,address,address,uint8,string,string,bytes).selector;

// xxx currently missing return value equivalence checks
function run_parametric_with_cvl_equivalent(method f, env e) {
    // note there's a strong assumption the side effects of CVL and Solidity versions are disjoint
    if (f.selector == sig:transfer(address,uint256).selector) {
        address a1;
        uint256 u1;
        aTokenTransferCVL(aToken, a1, u1, e);
        aToken.transfer(e, a1, u1);
    } else if (f.selector == sig:transferFrom(address,address,uint256).selector) {
        address a1;
        address a2;
        uint256 u1;
        // must have the same allowance at the beginning to have the same effect
        require allowanceByToken[aToken][a1][e.msg.sender] == aToken.allowance(e, a1, e.msg.sender);
        aTokenTransferFromCVL(aToken, a1, a2, u1, e);
        aToken.transferFrom(e, a1, a2, u1);
    } else if (f.selector == sig:transferOnLiquidation(address,address,uint256).selector) {
        address a1;
        address a2;
        uint256 u1;
        aTokenTransferOnLiquidationCVL(aToken, a1, a2, u1, e);
        aToken.transferOnLiquidation(e, a1, a2, u1);
    } else if (f.selector == sig:transferUnderlyingTo(address,uint256).selector) {
        address a1;
        uint256 u1;
        aTokenTransferUnderlyingToCVL(aToken, a1, u1);
        aToken.transferUnderlyingTo(e, a1, u1);
    } else if (f.selector == sig:permit(address,address,uint256,uint256,uint8,bytes32,bytes32).selector) {
        address a1;
        address a2;
        uint256 u1;
        uint256 u2;
        uint8 u3;
        bytes32 by1;
        bytes32 by2;
        permitCVL(aToken, a1, a2, u1, u2, u3, by1, by2);
        aToken.permit(e, a1, a2, u1, u2, u3, by1, by2);
    } else if (f.selector == sig:approve(address,uint256).selector) {
        address a1;
        uint256 u1;
        approveCVL(aToken, e.msg.sender, a1, u1);
        aToken.approve(e, a1, u1);
    } else if (f.selector == sig:decreaseAllowance(address,uint256).selector) {
        address a1;
        uint256 u1;
        decreaseAllowanceCVL(aToken, e.msg.sender, a1, u1);
        aToken.decreaseAllowance(e, a1, u1);
    } else if (f.selector == sig:increaseAllowance(address,uint256).selector) {
        address a1;
        uint256 u1;
        increaseAllowanceCVL(aToken, e.msg.sender, a1, u1);
        aToken.increaseAllowance(e, a1, u1);
    } else if (f.selector == sig:mint(address,address,uint256,uint256).selector) {
        address a1;
        address a2;
        uint256 u1;
        uint256 u2;
        aTokenMintCVL(aToken, a1, a2, u1, u2);
        aToken.mint(e, a1, a2, u1, u2);
    } else if (f.selector == sig:mintToTreasury(uint256,uint256).selector) {
        uint256 u1;
        uint256 u2;
        aTokenMintToTreasuryCVL(aToken, u1, u2);
        aToken.mintToTreasury(e, u1, u2);
    } else if (f.selector == sig:burn(address,address,uint256,uint256).selector) {
        address a1;
        address a2;
        uint256 u1;
        uint256 u2;
        aTokenBurnCVL(aToken, a1, a2, u1, u2);
        aToken.burn(e, a1, a2, u1, u2);
    } else if (f.selector == sig:handleRepayment(address,address,uint256).selector) {
        // it's literally a no-op
        address a1;
        address a2;
        uint256 u1;
        aTokenHandleRepaymentCVL(aToken, a1, a2, u1);
        aToken.handleRepayment(e, a1, a2, u1);
    } else if (f.selector == initialize_method_sig()) {
        // we're running all of our equivalence rules on an 'initialized' state of the AToken
        dont_care();
    } else if (f.selector == sig:rescueTokens(address,address,uint256).selector) {
        // there is no idempotency here (the summary will just simulate whatever is linked-to by rescueTokens,
        // in case the rescued token is an AToken), so rules may fail.
        // We will prove equivalence in an alternative way, see rescueTokenEquivalence
        dont_care();
    } else if (f.selector == sig:setIncentivesController(address).selector) {
        address a1;
        // no CVL implementation, so nop
        aToken.setIncentivesController(e, a1);
    } else {
        not_implemented();
    }
}

rule rescueTokenEquivalence() {
    env e;
    address a1;
    address a2;
    uint256 u1;
    storage init = lastStorage;
    aTokenRescueTokensCVL(aToken, a1, a2, u1, e);
    utils.nop(); // to properly set lastStorage, which is only updated in solidity calls
    storage afterCVL = lastStorage;
    aToken.rescueTokens(e, a1, a2, u1) at init;
    storage afterSol = lastStorage;
    assert afterCVL == afterSol;
}

hook Sstore _underlyingAsset address newValue {
    aTokenToUnderlying[aToken] = newValue;
}

hook Sstore _treasury address newValue {
    theTreasury = newValue;
}

invariant aTokenUnderlyingMatchesGhost()
    aToken._underlyingAsset == aTokenToUnderlying[aToken]
    filtered { f -> f.contract == currentContract }

invariant aTokenTreasuryMatchesGhost()
    aToken._treasury == theTreasury
    filtered { f -> f.contract == currentContract }

use builtin rule sanity filtered { f -> f.contract == currentContract }

function init_state_invariants() {
    requireInvariant aTokensAreNotUnderlyings();
    requireInvariant aTokenUnderlyingMatchesGhost();
    requireInvariant aTokenTreasuryMatchesGhost();
    require currentATokenHasAnUnderlying(); // see definition for justification
    require tokenToSort[aToken] == AToken_token();
}


use rule balanceOfEquivalence;
use rule scaledBalanceOfEquivalence;
use rule totalSupplyEquivalence;
use rule scaledTotalSupplyEquivalence;
use rule allowanceEquivalence;
use rule listOtherViewFunctions;
use invariant aTokensAreNotUnderlyings;
use rule currentATokenHasAnUnderlyingAfterInitiailization;
use rule aTokenWithoutUnderlyingIsERC20AfterInitialization;

