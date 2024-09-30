
// aave imports
import "../aToken.spec";
import "../AddressProvider.spec";
import "../FlashLoanReceiver.spec";

import "common/optimizations.spec";
import "common/functions.spec";
import "common/validation_functions.spec";

/*================================================================================================
  See the README.txt file in the solvency/ directory.

  Note that we rely on the summarization of cumulateToLiquidityIndex, that states that the 
  liquidity-index isn't increased too much.

  We prove that out summarization is indeed sound in the file cumulateToLiquidityIndexCVL-check.spec.
  ================================================================================================*/

methods {
  function ReserveLogic.cumulateToLiquidityIndex(DataTypes.ReserveData storage reserve,
                                                 uint256 totalLiquidity,
                                                 uint256 amount
                                                ) internal returns uint256 with (env e)
    => cumulateToLiquidityIndexCVL(e, totalLiquidity, amount);

  function ValidationLogic.validateFlashloanSimple(
                                                   DataTypes.ReserveData storage reserve,
                                                   uint256 amount
  ) internal => validateFlashloanSimpleCVL(amount);
}

ghost uint256 AMOUNT;
ghost address ATOKEN;
ghost uint128 VB;
ghost uint256 LIQUIDITY_IND_BEFORE;
ghost mathint TOT_SUP_ATOKEN;
ghost mathint TOT_SUP_DEBT;
ghost uint256 DELTA;


function cumulateToLiquidityIndexCVL(env e, uint256 totalLiq, uint256 amount) returns uint256 {
  uint256 __liqInd_before = getReserveNormalizedIncome(e, ASSET);
  assert (__liqInd_before == assert_uint256(currentContract._reserves[ASSET].liquidityIndex));
  assert to_mathint(amount) <= TOT_SUP_ATOKEN;
  assert TOT_SUP_ATOKEN <= to_mathint(totalLiq);

  uint256 scaled = scaledTotalSupplyCVL(ATOKEN);
    
  
  uint256 new_index;
  require to_mathint(rayMulCVLPrecise(new_index, scaled)) <= TOT_SUP_ATOKEN + amount + 2*__liqInd_before/10^27;

  havoc currentContract._reserves[ASSET].liquidityIndex;
  require currentContract._reserves[ASSET].liquidityIndex==require_uint128(new_index);
  
  return new_index;
}

function validateFlashloanSimpleCVL(uint256 amount) {
  require to_mathint(amount) <= TOT_SUP_ATOKEN;
}


/*=====================================================================================
  Rule: solvency__flashLoanSimple

  Status: PASS
  Link: https://prover.certora.com/output/66114/0245f79ede1044c787a1c6b834495d65/?anonymousKey=ce44cd008eb5a1e797acb2e2d9fb93f89485d2bb
  =====================================================================================*/
rule solvency__flashLoanSimple(env e, address _asset) {
  init_state();

  require FLASHLOAN_PREMIUM_TOTAL(e) <= 10000;
  require FLASHLOAN_PREMIUM_TO_PROTOCOL(e) <= 10000;

  address _atoken = currentContract._reserves[_asset].aTokenAddress; ATOKEN = _atoken;
  address _debt = currentContract._reserves[_asset].variableDebtTokenAddress;
  tokens_addresses_limitations(_atoken,_debt,_asset);

  require aTokenToUnderlying[_atoken]==_asset; require aTokenToUnderlying[_debt]==_asset;
  require forall address a. balanceByToken[_atoken][a] <= totalSupplyByToken[_atoken];
  
  DataTypes.ReserveData reserve = getReserveDataExtended(_asset);
  require reserve.lastUpdateTimestamp <= require_uint40(e.block.timestamp);

  // INDEXES REQUIREMENTS
  uint256 __liqInd_before = getReserveNormalizedIncome(e, _asset); LIQUIDITY_IND_BEFORE = __liqInd_before;
  uint256 __dbtInd_before = getReserveNormalizedVariableDebt(e, _asset);
  require __liqInd_before >= RAY() && __dbtInd_before >= RAY();

  mathint __totSUP_aToken; __totSUP_aToken = to_mathint(aTokenTotalSupplyCVL(_atoken, e));
  TOT_SUP_ATOKEN = __totSUP_aToken;
  mathint __totSUP_debt;  __totSUP_debt = to_mathint(aTokenTotalSupplyCVL(_debt, e));
  TOT_SUP_DEBT = __totSUP_debt;
  uint128 __virtual_bal = getReserveDataExtended(_asset).virtualUnderlyingBalance;

  // BASIC ASSUMPTION FOR THE RULE
  require isVirtualAccActive(reserve.configuration.data);

  // THE MAIN REQUIREMENT
  require to_mathint(__totSUP_aToken) <= to_mathint(__virtual_bal) + __totSUP_debt + DELTA;

  require __totSUP_aToken <= 10^27; // Without this requirement we get a timeout

  // THE FUNCTION CALL
  address receiverAddress; uint256 _amount; bytes params; uint16 referralCode; 
  AMOUNT = _amount;
  VB = __virtual_bal;
  flashLoanSimple(e, receiverAddress, _asset, _amount, params, referralCode);

  DataTypes.ReserveData reserve2 = getReserveDataExtended(_asset);
  
  assert reserve2.lastUpdateTimestamp == assert_uint40(e.block.timestamp);
  assert __totSUP_debt != 0 => (reserve2.variableBorrowIndex == require_uint128(__dbtInd_before));
  assert __totSUP_debt != 0 => (getReserveNormalizedVariableDebt(e, _asset) == __dbtInd_before);
  
  uint256 __dbtInd_after = getReserveNormalizedVariableDebt(e, _asset);

  mathint __totSUP_aToken__; mathint __totSUP_debt__;
  __totSUP_aToken__ = to_mathint(aTokenTotalSupplyCVL(_atoken, e));
  __totSUP_debt__ = to_mathint(aTokenTotalSupplyCVL(_debt, e));
  uint128 __virtual_bal__ = getReserveDataExtended(_asset).virtualUnderlyingBalance;
  
  //THE ASSERTION
  assert to_mathint(__totSUP_aToken__) <= to_mathint(__virtual_bal__) + __totSUP_debt__ + DELTA
    + 2*__liqInd_before / RAY();
}

