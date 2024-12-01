
// aave imports
import "../AUX/CVLMocks/aToken.spec";
import "../AUX/CVLMocks/AddressProvider.spec";

import "../common/optimizations.spec";
import "../common/functions.spec";
import "../common/validation_functions.spec";






/*=====================================================================================
  Rule: solvency__repayWithATokens_totDbt_EQ_0
  We prove that if scaled-total-supply of the variable-debt is 0, then repayWithATokens reverts.

  Status: PASS
  Link: https://prover.certora.com/output/66114/384d747b8ad540bca06387fe00d0a7bf/?anonymousKey=c15ce8ec3bd0ade0b0fa77042d725c28174e137d
  =====================================================================================*/
rule solvency__repayWithATokens_totDbt_EQ_0(env e, address _asset) {
  init_state();

  address _atoken = currentContract._reserves[_asset].aTokenAddress;
  address _debt = currentContract._reserves[_asset].variableDebtTokenAddress;
  tokens_addresses_limitations(_atoken,_debt,_asset);

  require forall address a. balanceByToken[_debt][a] <= totalSupplyByToken[_debt];
  require forall address a. balanceByToken[_atoken][a] <= totalSupplyByToken[_atoken];
  require aTokenToUnderlying[_atoken]==_asset; require aTokenToUnderlying[_debt]==_asset;

  DataTypes.ReserveData reserve = getReserveDataExtended(_asset);
  require reserve.lastUpdateTimestamp <= require_uint40(e.block.timestamp);

  // INDEXES REQUIREMENTS
  uint256 __liqInd_before = getReserveNormalizedIncome(e, _asset);
  uint256 __dbtInd_before = getReserveNormalizedVariableDebt(e, _asset);
  uint128 __liqInd_beforeS = reserve.liquidityIndex;
  uint128 __dbtInd_beforeS = reserve.variableBorrowIndex;
  require RAY()<=__liqInd_before && RAY()<=__dbtInd_before;
  require assert_uint128(RAY()) <= __liqInd_beforeS && assert_uint128(RAY()) <= __dbtInd_beforeS;
  
  mathint __totSUP_aToken; __totSUP_aToken = to_mathint(aTokenTotalSupplyCVL(_atoken, e));
  mathint __totSUP_debt;  __totSUP_debt = to_mathint(aTokenTotalSupplyCVL(_debt, e));
  uint128 __virtual_bal = getReserveDataExtended(_asset).virtualUnderlyingBalance;

  // BASIC ASSUMPTION FOR THE RULE
  require isVirtualAccActive(reserve.configuration.data);

  // THE MAIN REQUIREMENT
  uint256 CONST;
  require to_mathint(__totSUP_aToken) <= __virtual_bal + __totSUP_debt + CONST;

  require __totSUP_aToken <= 10^27; // Without this requirement we get a timeout
                                    // I believe it's due inaccure RAY-calculations.

  bool exists_debt = scaledTotalSupplyCVL(_debt)!=0;
  require !exists_debt;

  
  // THE FUNCTION CALL
  uint256 _amount; uint256 interestRateMode; address onBehalfOf; uint16 referralCode;
  assert balanceByToken[_debt][onBehalfOf]==0; // This should help the prover
  require interestRateMode == assert_uint256(DataTypes.InterestRateMode.VARIABLE);
  repayWithATokens@withrevert(e, _asset, _amount, interestRateMode);
  assert lastReverted;
}


