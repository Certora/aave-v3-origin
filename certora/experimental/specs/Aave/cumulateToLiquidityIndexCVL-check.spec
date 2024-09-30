import "../ERC20/WETHcvl.spec";
import "../ERC721/erc721.spec";
import "../ERC1967/erc1967.spec";
import "../PriceAggregators/chainlink.spec";
import "../PriceAggregators/tellor.spec";

// aave imports
import "./aToken.spec";
import "./AddressProvider.spec";
import "./PriceOracleSentinel.spec";
import "./PriceOracle.spec";
import "./ACLManager.spec";
import "./FlashLoanReceiver.spec";

// standard
import "../problems.spec";
import "../unresolved.spec";
import "../optimizations.spec";

import "../generic.spec"; // pick additional rules from here


function init_state() {
  // based on aTokensAreNotUnderlyings
  require forall address a. 
    a == 0 // nothing-token
    || aTokenToUnderlying[a] == 0 // underlying
    || aTokenToUnderlying[aTokenToUnderlying[a]] == 0 // aTokens map to underlyings which map to 0
    ;
  // aTokens have the AToken sort, VariableDebtTokens have the VariableDebt sort, etc...
  require forall address a. tokenToSort[currentContract._reserves[a].aTokenAddress] == AToken_token();
  require forall address a. tokenToSort[currentContract._reserves[a].variableDebtTokenAddress] == VariableDebtToken_token();
  require forall address a. tokenToSort[currentContract._reserves[a].stableDebtTokenAddress] == StableDebtToken_token();
}





ghost mathint TOT_SUP_ATOKEN;


/*
function cumulateToLiquidityIndexCVL(env e, uint256 totalLiq, uint256 amount) returns uint256 {
  uint256 __liqInd_before = getReserveNormalizedIncome(e, ASSET);
  assert (__liqInd_before == assert_uint256(currentContract._reserves[ASSET].liquidityIndex));

  uint256 scaled = scaledTotalSupplyCVL(ATOKEN);
    
  uint256 new_index;
  require to_mathint(rayMulCVLPrecise(new_index, scaled)) == TOT_SUP_ATOKEN + amount;
  
  return new_index;
}
*/


rule check_cumulateToLiquidityIndexCVL(env e, address _asset) {
  init_state();

  address _atoken = currentContract._reserves[_asset].aTokenAddress;
  require (_atoken != 0); require (_asset != 0);
  uint256 __scaled = scaledTotalSupplyCVL(_atoken);
  require aTokenToUnderlying[_atoken]==_asset;
  
  // INDEX
  uint256 __liqInd_before = getReserveNormalizedIncome(e, _asset);
  require (__liqInd_before == assert_uint256(currentContract._reserves[_asset].liquidityIndex));
  require 10^27 <= __liqInd_before;
  
  mathint __totSUP_aToken; __totSUP_aToken = to_mathint(aTokenTotalSupplyCVL(_atoken, e));
  TOT_SUP_ATOKEN = __totSUP_aToken;

  // THE FUNCTION CALL
  uint256 totalLiquidity; uint256 __amount;
  require __amount == 0;
  uint256 __new_index = cumulateToLiquidityIndex(e,_asset, totalLiquidity, __amount);

  mathint __totSUP_aToken__; __totSUP_aToken__ = to_mathint(aTokenTotalSupplyCVL(_atoken, e));

  assert to_mathint(rayMulCVLPrecise(__new_index, __scaled)) == TOT_SUP_ATOKEN + __amount;
}
