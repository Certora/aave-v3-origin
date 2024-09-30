
// aave imports
import "../../aToken.spec";
import "../../AddressProvider.spec";

import "../common/optimizations.spec";
import "../common/functions.spec";
import "../common/validation_functions.spec";


/*================================================================================================
  See the top comment at the file repay-indexSUMM.spec (this directory).
  ================================================================================================*/


/*=====================================================================================
  Rule: same_indexes__repay
  
  The rule is the following lemma (assumed in the file repay-indexSUMM.spec.
   
  a: The return value of getNormalizedIncome(...) is the same before and after the function call
  and:
  b: If the scaled-total-supply of the variable-debt isn't 0, then the return value of getNormalizedDebt(...)
  is the same before and after the function call.
  Note that getNormalizedIncome(...) return the liquidity index, while getNormalizedDebt(...) returns
  the variable-debt index.

  Status: PASS
  Link: https://prover.certora.com/output/66114/17b4d0b1734948029433e1ab174ec431/?anonymousKey=35f254e9d99941b9760eda33d00434141edba7e2

  =====================================================================================*/
rule same_indexes__repay(env e, address _asset) {
  init_state();

  address _atoken = currentContract._reserves[_asset].aTokenAddress;
  address _debt = currentContract._reserves[_asset].variableDebtTokenAddress;
  tokens_addresses_limitations(_atoken,_debt,_asset);

  require aTokenToUnderlying[_atoken]==_asset; require aTokenToUnderlying[_debt]==_asset;

  DataTypes.ReserveData reserve = getReserveDataExtended(_asset);
  require reserve.lastUpdateTimestamp <= require_uint40(e.block.timestamp);

  // INDEXES REQUIREMENTS
  uint256 __liqInd_before = getNormalizedIncome(e, _asset);
  uint256 __dbtInd_before = getNormalizedDebt(e, _asset);
  uint128 __liqInd_beforeS = reserve.liquidityIndex;
  uint128 __dbtInd_beforeS = reserve.variableBorrowIndex;
  require RAY()<=__liqInd_before && RAY()<=__dbtInd_before;
  require assert_uint128(RAY()) <= __liqInd_beforeS && assert_uint128(RAY()) <= __dbtInd_beforeS;
  

  // BASIC ASSUMPTION FOR THE RULE
  require isVirtualAccActive(reserve.configuration.data);

  bool exists_debt = scaledTotalSupplyCVL(_debt)!=0;
  require exists_debt;

  // THE FUNCTION CALL
  uint256 _amount; uint256 interestRateMode; address onBehalfOf; uint16 referralCode;
  require interestRateMode == assert_uint256(DataTypes.InterestRateMode.VARIABLE);
  repay(e, _asset, _amount, interestRateMode, onBehalfOf);

  DataTypes.ReserveData reserve2 = getReserveDataExtended(_asset);
  uint128 __liqInd_afterS = reserve2.liquidityIndex;
  uint128 __dbtInd_afterS = reserve2.variableBorrowIndex;
  uint256 __liqInd_after = getNormalizedIncome(e, _asset);
  uint256 __dbtInd_after = getNormalizedDebt(e, _asset);

  assert reserve2.lastUpdateTimestamp == assert_uint40(e.block.timestamp);

  assert __liqInd_after  == __liqInd_before;
  assert assert_uint256(__liqInd_afterS) == __liqInd_after;

  assert __dbtInd_after  == __dbtInd_before;
  assert assert_uint256(__dbtInd_afterS) == __dbtInd_after;
}






/*=====================================================================================
  Rule: solvency__repay_totDbt_EQ_0
  Details: We prove that if scaled-total-supply of the variable-debt is 0, then repay reverts.
  Status: PASS
  Link: https://prover.certora.com/output/66114/17b4d0b1734948029433e1ab174ec431/?anonymousKey=35f254e9d99941b9760eda33d00434141edba7e2
  =====================================================================================*/
rule solvency__repay_totDbt_EQ_0(env e, address _asset) {
  init_state();

  address _atoken = currentContract._reserves[_asset].aTokenAddress;
  address _debt = currentContract._reserves[_asset].variableDebtTokenAddress;
  tokens_addresses_limitations(_atoken,_debt,_asset);

  require aTokenToUnderlying[_atoken]==_asset; require aTokenToUnderlying[_debt]==_asset;
  require forall address a. balanceByToken[_debt][a] <= totalSupplyByToken[_debt];

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
  require interestRateMode == assert_uint256(DataTypes.InterestRateMode.VARIABLE);
  repay@withrevert(e, _asset, _amount, interestRateMode, onBehalfOf);
  assert lastReverted;
}


