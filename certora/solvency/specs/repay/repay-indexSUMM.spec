
// aave imports
import "../AUX/CVLMocks/aToken.spec";
import "../AUX/CVLMocks/AddressProvider.spec";

import "../common/optimizations.spec";
import "../common/functions.spec";
import "../common/validation_functions.spec";


/*================================================================================================
  See the README.txt file in the solvency/ directory.

  For the case of the repay functions getNormalizedIncome(...), getNormalizedDebt(...) to return 
  specific values (see below in the method block). We also assume that after the repay function
  is finished, that values will be the same as the values in the storage:
  reserve-of-the-asset.liquidityIndex, and reserve-of-the-asset.variableBorrowIndex.
  (This indeed holds under the assumption that the scaled-total-supply of the variable-debt isn't 0.)

  We prove that it is indeed the case, and we prove it in the file repay-NONindexSUMM.spec (in this
  directory.) We also take care there of the non interesting case where scaled-total-supply of the 
  variable-debt == 0.
  ================================================================================================*/

methods {
  function ValidationLogic.validateRepay(
                                         DataTypes.ReserveCache memory reserveCache,
                                         uint256 amountSent,
                                         DataTypes.InterestRateMode interestRateMode,
                                         address onBehalfOf,
                                         uint256 debt
  ) internal => NONDET;

  function ReserveLogic.getNormalizedIncome(DataTypes.ReserveData storage reserve)
    internal returns (uint256) => LIQUIDITY_INDEX;

  function ReserveLogic.getNormalizedDebt(DataTypes.ReserveData storage reserve)
    internal returns (uint256) => DEBT_INDEX;
}

ghost uint256 LIQUIDITY_INDEX {axiom LIQUIDITY_INDEX >= 10^27;}
ghost uint256 DEBT_INDEX {axiom DEBT_INDEX >= 10^27;}


/*=====================================================================================
  Rule: solvency__repay
  Status: PASS
  Link: https://prover.certora.com/output/66114/c3bf7d127763413a885fcae19671d662/?anonymousKey=f3f236570d484eeb903cab1cd345d20beb5f664b
  =====================================================================================*/
rule solvency__repay(env e, address _asset) {
  init_state();

  address _atoken = currentContract._reserves[_asset].aTokenAddress;
  address _debt = currentContract._reserves[_asset].variableDebtTokenAddress;
  tokens_addresses_limitations(_atoken,_debt,_asset);

  require aTokenToUnderlying[_atoken]==_asset; require aTokenToUnderlying[_debt]==_asset;

  DataTypes.ReserveData reserve = getReserveDataExtended(_asset);
  require reserve.lastUpdateTimestamp <= require_uint40(e.block.timestamp);
  
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
  require exists_debt;

  // THE FUNCTION CALL
  uint256 _amount; uint256 interestRateMode; address onBehalfOf; uint16 referralCode;
  require interestRateMode == assert_uint256(DataTypes.InterestRateMode.VARIABLE);
  repay(e, _asset, _amount, interestRateMode, onBehalfOf);

  
  DataTypes.ReserveData reserve2 = getReserveDataExtended(_asset);
  assert reserve2.lastUpdateTimestamp == assert_uint40(e.block.timestamp);
  require assert_uint256(reserve2.liquidityIndex) == LIQUIDITY_INDEX;
  require assert_uint256(reserve2.variableBorrowIndex) == DEBT_INDEX;
  
  mathint __totSUP_aToken__; __totSUP_aToken__ = to_mathint(aTokenTotalSupplyCVL(_atoken, e));
  mathint __totSUP_debt__;   __totSUP_debt__   = to_mathint(aTokenTotalSupplyCVL(_debt, e));
  uint128 __virtual_bal__ = getReserveDataExtended(_asset).virtualUnderlyingBalance;
  
  //THE ASSERTION
  assert to_mathint(__totSUP_aToken__) <= __virtual_bal__ + __totSUP_debt__ + CONST
    + reserve2.variableBorrowIndex / RAY() ;
}

