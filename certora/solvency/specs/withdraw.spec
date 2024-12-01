
// aave imports
import "AUX/CVLMocks/aToken.spec";
import "AUX/CVLMocks/AddressProvider.spec";

import "common/optimizations.spec";
import "common/functions.spec";
import "common/validation_functions.spec";


/*================================================================================================
  See the README.txt file in the solvency/ directory
  ================================================================================================*/



/*=====================================================================================
  Rule: solvency__withdraw

  Status: PASS
  Link: https://prover.certora.com/output/66114/f78383017cfa4b7ead6530b0b6e3a87b/?anonymousKey=58440ef19dd97ec9a5d7ba978481a77673e3f133
  =====================================================================================*/
rule solvency__withdraw(env e, address _asset) {
  init_state();

  address _atoken = currentContract._reserves[_asset].aTokenAddress;
  address _debt = currentContract._reserves[_asset].variableDebtTokenAddress;
  tokens_addresses_limitations(_atoken,_debt,_asset);

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
  mathint __totSUP_debt;   __totSUP_debt   = to_mathint(aTokenTotalSupplyCVL(_debt, e));
  uint128 __virtual_bal = getReserveDataExtended(_asset).virtualUnderlyingBalance;

  // BASIC ASSUMPTION FOR THE RULE
  require isVirtualAccActive(reserve.configuration.data);

  // THE MAIN REQUIREMENT
  uint256 CONST;
  require to_mathint(__totSUP_aToken) <= __virtual_bal + __totSUP_debt + CONST;
  
  require __totSUP_aToken <= 10^27; // Without this requirement we get a timeout
                                    // I believe it's due inaccure RAY-calculations.

  // THE FUNCTION CALL
  uint256 _amount; address _to;
  withdraw(e, _asset, _amount, _to);

  DataTypes.ReserveData reserve2 = getReserveDataExtended(_asset);
  assert reserve2.lastUpdateTimestamp == assert_uint40(e.block.timestamp);
  assert reserve2.liquidityIndex == assert_uint128(__liqInd_before);
  assert __totSUP_debt != 0 => (reserve2.variableBorrowIndex == assert_uint128(__dbtInd_before));
  assert getReserveNormalizedIncome(e, _asset) == __liqInd_before;
  assert __totSUP_debt != 0 => (getReserveNormalizedVariableDebt(e, _asset) == __dbtInd_before);
  
  mathint __totSUP_aToken__; __totSUP_aToken__ = to_mathint(aTokenTotalSupplyCVL(_atoken, e));
  mathint __totSUP_debt__;   __totSUP_debt__   = to_mathint(aTokenTotalSupplyCVL(_debt, e));
  uint128 __virtual_bal__ = getReserveDataExtended(_asset).virtualUnderlyingBalance;
  
  //THE ASSERTION
  assert __totSUP_aToken__ <= __virtual_bal__ + __totSUP_debt__ + CONST
         + reserve2.liquidityIndex / RAY();
}

