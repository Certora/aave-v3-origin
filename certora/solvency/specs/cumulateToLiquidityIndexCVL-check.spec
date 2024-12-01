
// aave imports
import "AUX/CVLMocks/aToken.spec";
import "AUX/CVLMocks/AddressProvider.spec";

import "common/optimizations.spec";
import "common/functions.spec";
import "common/validation_functions.spec";


ghost mathint TOT_SUP_ATOKEN;

methods {
  //  function _.rayMul(uint256 a, uint256 b) internal => rayMulCVLPrecise(a, b) expect uint256; // not optimized well by Prover
  //function _.rayDiv(uint256 a, uint256 b) internal => rayDivCVLPrecise(a, b) expect uint256; // seems to be optimized well by Prover
}


/*=====================================================================================
  Rule: check_cumulateToLiquidityIndexCVL
  In the proof of solvency__flashLoanSimple we summarize the function 
  cumulateToLiquidityIndex(...) with its CVL's counterpart: cumulateToLiquidityIndexCVL().
  Here we check that out summarization is indeed correct.

  Status: PASS
  Link: https://prover.certora.com/output/66114/398efa550ab44487bb5c958c588d9de9/?anonymousKey=9dfc18bf71c7a3d4074449a2319c2ebf558e5911
  =====================================================================================*/
rule check_cumulateToLiquidityIndexCVL(env e, address _asset) {
  init_state();

  address _atoken = currentContract._reserves[_asset].aTokenAddress;
  require (_atoken != 0); require (_asset != 0);
  uint256 __scaled = scaledTotalSupplyCVL(_atoken);
  require aTokenToUnderlying[_atoken]==_asset;
  
  // INDEX
  uint256 __liqInd_before = getReserveNormalizedIncome(e, _asset);
  require (__liqInd_before == assert_uint256(currentContract._reserves[_asset].liquidityIndex));
  require 10^27 <= __liqInd_before; // && __liqInd_before <= 100*10^27;
  
  
  mathint __totSUP_aToken; __totSUP_aToken = to_mathint(aTokenTotalSupplyCVL(_atoken, e));
  TOT_SUP_ATOKEN = __totSUP_aToken;

  require __totSUP_aToken <= 10^27;

  // THE FUNCTION CALL
  uint256 totalLiquidity; uint256 __amount;
  require __totSUP_aToken <= to_mathint(totalLiquidity) && totalLiquidity <= 10^27;
  require to_mathint(__amount) <= __totSUP_aToken;
  uint256 __new_index = cumulateToLiquidityIndex(e,_asset, totalLiquidity, __amount); // *******

  mathint __totSUP_aToken__; __totSUP_aToken__ = to_mathint(aTokenTotalSupplyCVL(_atoken, e));

  assert to_mathint(rayMulCVLPrecise(__new_index, __scaled)) <=
    TOT_SUP_ATOKEN + __amount + 2*__liqInd_before/10^27;
    
}
