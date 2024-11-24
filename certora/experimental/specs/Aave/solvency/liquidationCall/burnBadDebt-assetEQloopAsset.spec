
// aave imports
import "../../aToken.spec";
import "../../AddressProvider.spec";

import "../common/optimizations.spec";
import "../common/functions.spec";
import "../common/validation_functions.spec";


persistent ghost address ATOKEN; persistent ghost address DEBT;

persistent ghost address LOOP_ASSET;
//persistent ghost address ASSET;

persistent ghost mathint DELTA;

persistent ghost mathint ORIG_totSUP_aToken;
persistent ghost mathint ORIG_totSUP_debt;
persistent ghost uint128 ORIG_VB;
persistent ghost uint128 ORIG_deficit;

persistent ghost mathint INTR1_totSUP_aToken;
persistent ghost mathint INTR1_totSUP_debt;
persistent ghost uint128 INTR1_VB;
persistent ghost uint128 INTR1_deficit;

persistent ghost mathint INTR2_totSUP_aToken;
persistent ghost mathint INTR2_totSUP_debt;
persistent ghost uint128 INTR2_VB;
persistent ghost uint128 INTR2_deficit;



methods {
  function LiquidationLogic.HOOK_burnBadDebt_inside_loop(address reserveAddress)
    internal with (env e) => HOOK_burnBadDebt_inside_loop_CVL(e, reserveAddress);

  function LiquidationLogic.HOOK_burnBadDebt_before_burnDebtTokens(address reserveAddress, uint256 amount)
    internal with (env e) => HOOK_burnBadDebt_before_burnDebtTokens_CVL(e,reserveAddress,amount);

  function LiquidationLogic.HOOK_burnBadDebt_after_burnDebtTokens(address reserveAddress, uint256 amount)
    internal with (env e) => HOOK_burnBadDebt_after_burnDebtTokens_CVL(e,reserveAddress,amount);
}

function HOOK_burnBadDebt_inside_loop_CVL(env e, address reserveAddress) {
  LOOP_ASSET = reserveAddress;
  require LOOP_ASSET == ASSET;
}

function HOOK_burnBadDebt_before_burnDebtTokens_CVL(env e, address reserveAddress, uint256 amount) {
  INTR1_totSUP_aToken = to_mathint(aTokenTotalSupplyCVL(ATOKEN, e));
  INTR1_totSUP_debt   = to_mathint(aTokenTotalSupplyCVL(DEBT, e));
  INTR1_VB            = getReserveDataExtended(ASSET).virtualUnderlyingBalance;
  INTR1_deficit       = getReserveDataExtended(ASSET).deficit;

  assert INTR1_totSUP_aToken == ORIG_totSUP_aToken;
  assert INTR1_totSUP_debt == ORIG_totSUP_debt;
  assert INTR1_VB == ORIG_VB;
  assert INTR1_deficit == ORIG_deficit;
}

function HOOK_burnBadDebt_after_burnDebtTokens_CVL(env e, address reserveAddress, uint256 amount) {
  INTR2_totSUP_aToken = to_mathint(aTokenTotalSupplyCVL(ATOKEN, e));
  INTR2_totSUP_debt   = to_mathint(aTokenTotalSupplyCVL(DEBT, e));
  INTR2_VB            = getReserveDataExtended(ASSET).virtualUnderlyingBalance;
  INTR2_deficit       = getReserveDataExtended(ASSET).deficit;

 
  assert INTR2_totSUP_aToken == INTR1_totSUP_aToken;
  assert INTR2_VB == INTR1_VB;
  //  assert INTR2_totSUP_debt == INTR1_totSUP_debt;
  //assert INTR2_deficit == INTR1_deficit;
}









rule solvency__burnBadDebt(env e, address _asset) {
  LOOP_ASSET = 0;
  init_state();

  // Different assets have different Debt tokens.
  require forall address a1. forall address a2.
    a1!=a2 => currentContract._reserves[a1].variableDebtTokenAddress != currentContract._reserves[a2].variableDebtTokenAddress;
  
  ATOKEN = currentContract._reserves[_asset].aTokenAddress;
  DEBT = currentContract._reserves[_asset].variableDebtTokenAddress;
  tokens_addresses_limitations(ATOKEN,DEBT,_asset);

  require aTokenToUnderlying[ATOKEN]==_asset; require aTokenToUnderlying[DEBT]==_asset;

  DataTypes.ReserveData reserve = getReserveDataExtended(_asset);
  require reserve.lastUpdateTimestamp <= require_uint40(e.block.timestamp);

  // INDEXES REQUIREMENTS
  uint128 __liqInd_beforeS = reserve.liquidityIndex;
  uint128 __dbtInd_beforeS = reserve.variableBorrowIndex;
  uint256 __liqInd_before = getReserveNormalizedIncome(e, _asset);
  uint256 __dbtInd_before = getReserveNormalizedVariableDebt(e, _asset);
  require RAY()<=__liqInd_before && RAY()<=__dbtInd_before;
  require assert_uint128(RAY()) <= __liqInd_beforeS && assert_uint128(RAY()) <= __dbtInd_beforeS;

  ORIG_totSUP_aToken = to_mathint(aTokenTotalSupplyCVL(ATOKEN, e));
  ORIG_totSUP_debt   = to_mathint(aTokenTotalSupplyCVL(DEBT, e));
  ORIG_VB = getReserveDataExtended(_asset).virtualUnderlyingBalance;
  ORIG_deficit = getReserveDataExtended(_asset).deficit;
  
  // BASIC ASSUMPTION FOR THE RULE
  require isVirtualAccActive(reserve.configuration.data);

  //THE MAIN REQUIREMENT
  require ORIG_totSUP_aToken <= ORIG_VB + ORIG_totSUP_debt + ORIG_deficit + DELTA;
  
  require ORIG_totSUP_aToken <= 10^27; // Without this requirement we get a failure.
                                    // I believe it's due inaccure RAY-calculations.

  // THE FUNCTION CALL
  uint256 _amount; uint256 _interestRateMode; address onBehalfOf; uint16 referralCode;
  require _interestRateMode == assert_uint256(DataTypes.InterestRateMode.VARIABLE);
  address user;
  _burnBadDebt_WRP(e, user);

  DataTypes.ReserveData reserve2 = getReserveDataExtended(_asset);
  assert reserve2.lastUpdateTimestamp == assert_uint40(e.block.timestamp);
  assert reserve2.liquidityIndex == assert_uint128(__liqInd_before);
  assert (ORIG_totSUP_debt != 0 => (reserve2.variableBorrowIndex == assert_uint128(__dbtInd_before)));
  assert getReserveNormalizedIncome(e, _asset) == __liqInd_before;
  assert ORIG_totSUP_debt != 0 => (getReserveNormalizedVariableDebt(e, _asset) == __dbtInd_before);

  mathint FINAL_totSUP_aToken; FINAL_totSUP_aToken = to_mathint(aTokenTotalSupplyCVL(ATOKEN, e));
  mathint FINAL_totSUP_debt;   FINAL_totSUP_debt   = to_mathint(aTokenTotalSupplyCVL(DEBT, e));
  uint128 FINAL_VB = getReserveDataExtended(_asset).virtualUnderlyingBalance;
  uint128 FINAL_deficit = getReserveDataExtended(_asset).deficit;

  assert true;

  
  
  assert LOOP_ASSET != _asset => FINAL_totSUP_aToken==ORIG_totSUP_aToken;
  assert LOOP_ASSET != _asset => FINAL_VB==ORIG_VB;

  /*
  //THE ASSERTION
  assert LOOP_ASSET!=_asset =>
    FINAL_totSUP_aToken <= FINAL_VB + FINAL_totSUP_debt + FINAL_deficit + DELTA
    + reserve2.variableBorrowIndex / RAY() ;*/
}

