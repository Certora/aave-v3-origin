
// aave imports
import "../../aToken.spec";
import "../../AddressProvider.spec";

import "../common/optimizations.spec";
import "../common/functions.spec";
import "../common/validation_functions.spec";



/*================================================================================================
  See the README.txt file in the solvency/ directory
  ================================================================================================*/

persistent ghost bool INSIDE_liquidationCall;
persistent ghost bool INSIDE_burnBadDebt;

persistent ghost address _DBT_asset; persistent ghost address _DBT_atoken; persistent ghost address _DBT_debt;

persistent ghost address _COL_asset; persistent ghost address _COL_atoken; persistent ghost address _COL_debt;
persistent ghost uint256 _COL_liqIND {axiom _COL_liqIND >= 10^27;}
persistent ghost uint256 _COL_dbtIND {axiom _COL_dbtIND >= 10^27;}


persistent ghost address USER;
persistent ghost mathint DELTA;
persistent ghost mathint ORIG_totSUP_aToken;
persistent ghost mathint ORIG_totSUP_debt;
persistent ghost uint128 ORIG_VB;
persistent ghost uint128 ORIG_deficit;

persistent ghost mathint INTR_totSUP_aToken;
persistent ghost mathint INTR_totSUP_debt;
persistent ghost uint128 INTR_VB;
persistent ghost uint128 INTR_deficit;

persistent ghost mathint INTR2_totSUP_aToken;
persistent ghost mathint INTR2_totSUP_debt;
persistent ghost uint128 INTR2_VB;
persistent ghost uint128 INTR2_deficit;

persistent ghost mathint INTR3_totSUP_aToken;
persistent ghost mathint INTR3_totSUP_debt;
persistent ghost uint128 INTR3_VB;
persistent ghost uint128 INTR3_deficit;

persistent ghost mathint INTR4_totSUP_aToken;
persistent ghost mathint INTR4_totSUP_debt;
persistent ghost uint128 INTR4_VB;
persistent ghost uint128 INTR4_deficit;

persistent ghost mathint FINAL_totSUP_aToken;
persistent ghost mathint FINAL_totSUP_debt;
persistent ghost uint128 FINAL_VB;
persistent ghost uint128 FINAL_deficit;


methods {
  //function LiquidationLogic.DUMMY_vars_get_val1()
  //  internal returns (uint256,uint256,uint256) => NONDET;
  //function LiquidationLogic.DUMMY_vars_get_val2()
  //  internal returns (uint256,uint256,uint256) => NONDET;
  
  //function LiquidationLogic.DUMMY_get_maxLiquidatableDebt()
  //  internal returns (uint256) => NONDET;

  function IsolationModeLogic.updateIsolatedDebtIfIsolated(
    mapping(address => DataTypes.ReserveData) storage reservesData,
    mapping(uint256 => address) storage reservesList,
    DataTypes.UserConfigurationMap storage userConfig,
    DataTypes.ReserveCache memory reserveCache,
    uint256 repayAmount
  ) internal => updateIsolatedDebtIfIsolatedCVL();

  function LiquidationLogic._calculateAvailableCollateralToLiquidate(
    DataTypes.ReserveConfigurationMap memory collateralReserveConfiguration,
    uint256 collateralAssetPrice,
    uint256 collateralAssetUnit,
    uint256 debtAssetPrice,
    uint256 debtAssetUnit,
    uint256 debtToCover,
    uint256 userCollateralBalance,
    uint256 liquidationBonus
  ) internal returns (uint256,uint256,uint256,uint256) =>
    _calculateAvailableCollateralToLiquidateCVL();

  function LiquidationLogic._burnBadDebt(
    mapping(address => DataTypes.ReserveData) storage reservesData,
    mapping(uint256 => address) storage reservesList,
    DataTypes.UserConfigurationMap storage userConfig,
    uint256 reservesCount,
    address user
  ) internal with (env e) => _burnBadDebt_CVL(e);
}

function _burnBadDebt_CVL(env e) {
  INSIDE_liquidationCall = false;

  mathint curr_totSUP_aToken = to_mathint(aTokenTotalSupplyCVL(_COL_atoken, e));
  mathint curr_totSUP_debt   = to_mathint(aTokenTotalSupplyCVL(_COL_debt, e));
  uint128 curr_VB            = getReserveDataExtended(_COL_asset).virtualUnderlyingBalance;
  uint128 curr_deficit       = getReserveDataExtended(_COL_asset).deficit;
  
  if (curr_totSUP_aToken<=curr_VB + curr_totSUP_debt + curr_deficit + DELTA + _COL_liqIND / RAY()) {
    havoc_all(e);
    mathint after_totSUP_aToken = to_mathint(aTokenTotalSupplyCVL(_COL_atoken, e));
    mathint after_totSUP_debt   = to_mathint(aTokenTotalSupplyCVL(_COL_debt, e));
    uint128 after_VB            = getReserveDataExtended(_COL_asset).virtualUnderlyingBalance;
    uint128 after_deficit       = getReserveDataExtended(_COL_asset).deficit;

    require
      after_totSUP_aToken <=
      after_VB + after_totSUP_debt + after_deficit + DELTA +
      _COL_liqIND / RAY() + _COL_dbtIND / RAY()
      ;

    require
      getReserveDataExtended(_COL_asset).variableBorrowIndex == getNormalizedDebt_CVL();

    require
      getReserveDataExtended(_COL_asset).liquidityIndex == _COL_liqIND;
  }
  INSIDE_liquidationCall = true;
}

// This is immediately after the call to updateState for the COL token
function _calculateAvailableCollateralToLiquidateCVL() returns (uint256,uint256,uint256,uint256) {
  uint256 a; uint256 b; uint256 c; uint256 d;
  return (a,b,c,d);
}


// The function updateIsolatedDebtIfIsolated(...) only writes to the field isolationModeTotalDebt.
function updateIsolatedDebtIfIsolatedCVL() {
  address asset;
  havoc currentContract._reserves[asset].isolationModeTotalDebt;
}


/*==============================================================================================
  Summarizations
  ==============================================================================================*/
methods {
  function ReserveLogic.getNormalizedIncome(DataTypes.ReserveData storage reserve)
    internal returns (uint256) => _COL_liqIND;

  function ReserveLogic.getNormalizedDebt(DataTypes.ReserveData storage reserve)
    internal returns (uint256) => getNormalizedDebt_CVL();
}

function getNormalizedDebt_CVL() returns uint256 {
  if (INSIDE_liquidationCall) {
    uint256 any_index;
    return any_index;
  }
  else
    return _COL_liqIND;
}


/*================================================================================================
  Summarizations of HOOKS function 
  ================================================================================================*/
methods {
  function LiquidationLogic.HOOK_liquidation_before_burnCollateralATokens(uint256 actualCollateralToLiquidate)
    internal with (env e) => HOOK_liquidation_before_burnCollateralATokens_CVL(e, actualCollateralToLiquidate);

  function LiquidationLogic.HOOK_liquidation_after_burnCollateralATokens(uint256 actualCollateralToLiquidate)
    internal with (env e) => HOOK_liquidation_after_burnCollateralATokens_CVL(e, actualCollateralToLiquidate);

  function LiquidationLogic.HOOK_burnCollateralATokens_after_updateState()
    internal => HOOK_burnCollateralATokens_after_updateState_CVL();

  function LiquidationLogic.HOOK_liquidation_before_burnBadDebt()
    internal with (env e) => HOOK_liquidation_before_burnBadDebt_CVL(e);

  function LiquidationLogic.HOOK_liquidation_after_burnBadDebt()
    internal with (env e) => HOOK_liquidation_after_burnBadDebt_CVL(e);

}


function HOOK_liquidation_before_burnCollateralATokens_CVL(env e, uint256 actualCollateralToLiquidate) {
  INSIDE_liquidationCall = false;
  
  mathint curr_totSUP_aToken;  curr_totSUP_aToken = to_mathint(aTokenTotalSupplyCVL(_COL_atoken, e));
  mathint curr_totSUP_debt;    curr_totSUP_debt   = to_mathint(aTokenTotalSupplyCVL(_COL_debt, e));
  uint128 curr_VB;             curr_VB            = getReserveDataExtended(_COL_asset).virtualUnderlyingBalance;
  uint128 curr_deficit;        curr_deficit       = getReserveDataExtended(_COL_asset).deficit;
  
  assert ORIG_totSUP_aToken == curr_totSUP_aToken;
  assert ORIG_totSUP_debt   == curr_totSUP_debt;
  assert ORIG_VB == curr_VB;
  assert ORIG_deficit == curr_deficit;

  assert ORIG_totSUP_aToken <= ORIG_VB + ORIG_totSUP_debt + ORIG_deficit + DELTA;

  uint256 scaled = totalSupplyByToken[_COL_atoken]; uint256 IND = _COL_liqIND;
  assert
    to_mathint(rayMulCVLPrecise( require_uint256(scaled - rayDivCVLPrecise(actualCollateralToLiquidate,IND)), IND) )
    <=
    rayMulCVLPrecise(scaled,IND) - actualCollateralToLiquidate + IND/RAY();

  INSIDE_liquidationCall = true;
}

function HOOK_liquidation_after_burnCollateralATokens_CVL(env e, uint256 actualCollateralToLiquidate) {
  INSIDE_liquidationCall = false;
  
  INTR_totSUP_aToken = to_mathint(aTokenTotalSupplyCVL(_COL_atoken, e));
  INTR_totSUP_debt   = to_mathint(aTokenTotalSupplyCVL(_COL_debt, e));
  INTR_VB            = getReserveDataExtended(_COL_asset).virtualUnderlyingBalance;
  INTR_deficit       = getReserveDataExtended(_COL_asset).deficit;
  
  assert INTR_totSUP_debt == ORIG_totSUP_debt;
  assert INTR_deficit == ORIG_deficit;

  assert INTR_VB == ORIG_VB - actualCollateralToLiquidate;
  assert INTR_totSUP_aToken <= ORIG_totSUP_aToken - actualCollateralToLiquidate + _COL_liqIND / RAY() ;

  assert INTR_totSUP_aToken <= INTR_VB + INTR_totSUP_debt + INTR_deficit + DELTA + _COL_liqIND / RAY();

  INSIDE_liquidationCall = true;
}

function HOOK_burnCollateralATokens_after_updateState_CVL() {
  require currentContract._reserves[_COL_asset].liquidityIndex == _COL_liqIND;
  require currentContract._reserves[_COL_asset].variableBorrowIndex == _COL_dbtIND;
}

function HOOK_liquidation_before_burnBadDebt_CVL(env e) {
  INSIDE_liquidationCall = false;
  
  INTR2_totSUP_aToken = to_mathint(aTokenTotalSupplyCVL(_COL_atoken, e));
  INTR2_totSUP_debt   = to_mathint(aTokenTotalSupplyCVL(_COL_debt, e));
  INTR2_VB            = getReserveDataExtended(_COL_asset).virtualUnderlyingBalance;
  INTR2_deficit       = getReserveDataExtended(_COL_asset).deficit;

  assert INTR2_totSUP_aToken <= INTR2_VB + INTR2_totSUP_debt + INTR2_deficit + DELTA + _COL_liqIND / RAY();

  INSIDE_liquidationCall = true;
  INSIDE_burnBadDebt = true;
}

function HOOK_liquidation_after_burnBadDebt_CVL(env e) {
  INSIDE_liquidationCall = false;
  INSIDE_burnBadDebt = false;

  FINAL_totSUP_aToken = to_mathint(aTokenTotalSupplyCVL(_COL_atoken, e));
  FINAL_totSUP_debt   = to_mathint(aTokenTotalSupplyCVL(_COL_debt, e));
  FINAL_VB            = getReserveDataExtended(_COL_asset).virtualUnderlyingBalance;
  FINAL_deficit       = getReserveDataExtended(_COL_asset).deficit;

  assert
    FINAL_totSUP_aToken <= FINAL_VB + FINAL_totSUP_debt + FINAL_deficit + DELTA +
    _COL_liqIND / RAY() + _COL_dbtIND / RAY();

  INSIDE_liquidationCall = true;
}


  





function tokens_addresses_limitations_LQD(address asset, address atoken, address debt,
                                          address asset2, address atoken2, address debt2
                                         ) {
  require asset==100;  require atoken==10;  require debt==11; 
  require asset2==200; require atoken2==20; require debt2==21; 

}


function configuration() {
  init_state();

  _DBT_atoken = currentContract._reserves[_DBT_asset].aTokenAddress;
  _COL_atoken = currentContract._reserves[_COL_asset].aTokenAddress;            
  _DBT_debt = currentContract._reserves[_DBT_asset].variableDebtTokenAddress;
  _COL_debt = currentContract._reserves[_COL_asset].variableDebtTokenAddress;
  tokens_addresses_limitations_LQD(_DBT_asset, _DBT_atoken, _DBT_debt,
                                   _COL_asset, _COL_atoken, _COL_debt);

  require aTokenToUnderlying[_DBT_atoken]==_DBT_asset; require aTokenToUnderlying[_DBT_debt]==_DBT_asset;
  require aTokenToUnderlying[_COL_atoken]==_COL_asset; require aTokenToUnderlying[_COL_debt]==_COL_asset;
}

/*=====================================================================================
  Rule: solvency__liquidationCall
  =====================================================================================*/
rule solvency__liquidationCall_COLasset(env e) {
  INSIDE_liquidationCall = false;
  INSIDE_burnBadDebt = false;
  configuration();

  DataTypes.ReserveData reserve = getReserveDataExtended(_COL_asset);
  require reserve.lastUpdateTimestamp <= require_uint40(e.block.timestamp);
  
  ORIG_totSUP_aToken = to_mathint(aTokenTotalSupplyCVL(_COL_atoken, e));
  ORIG_totSUP_debt = to_mathint(aTokenTotalSupplyCVL(_COL_debt, e));
  ORIG_VB = getReserveDataExtended(_COL_asset).virtualUnderlyingBalance;
  ORIG_deficit = getReserveDataExtended(_COL_asset).deficit;

  // BASIC ASSUMPTION FOR THE RULE
  require isVirtualAccActive(reserve.configuration.data);

  // THE MAIN REQUIREMENT
  require ORIG_totSUP_aToken <= ORIG_VB + ORIG_totSUP_debt + ORIG_deficit + DELTA;

  require ORIG_totSUP_aToken <= 10^27; // Without this requirement we get a timeout
                                       // I believe it's due inaccure RAY-calculations.

  bool exists_debt = scaledTotalSupplyCVL(_COL_debt)!=0;
  require exists_debt;

  // THE FUNCTION CALL
  uint256 _debtToCover; bool _receiveAToken;
  INSIDE_liquidationCall = true;
  liquidationCall(e, _COL_asset, _DBT_asset, USER, _debtToCover, _receiveAToken);
  INSIDE_liquidationCall = false;
  
  DataTypes.ReserveData reserve2 = getReserveDataExtended(_COL_asset);
  
  mathint final_totSUP_aToken = to_mathint(aTokenTotalSupplyCVL(_COL_atoken, e));
  mathint final_totSUP_debt   = to_mathint(aTokenTotalSupplyCVL(_COL_debt, e));
  uint128 final_VB = getReserveDataExtended(_COL_asset).virtualUnderlyingBalance;
  uint128 final_deficit = getReserveDataExtended(_COL_asset).deficit;

  //  assert true;
  /*
  assert FINAL_totSUP_aToken == INTR_totSUP_aToken;
  assert FINAL_totSUP_debt == INTR_totSUP_debt;
  assert FINAL_deficit == INTR_deficit;
  assert FINAL_VB == INTR_VB;*/
  
  //THE ASSERTION
  assert
    final_totSUP_aToken <= final_VB + final_totSUP_debt + final_deficit + DELTA
    + reserve2.variableBorrowIndex / RAY()
    + reserve2.liquidityIndex / RAY()
    ;
}

